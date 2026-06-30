from flask import jsonify, request
from flask_smorest import Blueprint

from api.services import DownloadService


download_bp = Blueprint(
    "downloads",
    __name__,
    url_prefix="/api/downloads",
    description="Histórico de downloads",
)


@download_bp.post("")
@download_bp.doc(summary="Cria um registro de download")
def create_download():
    data = request.get_json(silent=True) or {}
    if not data.get("url"):
        return jsonify({"error": "url é obrigatória"}), 400

    download = DownloadService.create(data)
    return jsonify(download.to_dict()), 201


@download_bp.get("")
@download_bp.doc(summary="Lista downloads")
def list_downloads():
    limit = min(request.args.get("limit", default=50, type=int), 200)
    status = request.args.get("status")
    downloads = DownloadService.list(limit=limit, status=status)
    return jsonify([download.to_dict() for download in downloads])


@download_bp.get("/<int:download_id>")
@download_bp.doc(summary="Busca um download pelo ID")
def get_download(download_id: int):
    download = DownloadService.get(download_id)
    if download is None:
        return jsonify({"error": "download não encontrado"}), 404
    return jsonify(download.to_dict())


@download_bp.patch("/<int:download_id>")
@download_bp.doc(summary="Atualiza um download")
def update_download(download_id: int):
    data = request.get_json(silent=True) or {}
    download = DownloadService.update(download_id, data)
    if download is None:
        return jsonify({"error": "download não encontrado"}), 404
    return jsonify(download.to_dict())


@download_bp.delete("")
@download_bp.doc(summary="Remove todos os downloads")
def clear_downloads():
    deleted = DownloadService.clear()
    return jsonify({"deleted": deleted})
