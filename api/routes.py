from flask import Blueprint, jsonify, request

from api.models import AppLog, db


api_bp = Blueprint("api", __name__, url_prefix="/api")

ALLOWED_EVENT_TYPES = {
    "download_started",
    "download_completed",
    "download_cancelled",
    "download_error",
    "ffmpeg_install_completed",
    "ffmpeg_install_error",
    "ytdlp_updated",
}


@api_bp.get("/health")
def health():
    return {"status": "ok"}


@api_bp.post("/logs")
def create_log():
    data = request.get_json(silent=True) or {}
    event_type = str(data.get("event_type", "")).strip()

    if not event_type:
        return jsonify({"error": "event_type é obrigatório"}), 400
    if event_type not in ALLOWED_EVENT_TYPES:
        return jsonify({"error": "event_type não é permitido"}), 400

    log = AppLog(
        event_type=event_type,
        status=data.get("status"),
        message=data.get("message"),
        url=data.get("url"),
        download_format=data.get("download_format"),
        quality=data.get("quality"),
        file_path=data.get("file_path"),
        error_message=data.get("error_message"),
        app_version=data.get("app_version"),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify(log.to_dict()), 201


@api_bp.get("/logs")
def list_logs():
    limit = min(request.args.get("limit", default=50, type=int), 200)
    query = AppLog.query

    event_type = request.args.get("event_type")
    if event_type:
        query = query.filter(AppLog.event_type == event_type)

    logs = query.order_by(AppLog.created_at.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])
