from loguru import logger

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.formatting import as_list, as_line
from aiogram.enums import ParseMode

from app_globals import app_config, bot


router = Router()


@router.message(Command("start", "help"))
@logger.catch
async def cmd_start(message: Message):
    logger.debug("-> Enter Def")
    if message.chat.id != bot.chat_id: return

    t = as_list(
        as_line(app_config['telegram']['service_nickname']),
        "📖 Commands:", "",
        " ⦙ /start or /help ⋅ This message", "",
        " ⦙ /view_config ⋅ View service config", "",
        " ⦙ /view_node ⋅ View a node status", "",
        " ⦙ /view_wallet ⋅ View a wallet info", "",
        " ⦙ /view_address ⋅ View any wallet info", "",
        " ⦙ /add_node ⋅ Add a node to bot", "",
        " ⦙ /add_wallet ⋅ Add a wallet to bot", "",
        " ⦙ /delete_node ⋅ Delete node from bot", "",
        " ⦙ /delete_wallet ⋅ Delete wallet from bot", "",
        " ⦙ /release ⋅ Show actual MASSA release", "",
        " ⦙ /id ⋅ Show chat_id", "",
        " ⦙ /cancel ⋅ Cancel any scenario", "",
        "☝ Bot info: https://github.com/dex2code/massa_acheta", ""
    )

    await message.answer(
        text=t.as_html(),
        parse_mode=ParseMode.HTML,
        request_timeout=app_config['telegram']['sending_timeout_sec']
    )
