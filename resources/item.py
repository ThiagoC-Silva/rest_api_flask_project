from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from flask_smorest import abort, Blueprint
from flask_jwt_extended import get_jwt, jwt_required

from db import db
from models import ItemModel 
from schemas import ItemSchema, UpdateItemSchema

items_bp = Blueprint("Items", "__name__", description="Items operations")

@items_bp.route("/item/<int:item_id>")
class Item(MethodView):

    @jwt_required()
    @items_bp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    @items_bp.arguments(UpdateItemSchema)
    @items_bp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        item = ItemModel.query.get(item_id)

        if item:
            item.name = item_data["name"]
            item.price = item_data["price"]
        else:
            item = ItemModel(id=item_id, **item_data)

        db.session.add(item)
        db.session.commit()

        return item

    @jwt_required()
    def delete(self, item_id):
        jwt = get_jwt()
        print(jwt)
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")

        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()

        return {"message": "Item deleted."}

@items_bp.route("/item")
class ItemList(MethodView):

    @jwt_required()
    @items_bp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @items_bp.arguments(ItemSchema)
    @items_bp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error ocurred while inserting the item.")
        
        return item
