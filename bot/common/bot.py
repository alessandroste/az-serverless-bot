import logging
from queue import Queue

from common.configuration import ConfigurationService
from common.reddit import get_relevat_subreddits
from common.settings import Setting
from common.storage import StorageService
from functools import wraps
from telegram import Bot, ChatAction, Update
from telegram.ext import CallbackContext, CommandHandler, Dispatcher

convos_blob_name = "registered-convos.json"


def build_dispatcher(storage_service: StorageService) -> Dispatcher:
    configuration_service = ConfigurationService(storage_service)
    token = configuration_service.get(Setting.CFG_SECRET_TELEGRAM_BOT_TOKEN)
    dispatcher = Dispatcher(Bot(token), Queue())
    dispatcher.add_handler(CommandHandler("start", cmd_register_callback))
    dispatcher.add_handler(CommandHandler("stop", cmd_unregister_callback))
    return dispatcher


def send_action(action):
    """Sends `action` while processing func command."""

    def decorator(func):

        @wraps(func)
        def command_func(update, context, *args, **kwargs):
            context.bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action)
            return func(update, context, *args, **kwargs)

        return command_func

    return decorator


@send_action(ChatAction.TYPING)
def cmd_register_callback(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        logging.warn(f"No message found in the update")
        return
    chat_id = str(message.chat_id)
    logging.info(f"Registering chat {chat_id}")
    if not register_chat(chat_id):
        text = "Already registered"
    else:
        text = "Registered 🚀"
    message.reply_text(text=text)
    logging.info(f"Registered chat {chat_id}")


@send_action(ChatAction.TYPING)
def cmd_unregister_callback(update: Update, context: CallbackContext):
    message = update.message
    if not message:
        logging.warn(f"No message found in the update")
        return
    chat_id = str(message.chat_id)
    logging.info(f"Unregistering chat {chat_id}")
    unregister_chat(chat_id)
    message.reply_text("Unregistered")
    logging.info(f"Unregistered chat {chat_id}")


def unregister_chat(chat_id: str) -> bool:
    storage = StorageService()
    convos = (
        storage.get_blob_data(
            StorageService.default_container, convos_blob_name) or {})
    if chat_id in convos:
        del convos[chat_id]
        storage.set_blob_data(
            StorageService.default_container, convos_blob_name, convos)
        return True
    else:
        return False


def register_chat(chat_id: str) -> bool:
    storage_service = StorageService()
    subreddits = get_relevat_subreddits(storage_service)
    convos = (
        storage_service.get_blob_data(
            StorageService.default_container, convos_blob_name) or {})
    if chat_id not in convos:
        convos[chat_id] = subreddits
        storage_service.set_blob_data(
            StorageService.default_container, convos_blob_name, convos)
        return True
    return False
