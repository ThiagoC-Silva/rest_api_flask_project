from os import getenv
from flask_smorest import Api
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager

from db import db
from blocklist import BLOCKLIST
from flask_migrate import Migrate

# Blueprints
from resources.tag import tags_bp as tags_blueprint
from resources.item import items_bp as items_blueprint
from resources.user import users_bp as users_blueprint
from resources.store import stores_bp as stores_blueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config["API_TITLE"] = "Store API"
    app.config["API_VERSION"] = "v1"
    app.config["PROPAGTE_EXCEPTIONS"] = True
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Configurações do banco de dados
    app.config["SQLALCHEMY_DATABASE_URI" ]= db_url or getenv("DATABASE_URL","sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app) 
    migrate = Migrate(app, db)
    api = Api(app)

    # Cria as tabelas antes da primeira requisição
    # Método utilizado com o SQLAlchemy
    # with app.app_context():
    #     db.create_all()

    app.config["JWT_SECRET_KEY"] = "junindev"
    jwt = JWTManager(app)

    # Callbacks jwt
    @jwt.token_in_blocklist_loader
    def check_idf_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "Token_revoked"}
            )
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_refresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token is not fresh",
                 "error": "fresh_token_required"}
            )
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        if identity == "1":
            return {"is_admin": True}
        return {"is_admin": False}

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify ({"message": "The token has expired", "error": "token_expired"}), 401
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed", "error": "invalid_token"}), 401
        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({"message": "Request does not contain an access token", "error": "authorization_required"}), 401
        )

    api.register_blueprint(tags_blueprint)
    api.register_blueprint(items_blueprint)
    api.register_blueprint(users_blueprint)
    api.register_blueprint(stores_blueprint)

    return app
