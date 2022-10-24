from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel, TagModel, ItemModel
from schemas import TagSchema, TagAndItemSchema

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/tag")
class TagList(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self):
        return TagModel.query.all()
    
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema)
    def post(self, tag_data):
        tag = TagModel(**tag_data)
        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=str(e))
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag


@blp.route("/tag/<string:tag_id>")
class TagByID(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    
@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id = store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, {'message': f'SQLAlchemyerror {e}'})
        
        return tag
    
    
@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        
        item.tags.append(tag)  # apparently this will update all necessary relations, also in tags
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f'Item/tag error: {e}')
            
        return tag

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        
        item.tags.remove(tag)  # apparently this will update all necessary relations, also in tags
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f'Item/tag error: {e}')
        
        return {
            "message": f"Item removed from tag",
            "item": item,
            "tag": tag,
            }

@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(
        202, description="Deletes a tag if no item is tagged with it",
        example={"message": "Tag deleted"}
    )
    @blp.alt_response(404, description="Tag Not found")
    @blp.alt_response(400, description="Tag is assigned to one or more items, tag is not deleted")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, {"message": "Tag is assigned to one or more items, tag is not deleted"})

