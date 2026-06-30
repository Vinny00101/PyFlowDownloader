from flask import jsonify, request
from flask_smorest import Blueprint

from api.services import LogService


log_bp = Blueprint(
    "logs",
    __name__,
    url_prefix="/api/logs",
    description="Logs do sistema",
)


@log_bp.post("")
@log_bp.doc(summary="Cria um log")
def create_log():
    data = request.get_json(silent=True) or {}
    try:
        log = LogService.create(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(log.to_dict()), 201


@log_bp.get("")
@log_bp.doc(summary="Lista logs")
def list_logs():
    limit = min(request.args.get("limit", default=50, type=int), 200)
    event_type = request.args.get("event_type")
    logs = LogService.list(limit=limit, event_type=event_type)
    return jsonify([log.to_dict() for log in logs])


@log_bp.delete("")
@log_bp.doc(summary="Remove todos os logs")
def clear_logs():
    deleted = LogService.clear()
    return jsonify({"deleted": deleted})
