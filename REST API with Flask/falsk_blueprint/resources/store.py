import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from db import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import StoreSchema
from models import StoreModel

blp = Blueprint("stores",__name__,description="針對 stores 操作")

# 查詢 store
@blp.route("/store",methods=["GET"])
@blp.response(200, StoreSchema(many=True))
def get_all_store():
    return StoreModel.query.all()

# 查詢 store by store_id
@blp.route("/store/<string:store_id>",methods=["GET"])
def get(store_id):
    store = StoreModel.query.get_or_404(store_id) # retrive by pk, if not found return 404
    return store

# 新增 store
@blp.route("/store",methods=["POST"])
@blp.arguments(StoreSchema) # mashmallow 規範新增 item 格式
@blp.response(201, StoreSchema(many=True)) # 定義 response code(many=True, 定義回傳 list，return stores.values())
def create_store(request_data): # request_data 會是已經通過驗證的 StoreSchema 的 json 資料(不用再定義 request.get_jsion())
    store_data = StoreModel(**request_data) # 

    try:
        db.session().add(store_data)
        db.session().commit()
    except IntegrityError:
        abort(404,message="A store with that name already exists.") # 404 代表找不到 client request 的資源

    except SQLAlchemyError:
        abort(400,message="An error occurred creating the store.") # 400 代表 client 發送的 request 有問題(參數錯誤)

    return store_data

# 刪除 store
@blp.route("/store/<string:store_id>",methods=["DELETE"])
def delete_store(store_id):
    store = StoreModel.query.get_or_404(store_id)
    db.session.delete(store)
    db.session.commit()
    return {"message": "Store successfully deleted."},200

