from datetime import datetime

from flask import g, jsonify, make_response, request
from flask_pydantic import validate
from sqlalchemy import delete, select
from sqlalchemy.orm import joinedload

from app.api.auth.helpers import (
    calc_expiration_at,
    calc_refresh_at,
    check_password,
    hash_password,
    set_session_cookie,
)
from app.core.database import session_maker
from app.core.utils import uuidhex
from app.main import app
from app.models.user import LoginSchema, RegisterSchema, Role, User, UserSession


@app.route("/auth/register", methods=["POST"])
@validate()
def api_register(body: RegisterSchema):
    with session_maker() as db_session:
        user = db_session.scalar(select(User).where(User.email == body.email))
        if user is not None:
            return jsonify({"error": "User already exists"}), 400

        user = User(
            user_id=uuidhex(),
            email=body.email,
            first_name=body.first_name,
            last_name=body.last_name,
            middle_name=body.middle_name,
            hashed_password=hash_password(body.password),
            role=Role.WORKER,
        )
        session = UserSession(user_id=user.user_id, expiration_at=calc_expiration_at())

        db_session.add_all([user, session])
        db_session.commit()

    response = make_response(
        jsonify({"message": "User created", "user": user.to_dict()}),
        201,
    )
    set_session_cookie(response, session)
    return response


@app.route("/auth/login", methods=["POST"])
@validate()
def api_login(body: LoginSchema):
    with session_maker() as db_session:
        user = db_session.scalar(select(User).where(User.email == body.email))
        if user is None:
            return jsonify({"error": "AuthEror"}), 401

        if not check_password(body.password, user.hashed_password):
            return jsonify({"error": "AuthEror"}), 401

        db_session.execute(
            delete(UserSession).where(UserSession.user_id == user.user_id)
        )
        db_session.flush()

        session = UserSession(user_id=user.user_id, expiration_at=calc_expiration_at())
        db_session.add(session)
        db_session.commit()

        response = make_response(
            jsonify({"message": "Logged in", "user": user.to_dict()}), 200
        )

        set_session_cookie(response, session)
        return response


@app.route("/auth/logout", methods=["POST"])
def api_logout():
    session_id = request.cookies.get("X-Session-ID")
    if not session_id:
        return jsonify({"error": "AuthError"}), 401

    with session_maker() as db_session:
        db_session.execute(
            delete(UserSession).where(UserSession.session_id == session_id)
        )
        db_session.commit()

    response = make_response(jsonify({"message": "Logged out"}), 200)
    response.delete_cookie("X-Session-ID")

    return response


@app.before_request
def current_user():
    if request.path.startswith("/auth"):
        return None

    session_id = request.cookies.get("X-Session-ID")
    if not session_id:
        return jsonify({"error": "Unauthorized"}), 401

    with session_maker() as db_session:
        session = db_session.scalar(
            select(UserSession)
            .options(joinedload(UserSession.user))
            .where(UserSession.session_id == session_id)
        )
        if session is None or session.user is None:
            return jsonify({"error": "Unauthorized"}), 401

        user = session.user

        if session.expiration_at <= datetime.utcnow():
            db_session.execute(
                delete(UserSession).where(UserSession.session_id == session_id)
            )
            db_session.commit()
            return jsonify({"error": "Unauthorized"}), 401

        if calc_refresh_at(session.created_at) <= datetime.utcnow():
            db_session.execute(
                delete(UserSession).where(UserSession.session_id == session_id)
            )
            db_session.flush()

            session = UserSession(
                user_id=user.user_id, expiration_at=calc_expiration_at()
            )
            db_session.add(session)
            db_session.commit()

            g.user_session = session

        if request.method in ["POST", "PUT", "DELETE"] and user.role != Role.ADMIN:
            return jsonify({"error": "Forbidden"}), 403

        g.user = user


@app.after_request
def add_header(response):
    if session := g.get("user_session"):
        set_session_cookie(response, session)
    return response
