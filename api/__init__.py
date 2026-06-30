from flask import Flask
from flask_smorest import Api
from sqlalchemy import text

from api.config import Config
from api.models import db
from api.routes import download_bp, health_bp, log_bp

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    api = Api(app)
    db.init_app(app)
    api.register_blueprint(health_bp)
    api.register_blueprint(download_bp)
    api.register_blueprint(log_bp)

    with app.app_context():
        try:
            db.session.execute(text("SELECT 1"))
            db.create_all()
            print("[API] Conexão com o banco efetuada com sucesso.")
        except Exception as exc:
            print(f"[API] Erro ao conectar no banco de dados: {exc}")
            raise

    return app
