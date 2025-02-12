from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models.tag import TagModel
from models.item import ItemModel
from models.store import StoreModel
from schemas import TagSchema, ItemTagSchema

tags_bp = Blueprint("Tags", __name__, description="Tags operations")

@tags_bp.route("/tag/<int:tag_id>/")
class Tag(MethodView):

    @tags_bp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        
        return tag
    
    @tags_bp.response(
        202,
        description="Deletes a tag if no item is togged with it",
        example={"message": 'Tag deleted.'}
    )
    @tags_bp.alt_response(404, description="Tag not found")
    @tags_bp.alt_response(
        400, 
        description="Returned if the tag is assigned to one or more items. In this casa, the tag is not deleted."
    )
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        
        abort(
            400, 
            message="Could not delete the tag. Make sure tag is assoscieted with any items, the try again"
        )

@tags_bp.route("/store/<int:store_id>/tag")
class TagsInStores(MethodView):
    @tags_bp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()

    @tags_bp.arguments(TagSchema)
    @tags_bp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if (
            TagModel.query.filter(
                TagModel.store_id == store_id,
                TagModel.name == tag_data["name"]
            ).first()
        ):
            abort(400, message="A tag with that name already exists in that store.")

        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag
    

@tags_bp.route("/tag/<int:item_id>/tag/<int:tag_id>")
class ItemTag(MethodView):
    @tags_bp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message="An error occurred while adding the tag to the item")

        return tag
    
    @tags_bp.response(200, ItemTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while removing the tag from the item")

        return {"message": "Item removed from tag", "item": item, "tag": tag}
