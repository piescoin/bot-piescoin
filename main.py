import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.filters import Command
from aiogram.dispatcher.router import Router
from dotenv import load_dotenv
import sys
from pathlib import Path

# Clone and import custom library
REPO_URL = "https://github.com/piescoin/bot-piescoin.git"
LIB_PATH = Path("bot_piescoin")

if not LIB_PATH.exists():
    os.system(f"git clone {REPO_URL}")
sys.path.append(str(LIB_PATH))

try:
    from bot_piescoin.custom_module import CustomClass, helper_function  # Adjust imports based on the repo structure
except ImportError:
    logging.error("Failed to import the custom module from the repository.")
    raise

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "7826649604:AAF7T4pSAAaf99ThPlfCDWSkkBPvXXBImhQ")

# Initialize bot and router
bot = Bot(token=TOKEN)
router = Router()

# Example user data structure
users = {}

# Base constants
MAX_ENERGY = 5000
DOG_IMAGES = {
    1: "images/dog_level_1.jpg",
    2: "images/dog_level_2.jpg",
    3: "images/dog_level_3.jpg",
}

# Function to generate the main game screen
def get_main_screen(user_data):
    caption = (
        f"<b>🐕 Ваш Пес</b>\n"
        f"<b>🔋 Енергія:</b> {user_data['energy']} / {MAX_ENERGY}\n\n"
        "Натискайте на пса, щоб зібрати монети!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Меню", callback_data="open_menu")]
    ])

    return caption, keyboard

@router.message(Command("start"))
async def send_welcome(message: Message):
    user_id = message.from_user.id

    # Initialize user data if not exists
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "energy": MAX_ENERGY,
            "level": 1,
        }

    # Show initial screen with the dog image
    user_data = users[user_id]
    dog_image = DOG_IMAGES.get(user_data["level"], DOG_IMAGES[1])
    caption, keyboard = get_main_screen(user_data)

    with open(dog_image, "rb") as photo:
        await message.answer_photo(
            photo=photo,  # Correctly passing the opened file
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

@router.callback_query(lambda c: c.data == "open_menu")
async def open_menu(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in users:
        await callback_query.answer("Помилка: Користувач не знайдений.", show_alert=True)
        return

    user_data = users[user_id]

    caption = (
        f"<b>📋 Меню</b>\n\n"
        "Оберіть дію:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💪 Вдосконалення", callback_data="upgrade")],
        [InlineKeyboardButton(text="👥 Реферали", callback_data="referrals")],
        [InlineKeyboardButton(text="💎 Донат", callback_data="donate")],
        [InlineKeyboardButton(text="🔙 Назад до гри", callback_data="back_to_game")]
    ])

    await callback_query.message.edit_text(caption, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(lambda c: c.data == "back_to_game")
async def back_to_game(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id not in users:
        await callback_query.answer("Помилка: Користувач не знайдений.", show_alert=True)
        return

    user_data = users[user_id]

    dog_image = DOG_IMAGES.get(user_data["level"], DOG_IMAGES[1])
    caption, keyboard = get_main_screen(user_data)

    with open(dog_image, "rb") as photo:
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback_query.message.edit_media(
            media=InputMediaPhoto(media=photo)
        )

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
