import json
import logging
from os import environ
from typing import Any, Union
from azure.keyvault.secrets import SecretClient
from azure.identity import AzureCliCredential, ChainedTokenCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from common.settings import Setting, get_name


class StorageService:
    _default_credential = ChainedTokenCredential(
        ManagedIdentityCredential(), AzureCliCredential())
    _vault_name = environ.get(
        get_name(Setting.CFG_CONFIG_CORE_MAINKEYVAULT), 'az-serverless-bot')
    _vault_url = f"https://{_vault_name}.vault.azure.net/"
    _storage_name = environ.get(
        get_name(Setting.CFG_CONFIG_CORE_MAINSTORAGE), 'az-serverless-bot')
    _storage_url = f"https://{_storage_name}.blob.core.windows.net/"

    default_container = "bot-storage"

    def __init__(self, credential=None):
        logging.getLogger('azure').setLevel(logging.WARNING)
        self._credential = StorageService._default_credential if credential == None else credential
        self._main_storage_blob_client = BlobServiceClient(
            account_url=StorageService._storage_url,
            credential=self._credential,
            logging_enable=False)
        self._main_keyvault_client = SecretClient(
            vault_url=StorageService._vault_url,
            credential=self._credential,
            logging_enable=False)

    def get_secret(self, secret: str):
        return self.get_secret_client().get_secret(secret).value

    def get_secret_client(self):
        return self._main_keyvault_client

    def get_blob_account_client(self):
        return self._main_storage_blob_client

    def get_blob_client(self, container: str, blob: str):
        return (
            self.get_blob_account_client().get_container_client(
                container).get_blob_client(blob))

    def get_blob_data(self, container: str, blob: str):
        try:
            client = self.get_blob_client(container, blob)
            data_str = client.download_blob().readall()
            return json.loads(data_str)
        except Exception as e:
            logging.warning(f"error while downloading data {container}, {blob}")
            logging.error(e)
            return None

    def set_blob_data(
            self,
            container: str,
            blob: str,
            data: Union[Any, str],
            overwrite: bool = True):
        data_str = data if (isinstance(data, str)) else json.dumps(data)
        self.get_blob_client(container, blob).upload_blob(
            data=data_str, overwrite=overwrite)