# RESTful API
# 使用HTTP協議作為基礎通過使用HTTP的方法（如GET、POST、PUT、DELETE等）來執行CRUD（Create、Read、Update、Delete）操作

from flask import Flask,request
from db import stores,items
from flask_smorest import abort
import uuid

app =Flask(__name__)

# 查詢 store
@app.get("/store")
def get_all_store():
    return {"stores":list(stores.values())}

# 新增 store
@app.post("/store")
def create_store():
    request_data = request.get_json()

    if "store_name" not in request_data:
        abort(400, message="確認 store_name 是否正確")

    for store in stores.values():
        if request_data["store_name"] == store["store_name"]:
            return abort(400, message="store_name 已經存在")
            
    store_id = uuid.uuid4().hex
    new_store = {
        **request_data,
        "store_id": store_id
    }
    stores[store_id] = new_store
    print(stores)
    return stores,201

# 刪除 store
@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        return {"message":"已成功刪除 store"}
    except KeyError:
        abort(400, message="store_id不存在")

# 查詢 item
@app.get("/item")
def get_all_item():
    return {"items":list(items.values())}

#  新增item
@app.post("/item")
def create_item():
    request_data = request.get_json()
    print(request_data)
    if (
        "store_id" not in request_data
        or "product_name" not in request_data
        or "product_price" not in request_data
    ):
        abort(400, message="確認 store_id/product_price/product_name 是否正確")

    for item in items.values():
        if (
            request_data['product_name'] == item['product_name'] 
            and request_data['store_id'] == item['store_id']
        ):
            abort(400, message=f"item 已經存在")
            
    item_id = uuid.uuid4().hex
    new_item = {
        **request_data,
        "item_id": item_id
    }
    items[item_id] = new_item
    return items,201

# 刪除 item
@app.delete("/item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id]
        return {"message":"已成功刪除 item"}
    except KeyError:
        abort(400, message="item_id 不存在")

# 更新 item
@app.put("/item/<string:item_id>")
def update_item(item_id):
    request_data = request.get_json()
    if "product_price" not in request_data or "product_name" not in request_data:
        abort(400,message="確認 product_price/product_name 是否正確")
    try:
        item = items[item_id]
        item |= request_data # 合併兩個字典(更新資料)
        return item
    except KeyError:
        abort(404, message="item 不存在")

if __name__ == "__main__":
    app.run(debug=True)