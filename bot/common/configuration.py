from os import environ
from typing import Dict, Union
from common.settings import Setting, get_name
from common.storage import StorageService


class ConfigurationService:

    def __init__(self, storage_service: StorageService) -> None:
        self._storage_service = storage_service or StorageService()
        self._values: Dict[str, str] = {}

    def _get_secret(self, key: str) -> Union[str, None]:
        return self._storage_service.get_secret(key)

    def _get_config(self, key: str) -> Union[str, None]:
        self._values = self._values or self._storage_service.get_blob_data(
            StorageService.default_container, 'settings.json')
        return self._values[key] if key in self._values.keys() else None

    def get(self, key: Setting) -> Union[str, None]:
        name = get_name(key)
        env_value = environ.get(name)
        if env_value:
            return env_value
        elif name.startswith('cfg-config'):
            return self._get_config(name.replace('cfg-config-', ''))
        elif name.startswith('cfg-secret'):
            return self._get_secret(name.replace('cfg-secret-', ''))
        else:
            raise Exception(f"Invalid configuration type {name}")