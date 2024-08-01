from flask.views import MethodView
from flask_smorest import Blueprint, abort
from models import StoreModel, TagModel, ItemModel
from schemas import TagSchema, TagAndItemSchema
from sqlalchemy.exc import SQLAlchemyError
from db import db

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(200, TagSchema(many=True))
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name==tag_data["name"]).first():
            abort(400, message="A tag with that store name already exists in that store.")
        tag = TagModel(**tag_data, store_id=store_id)
        
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
    
@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema(many=True))
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @blp.response(202, description="Delete a tag if no item is tagged with it.", example={"Message: Tag deleted."})
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items. In this case, the tag is not deleted.")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message" : "Tag deleted."}
        abort(400, message="Could not delete tag. Maje sure tag is not associated with the any items, then try again.")
    
@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    @blp.response(200, TagSchema(many=True))
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        
        item.tags.append(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the tag.")
            
        return tag
    
    @blp.response(204, TagSchema(many=True))
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        
        item.tags.remove(tag)
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occured while inserting the tag.")
            
        return tag