import uuid
from flask import Flask, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores, items
from schemas import StoreSchema

blp = Blueprint('Stores', __name__, description='Operations on stores')


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="Store not found")

    def delete(self, store_id):
        try:
            del stores[store_id]
            global items
            items = dict(
                filter(lambda item: item[1]["store_id"]
                       != store_id, items.items())
            )
            return {"message": "Store deleted successfully"}
        except KeyError:
            abort(404, message="Store not found")


@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema)
    def get(self):
        return {"stores": list(stores.values())}

    @blp.arguments(StoreSchema)
    @blp.response(200, StoreSchema)
    def post(self, store_data):
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(405, message="Store already exists")

        store_id = uuid.uuid4().hex
        store = {**store_data, "id": store_id}
        stores[store_id] = store
        return store, 201


@blp.route("/store/items/<string:store_id>")
class StoreItemList(MethodView):
    def get(self, store_id):
        try:
            store = stores[store_id]
        except KeyError:
            abort(404, message="Store not found")

        store_items = [item for _, item in items.items()
                       if item["store_id"] == store_id]
        return {"store": store, "items": store_items}
