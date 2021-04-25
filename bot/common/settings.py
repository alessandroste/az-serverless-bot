from enum import Enum, auto


class Setting(Enum):
    CFG_CONFIG_CORE_MAINSTORAGE = auto()
    CFG_CONFIG_CORE_MAINKEYVAULT = auto()
    CFG_SECRET_TELEGRAM_BOT_TOKEN = auto()


def get_name(setting: Setting) -> str:
    return setting.name.casefold().replace('_', '-')