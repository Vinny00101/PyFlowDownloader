from flask_smorest import Blueprint


health_bp = Blueprint("health", __name__, url_prefix="/api", description="Health check")


@health_bp.get("/health")
@health_bp.doc(summary="Verifica se a API está online")
def health():
    return {"status": "ok"}
