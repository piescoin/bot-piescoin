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

# Ensure the library path is correctly added to the system path
sys.path.append(str(Path(__file__).parent / "bot_piescoin"))

try:
    from bot_piescoin.custom_module import CustomClass, helper_function  # Adjust imports based on the repo structure
except ImportError as e:
    logging.error(f"Failed to import the custom module from the repository: {e}")
    raise

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set. Please check your .env file.")

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
        f"<b>\ud83d\udc15 Ваш Пес</b>\n"
        f"<b>\ud83d\udd0b Енергія:</b> {user_data['energy']} / {MAX_ENERGY}\n\n"
        "Натискайте на пса, щоб зібрати монети!"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\ud83d\udccb Меню", callback_data="open_menu")]
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

    # Ensure the dog image file exists
    if not Path(dog_image).is_file():
        logging.error(f"Dog image not found: {dog_image}")
        await message.answer("Помилка: Зображення пса не знайдено.")
        return

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
        f"<b>\ud83d\udccb Меню</b>\n\n"
        "Оберіть дію:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\ud83d\udcaa Вдосконалення", callback_data="upgrade")],
        [InlineKeyboardButton(text="\ud83d\udc65 Реферали", callback_data="referrals")],
        [InlineKeyboardButton(text="\ud83d\udc8e Донат", callback_data="donate")],
        [InlineKeyboardButton(text="\ud83d\udd19 Назад до гри", callback_data="back_to_game")]
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
    if not Path(dog_image).is_file():
        logging.error(f"Dog image not found: {dog_image}")
        await callback_query.message.answer("Помилка: Зображення пса не знайдено.")
        return

    caption, keyboard = get_main_screen(user_data)

    with open(dog_image, "rb") as photo:
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

async def main():
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
