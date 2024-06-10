from flask import jsonify
from flask_pydantic import validate
from sqlalchemy import select

from app.core.database import session_maker
from app.main import app
from app.models.consumable import (
    Consumable,
    ConsumableCategory,
    ConsumableHistory,
    GETListParams,
    POSTConsumable,
    POSTConsumableHistory,
)


@app.post("/categories/<category_id>/consumables")
@validate()
def api_add_consumable(category_id: str, body: POSTConsumable):
    with session_maker() as db_session:
        category = db_session.scalar(
            select(ConsumableCategory).where(
                ConsumableCategory.category_id == category_id
            )
        )
        if category is None:
            return jsonify({"error": "Category does not exist"}), 404

        consumable = db_session.scalar(
            select(Consumable).where(Consumable.name == body.name)
        )
        if consumable is not None:
            return jsonify({"error": "Consumable already exists"}), 400

        consumable = Consumable(
            name=body.name,
            quantity=body.quantity,
            description=body.description,
            category_id=category_id,
        )
        db_session.add(consumable)
        db_session.commit()

        return jsonify({"consumable": consumable.to_dict()}), 201


@app.get("/categories/<category_id>/consumables")
@validate()
def api_get_consumables(category_id: str, query: GETListParams):
    with session_maker() as db_session:
        sql_query = (
            select(Consumable)
            .where(Consumable.category_id == category_id)
            .offset(query.offset)
        )
        if query.limit:
            sql_query = sql_query.limit(query.limit)

        consumables = db_session.scalars(sql_query)

        return jsonify(
            {"consumables": [consumable.to_dict() for consumable in consumables]}
        )


@app.get("/categories/<category_id>/consumables/<consumable_id>")
@validate()
def api_get_consumable(category_id: str, consumable_id: str):
    with session_maker() as db_session:
        consumable = db_session.scalar(
            select(Consumable)
            .where(Consumable.category_id == category_id)
            .where(Consumable.consumable_id == consumable_id)
        )
        if consumable is None:
            return jsonify({"error": "Consumable not found"}), 404

        return jsonify({"consumable": consumable.to_dict()})


@app.put("/categories/<category_id>/consumables/<consumable_id>")
@validate()
def api_update_consumable(category_id: str, consumable_id: str, body: POSTConsumable):
    with session_maker() as db_session:
        consumable = db_session.scalar(
            select(Consumable)
            .where(Consumable.category_id == category_id)
            .where(Consumable.consumable_id == consumable_id)
        )
        if consumable is None:
            return jsonify({"error": "Consumable not found"}), 404

        consumable.name = body.name
        consumable.quantity = body.quantity
        consumable.description = body.description
        db_session.commit()

        return jsonify({"consumable": consumable.to_dict()})


@app.delete("/categories/<category_id>/consumables/<consumable_id>")
@validate()
def api_delete_consumable(category_id: str, consumable_id: str):
    with session_maker() as db_session:
        consumable = db_session.scalar(
            select(Consumable)
            .where(Consumable.category_id == category_id)
            .where(Consumable.consumable_id == consumable_id)
        )
        if consumable is None:
            return jsonify({"error": "Consumable not found"}), 404

        db_session.delete(consumable)
        db_session.commit()

        return jsonify({"message": "Consumable deleted"})


@app.post("/categories/<category_id>/consumables/<consumable_id>/history")
@validate()
def api_add_consumable_history(
    category_id: str, consumable_id: str, body: POSTConsumableHistory
):
    with session_maker() as db_session:
        consumable = db_session.scalar(
            select(Consumable)
            .where(Consumable.category_id == category_id)
            .where(Consumable.consumable_id == consumable_id)
        )
        if consumable is None:
            return jsonify({"error": "Consumable not found"}), 404

        consumable.quantity += body.modified_count

        history = ConsumableHistory(
            modified_count=body.modified_count,
            description=body.description,
            consumable_id=consumable_id,
        )
        db_session.add(history)
        db_session.commit()

        return jsonify({"history": [history.to_dict()]})


@app.get("/categories/<category_id>/consumables/<consumable_id>/history")
@validate()
def api_get_consumable_history(
    category_id: str, consumable_id: str, query: GETListParams
):
    with session_maker() as db_session:
        sql_query = (
            select(ConsumableHistory)
            .join(Consumable, ConsumableHistory.consumable_id == Consumable.consumable_id)
            .where(ConsumableHistory.consumable_id == consumable_id)
            .where(Consumable.category_id == category_id)
            .offset(query.offset)
        )
        if query.limit:
            sql_query = sql_query.limit(query.limit)

        history = db_session.scalars(
            sql_query.order_by(ConsumableHistory.history_id.desc())
        )

        return jsonify({"history": [item.to_dict() for item in history]})


@app.delete(
    "/categories/<category_id>/consumables/<consumable_id>/history/<history_id>"
)
@validate()
def api_delete_consumable_history(
    category_id: str, consumable_id: str, history_id: int
):
    with session_maker() as db_session:
        history = db_session.scalar(
            select(ConsumableHistory)
            .join(Consumable, ConsumableHistory.consumable_id == Consumable.consumable_id)
            .where(ConsumableHistory.consumable_id == consumable_id)
            .where(Consumable.category_id == category_id)
            .where(ConsumableHistory.history_id == history_id)
        )
        if history is None:
            return jsonify({"error": "History item not found"}), 404

        db_session.delete(history)
        db_session.commit()

        return jsonify({"message": "History item deleted"})
