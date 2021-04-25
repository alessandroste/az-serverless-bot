from common.storage import StorageService
from common.bot import build_dispatcher
from azure.functions import HttpRequest, HttpResponse
from telegram import Update


def main(request: HttpRequest) -> HttpResponse:
    storage_service = StorageService()
    dispatcher = build_dispatcher(storage_service)
    dispatcher.process_update(
        Update.de_json(request.get_json(), bot=dispatcher.bot))
    return HttpResponse()
