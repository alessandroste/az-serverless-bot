# IMPORTANT: replace {YOUR_DOMAIN} with your custom domain in the form domain.net

import datetime
import logging
import re
import ssl
import sys
import time
from io import BytesIO
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from common.settings import Setting
from common.configuration import ConfigurationService
from telegram.bot import Bot
from common.storage import StorageService
from cryptography.hazmat.primitives.serialization import Encoding

logging.basicConfig(level=logging.INFO)

url = "https://{YOUR_DOMAIN}/bot"

storage_service = StorageService()
configuration_service = ConfigurationService(storage_service)
token_param = list(filter(lambda p: p.startswith('token:'), sys.argv))
if token_param:
    token = token_param[0].replace('token:', '')
else:
    token = configuration_service.get(Setting.CFG_SECRET_TELEGRAM_BOT_TOKEN)

bot = Bot(token)
logging.info(f"Setting up bot {bot.first_name}")

cert_stream: BytesIO = None

cert_param = list(filter(lambda p: p.startswith('cert:'), sys.argv))
if cert_param:
    cert_file = cert_param[0].replace('cert:', '')
    if cert_file:
        logging.info(f"Attempting read from file {cert_file}")
        with open(cert_file) as f:
            cert_str = f.read()
    else:
        cert_str = ssl.get_server_certificate(('{YOUR_DOMAIN}', 443))
    for single_cert in re.findall(
            '-----BEGIN CERTIFICATE-----[^-]+-----END CERTIFICATE-----',
            cert_str):
        downloaded_cert = x509.load_pem_x509_certificate(
            single_cert.encode('utf-8'), default_backend())
        fingerprint = ''.join(
            [
                "{:02X}".format(x)
                for x in downloaded_cert.fingerprint(hashes.SHA1())
            ])
        logging.info(
            f"Found certificate {fingerprint}, {downloaded_cert.subject}")
    cert_stream = BytesIO(cert_str.encode('utf-8'))
bot.set_webhook(url=url, certificate=cert_stream)
logging.info(f"Webhook was set on url {url}")
time.sleep(5)
info = bot.get_webhook_info()
if info.last_error_date:
    error_time = datetime.datetime.utcfromtimestamp(info.last_error_date)
    logging.error(f"{error_time}: {info.last_error_message}")