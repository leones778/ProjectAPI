from flask import jsonify
from flask_pydantic import validate
from sqlalchemy import select

from app.core.database import session_maker
from app.main import app
from app.models.consumable import (
    ConsumableCategory,
    GETListParams,
    POSTConsumableCategory,
)


@app.post("/categories")
@validate()
def api_add_consumable_category(body: POSTConsumableCategory):
    with session_maker() as db_session:
        category = db_session.scalar(
            select(ConsumableCategory).where(ConsumableCategory.name == body.name)
        )
        if category is not None:
            return jsonify({"error": "Consumable category already exists"}), 400

        category = ConsumableCategory(name=body.name, description=body.description)
        db_session.add(category)
        db_session.commit()

        return jsonify({"category": category.to_dict()}), 201


@app.get("/categories")
@validate()
def api_get_consumable_categories(query: GETListParams):
    with session_maker() as db_session:
        sql_query = select(ConsumableCategory).offset(query.offset)
        if query.limit:
            sql_query = sql_query.limit(query.limit)

        categories = db_session.scalars(sql_query)

        return jsonify({"categories": [category.to_dict() for category in categories]})


@app.get("/categories/<category_id>")
def api_get_consumable_category(category_id: str):
    with session_maker() as db_session:
        category = db_session.scalar(
            select(ConsumableCategory).where(
                ConsumableCategory.category_id == category_id
            )
        )
        if category is None:
            return jsonify({"error": "Consumable category not found"}), 404

        return jsonify({"category": category.to_dict()})


@app.put("/categories/<category_id>")
@validate()
def api_update_consumable_category(category_id: str, body: POSTConsumableCategory):
    with session_maker() as db_session:
        category = db_session.scalar(
            select(ConsumableCategory).where(
                ConsumableCategory.category_id == category_id
            )
        )
        if category is None:
            return jsonify({"error": "Consumable category not found"}), 404

        category.name = body.name
        category.description = body.description

        db_session.commit()

        return jsonify({"category": category.to_dict()})


@app.delete("/categories/<category_id>")
def api_delete_consumable_category(category_id: str):
    with session_maker() as db_session:
        category = db_session.scalar(
            select(ConsumableCategory).where(
                ConsumableCategory.category_id == category_id
            )
        )
        if category is None:
            return jsonify({"error": "Consumable category not found"}), 404

        db_session.delete(category)
        db_session.commit()

        return jsonify({"message": "Consumable category deleted"})
