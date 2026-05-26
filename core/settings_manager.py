import copy
import json
import os
from pathlib import Path
from typing import Any


class SettingsManager:
    """Gerencia leitura, escrita e valores padrão das configurações do app."""

    def __init__(
        self,
        app_name: str = "PyFlowDownloader",
        settings_dir: str | Path | None = None,
    ) -> None:
        self.app_name = app_name
        self.settings_dir = Path(settings_dir) if settings_dir else self._get_settings_app_data()
        self.settings_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.settings_dir / "settings.json"
        self._defaults = self._get_default_settings()
        self._settings: dict[str, Any] = {}
        self.load()

    def _get_settings_app_data(self) -> Path:
        """Metodo para definir o caminho do Settings no APPDATA"""
        if os.name == "nt":
            base_dir = os.getenv("APPDATA") or str(Path.home())
        else:
            base_dir = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))

        settings_dir = Path(base_dir) / self.app_name
        settings_dir.mkdir(parents=True, exist_ok=True)
        return settings_dir

    def _get_default_settings(self) -> dict[str, Any]:
        """Define os valores padrão para todas as configurações.
        returns:
            Retorna um dicionario contendo todas as configuações base do Programa
        """
        return {
            "appearance": {
                "theme": "dark",
                "font_size": 10,
            },
            "downloads": {
                "default_path": str(Path.home() / "Downloads"),
                "default_format": "mp4",
                "default_quality": "720p",
                "concurrent_downloads": 3,
            },
            "tools": {
                "ffmpeg_path": "",
            },
            "youtube": {
                "browser_cookies": "chrome",
            },
            "window": {
                "x": 100,
                "y": 100,
                "width": 1200,
                "height": 800,
                "maximized": False,
            },
        }

    def load(self) -> bool:
        """
        Metodo para realiza a buscar das configurações no diretorio criado no APPDATA
        
        returns:
            Retorna um valor boleano idicando se a buscar realizada deu certo ou não
        """
        loaded_settings: dict[str, Any] = {}
        try:
            if self.settings_file.exists():
                with self.settings_file.open("r", encoding="utf-8") as file:
                    loaded_settings = json.load(file)

            self._settings = self._deep_merge(self._defaults, loaded_settings)
            return True
        except (OSError, json.JSONDecodeError, TypeError):
            self._settings = copy.deepcopy(self._defaults)
            return False

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Obtém um valor de configuração usando notação de pontos.
        
        args:
            key_path: Caminho da configuração (ex: "appearance.theme")
            default: Valor retornado se a chave não existir
            
        returns:
            Valor da configuração ou default
        """
        current: Any = self._settings
        for key in key_path.split("."):
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def set(self, key_path: str, value: Any) -> None:
        """
        Recebi o camainho da chave e um valor para ser atualizado nas configurações

        args:
            key_path: Caminho da chave que deve inserir o novo valor
            value: O valor que será inserirdo nas configurações 
        """
        keys = key_path.split(".")
        if not keys:
            return

        current = self._settings
        for key in keys[:-1]:
            next_value = current.get(key)
            if not isinstance(next_value, dict):
                next_value = {}
                current[key] = next_value
            current = next_value

        current[keys[-1]] = value

    def save(self) -> bool:
        """
        Salva as configurações atuais no arquivo JSON.
        
        Returns:
            True se salvo com sucesso, False se houve erro
        """
        try:
            self.settings_dir.mkdir(parents=True, exist_ok=True)
            with self.settings_file.open("w", encoding="utf-8") as file:
                json.dump(self._settings, file, indent=2, ensure_ascii=False)
            return True
        except OSError:
            return False

    def as_dict(self) -> dict[str, Any]:
        """Retorna uma cópia das configurações atuais."""
        return copy.deepcopy(self._settings)

    def _deep_merge(
        self,
        default_settings: dict[str, Any],
        loaded_settings: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Realiza a junção entre as duas configurações sem deixa conflito
        
        args:
            default_settigs: Configuração base/default
            settigs_app_data: Configuração do diretorio do AppData
            
        returns:
            Resultado com um dicionario com as configuração
        """
        result = copy.deepcopy(default_settings)
        for key, value in loaded_settings.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
