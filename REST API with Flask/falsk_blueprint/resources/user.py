from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from blocklist import BLOCKLIST

from db import db
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        # 如果用戶存在且密碼正確，則 login 時產生token，其中包含access_token(15分鐘)和refresh_token(30天)
        if user and pbkdf2_sha256.verify(user_data["password"], user.password): 
            access_token = create_access_token(identity=user.id,fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token,"refresh_token": refresh_token}, 200
        else: # 如果使用者不存在或密碼不正確，則傳回一個HTTP 401 狀態碼和一個錯誤訊息
            abort(401, message="Invalid credentials.")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        # 如果用戶存在，回傳
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            # 409 代表客戶端的請求與目標資源的當前狀態衝突
            # 例如當兩個客戶端同時嘗試更新相同的資源時，當客戶端嘗試將資源移動到目前狀態不允許的狀態，
            # 或當客戶端嘗試刪除仍在其他進程中使用的資源
            abort(409, message="A user with that username already exists.")  

        # 如果 username 不存在，則新增 user 進資料庫
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        db.session.add(user)
        db.session.commit()

        return {"message": "User created successfully."}, 201

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti) # 當 user 登出時，將其jti加入黑名單中，避免再次登入
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """
    This resource can be useful when testing our Flask app.
    We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful
    when we are manipulating data regarding the users.
    """

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted."}, 200


# 允許客戶端使用有效的 refresh_token 來獲取一個新的access_token,從而延長訪問週期,無需再次輸入用戶憑證
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) # 只接受 refresh_token,不接受 access_token
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200