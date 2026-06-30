import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from core.app_info import APP_VERSION


class ApiClient:
    """Cliente simples para enviar logs do desktop para a API local."""

    def __init__(self, base_url: str = "http://127.0.0.1:5000") -> None:
        self.base_url = base_url.rstrip("/")

    def send_log(
        self,
        event_type: str,
        *,
        status: str | None = None,
        message: str | None = None,
        url: str | None = None,
        download_format: str | None = None,
        quality: str | None = None,
        file_path: str | None = None,
        error_message: str | None = None,
    ) -> bool:
        payload = {
            "event_type": event_type,
            "status": status,
            "message": message,
            "url": url,
            "download_format": download_format,
            "quality": quality,
            "file_path": file_path,
            "error_message": error_message,
            "app_version": APP_VERSION,
        }
        payload = {key: value for key, value in payload.items() if value is not None}

        request = Request(
            f"{self.base_url}/api/logs",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=3) as response:
                return 200 <= response.status < 300
        except (OSError, URLError):
            return False
