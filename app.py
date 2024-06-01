import uuid
from flask import Flask, request
from flask_smorest import abort
from db import stores, items


app = Flask(__name__)


@app.route("/")
def home():
    return "Home Page"


@app.get("/store")
def get_store():
    return {"stores": list(stores.values())}


@app.post("/store")
def create_store():
    store_data = request.get_json()
    required_fields = {"name"}
    if not required_fields.issubset(store_data):
        abort(400, message="Bad request. Ensure name is included in JSON payload")

    store_id = uuid.uuid4().hex
    store = {**store_data, "id": store_id}
    stores[store_id] = store
    return store, 201


@app.post("/item")
def create_item():
    item_data = request.get_json()
    required_fields = {"price", "store_id", "name"}
    if not required_fields.issubset(item_data):
        abort(
            400,
            message="Bad request. Ensure price, store_id and name are included in JSON payload",
        )
    if item_data["store_id"] not in stores:
        abort(404, message="Store not found")
    item_id = uuid.uuid4().hex
    item = {**item_data, "id": item_id}
    items[item_id] = item

    return item, 201


@app.get("/item")
def get_all_items():
    return {"items": list(items.values())}


@app.get("/store/<string:store_id>")
def get_store_by_id(store_id):
    try:
        return stores[store_id]
    except KeyError:
        abort(404, message="Store not found")


@app.get("/item/<string:item_id>")
def get_item(item_id):
    try:
        return items[item_id]
    except KeyError:
        abort(404, message="Items not found")


@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message": "Item deleted"}
    except KeyError:
        abort(404, message="Item not found")


@app.get("/store/items/<string:store_id>")
def get_store_items_by_store_id(store_id):
    try:
        store = stores[store_id]
    except KeyError:
        abort(404, message="Store not found")

    store_items = [item for _, item in items.items() if item["store_id"] == store_id]
    return {"store": store, "items": store_items}


@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        global items
        items = dict(
            filter(lambda item: item[1]["store_id"] != store_id, items.items())
        )
        return {"message": "Store deleted successfully"}
    except KeyError:
        abort(404, message="Store not found")

@app.put("/item/<string:item_id>")
def update_item(item_id):
    item_data = request.get_json()
    if ("name" not in item_data or "price" not in item_data):
        abort(
            400,
            message="Bad request. Ensure price and name are included in JSON payload",
        )
    
    try:
        global items
        items[item_id] |= item_data
        return {"items": items, "message": "Updated successfully"}
    except KeyError:
        abort(404, message="Item not found")
        
        
if __name__ == "__main__":
    app.run()
