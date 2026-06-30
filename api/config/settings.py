import os

from dotenv import load_dotenv


load_dotenv()

DATABASE_URI = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://pyflow:pyflow@localhost:5433/pyflow_downloader",
)


class Config:
    API_TITLE = "PyFlow"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.2"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/swagger-ui"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_ENGINE_OPTIONS = (
        {
            "connect_args": {
                "connect_timeout": int(os.getenv("DATABASE_CONNECT_TIMEOUT", "3")),
            }
        }
        if DATABASE_URI.startswith("postgresql")
        else {}
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
