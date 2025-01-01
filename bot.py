from aiogram import Bot, Dispatcher, executor, types
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN in .env")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users = {}

async def energy_recovery():
    while True:
        await asyncio.sleep(20)
        for user_id in users:
            users[user_id]["energy"] = min(5000, users[user_id]["energy"] + 5)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "energy": 5000,
            "level": 1
        }
    await message.reply("Welcome to Pies Coin Bot! 🐕\nCollect coins, level up, and have fun!")

@dp.message_handler(commands=['collect'])
async def collect_coins(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.reply("You are not registered. Use /start to begin!")
        return

    user_data = users[user_id]

    if user_data["energy"] <= 0:
        await message.reply("You are out of energy! Please wait for recovery.")
        return

    user_data["energy"] -= 10
    user_data["coins"] += 10
    await message.reply(f"💰 You collected 10 coins! Current coins: {user_data['coins']}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(energy_recovery())
    executor.start_polling(dp, skip_updates=True)
