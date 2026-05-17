import logging

from telegram import Bot, BotCommand, BotCommandScopeDefault, MenuButtonCommands

logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand("start", "Start the bot and show main menu"),
    BotCommand("bump", "Start bumping tiers"),
    BotCommand("volume", "Open chart volume packages"),
    BotCommand("trending", "Open trend push packages"),
    BotCommand("help", "Help and how it works"),
]


async def setup_telegram_menu(bot: Bot) -> None:
    """Blue Menu button + command hints when typing /."""
    await bot.set_my_commands(BOT_COMMANDS, scope=BotCommandScopeDefault())
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
    logger.info("Telegram menu button and /commands registered.")
