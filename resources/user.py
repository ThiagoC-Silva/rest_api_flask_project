from flask.views import MethodView
from passlib.hash import pbkdf2_sha256
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt

from db import db 
from models import UserModel
from schemas import UserSchema
from blocklist import BLOCKLIST

users_bp = Blueprint("Users", __name__, description="User operations")

@users_bp.route("/login")
class UserLogin(MethodView):

    @users_bp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}, 200

        abort(401, message="Invalid credentials.")    

@users_bp.route("/refresh")
class TokenRefresh(MethodView):

    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}

@users_bp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
    
        return {"message": "Logged out successfuly."}
        

@users_bp.route("/register")
class UserRegister(MethodView):

    @users_bp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(409, message="User already exists")

        user = UserModel(
            username = user_data["username"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )

        db.session.add(user)
        db.session.commit()

        return {"message": "User created"}, 201
    
@users_bp.route("/user/<int:user_id>")
class User(MethodView):

    @users_bp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
     
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()

        return {"message": "User deleted"}, 200