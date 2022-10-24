from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    get_jwt_identity,
    get_jwt, 
    jwt_required
)
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema


blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class RegisterUser(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        username = user_data["username"]
        password_hash = pbkdf2_sha256.hash(user_data["password"])
        user = UserModel(
            username=username, 
            password=password_hash
            )
        
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            abort(500, message='Username already exists')
        except SQLAlchemyError as e:
            abort(500, message=f"SQLAlchemyerror: {e}")
        # The message below is not shown; it only returns the 'user'
        # return user
        return {"message": "User created successfully"}
    

@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted"}, 200

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        username = user_data["username"]
        user = UserModel.query.filter(
            UserModel.username == username
        ).first()
        if not user:
            abort(403, {"message": "Username not found"})
        
        password = user_data["password"]
        password_is_correct = pbkdf2_sha256.verify(password, user.password)
        if password_is_correct:
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        abort(403, {"message": "Wrong password, forbidden"})
        
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}
    
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
