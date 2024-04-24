import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import ItemSchema, ItemUpdateSchema

from flask_jwt_extended import jwt_required, get_jwt

blp = Blueprint("items",__name__,description="針對 item 操作")

# 查詢 item
@blp.route("/item",methods=["GET"])
@blp.response(200, ItemSchema(many=True))
def get_all_item():
    return ItemModel.query.all()

# 查詢 item by item_id
@blp.route("/item/<string:item_id>",methods=["GET"])
def get(item_id):
    item = ItemModel.query.get_or_404(item_id)
    return item

# 新增 item
@jwt_required(fresh=True) # 必須為 fresh_token
@blp.route("/item",methods=["POST"])
@blp.arguments(ItemSchema) # mashmallow 規範新增 item 格式
@blp.response(201, ItemSchema(many=True))
def create_item(request_data):
    item_data = ItemModel(**request_data)

    try:
        db.session().add(item_data)
        db.session().commit()
    except SQLAlchemyError:
        abort(500,message="An error occurred inserting the item.") # 500 代表伺服器內部錯誤和異常

    return item_data

# 刪除 item(admin only)
@blp.route("/item/<string:item_id>",methods=["DELETE"])
@jwt_required()
def delete_item(item_id):
    # 檢查 jwt payload 是否有 is_admin 屬性
    jwt = get_jwt()
    if not jwt.get("is_admin"):
        abort(401, message="Admin privilege required.")

    item = ItemModel.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return {"message": "Item successfully deleted."},200

# 更新 item
@blp.route("/item/<string:item_id>",methods=["PUT"])
@blp.arguments(ItemUpdateSchema) # mashmallow 規範更新 item 格式
def update_item(request_data,item_id):
    item = ItemModel.query.get(item_id)
    if item: # 如果搜尋 item_id 存在，則 update 該筆資料   
        item.price = request_data["item_price"]
        item.name = request_data["item_name"]
    else: # 如果沒有該筆資料則 insert
        item = ItemModel(id=item_id,**request_data)
    db.session.add(item)
    db.session.commit()
    return item