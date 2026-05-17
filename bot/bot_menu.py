import logging

from telegram import Bot, BotCommand, BotCommandScopeDefault, MenuButtonCommands

logger = logging.getLogger(__name__)

# Keep the command list minimal. Everything else is in the inline menu.
BOT_COMMANDS = [
    BotCommand("start", "Open main menu"),
]


async def setup_telegram_menu(bot: Bot) -> None:
    await bot.set_my_commands(BOT_COMMANDS, scope=BotCommandScopeDefault())
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    logger.info("Telegram menu: /start only.")
