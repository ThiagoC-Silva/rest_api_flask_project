from flask_smorest import abort, Blueprint
from flask.views import MethodView

from db import db
from models.store import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import StoreSchema

stores_bp = Blueprint("Stores", "__name__", description="Stores operations")

@stores_bp.route("/store/<int:store_id>")
class Store(MethodView):
    @stores_bp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()

        return {"message": "Store deleted."}
    
@stores_bp.route("/store")
class StoreList(MethodView):
    @stores_bp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @stores_bp.arguments(StoreSchema)
    @stores_bp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400,
                  message="A store with that name already exists."  
            )
        except SQLAlchemyError:
            abort(500, 
                  message="An error ocurred while inserting the store."
            )

        return store


