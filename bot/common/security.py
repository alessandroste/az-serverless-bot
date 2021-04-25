import base64
import logging
import os
from typing import Tuple

from azure.functions import HttpRequest
from common.storage import StorageService
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import pkcs12

HEADER_CERT = 'X-ARR-ClientCert'


def check_certificate(request: HttpRequest,
                      storage_service: StorageService) -> Tuple[bool, str]:
    required_cert_str = os.environ.get(
        'Secrets.BotCertificate', '@Microsoft.KeyVault')
    if (required_cert_str.startswith('@Microsoft.KeyVault')):
        required_cert_str = storage_service.get_secret("astrotards-bot-cert")
    if not required_cert_str:
        logging.warning(f"Could not retrieve certificate from KV")
        return (False, "Internal error")
    _, required_cert, _ = pkcs12.load_key_and_certificates(
        base64.b64decode(required_cert_str), password=None)
    if not required_cert:
        return (False, "Internal error")
    required_fingerprint = required_cert.fingerprint(hashes.SHA256())
    try:
        client_cert_str = request.headers.get(HEADER_CERT)
    except:
        client_cert_str = None
    if not client_cert_str:
        logging.warning(f"No certificate set in the header {HEADER_CERT}")
        return (False, "No certificate found in the headers")
    _, client_cert, _ = pkcs12.load_key_and_certificates(
        base64.b64decode(required_cert_str), password=None)
    if not client_cert:
        return (False, "Certificate in the header is not valid")
    client_fingerprint = client_cert.fingerprint(hashes.SHA256())
    if client_fingerprint != required_fingerprint:
        logging.warning(
            f"Client certificate is not matching {client_fingerprint.hex()}")
        return (False, "Certificate not accepted")
    return (True, '')