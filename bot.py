from imaplib import Commands
from aiogram import Bot, Dispatcher, executor, types # type: ignore # type: ignore
import asyncio
import os
import subprocess
from dotenv import load_dotenv # type: ignore

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN", "7826649604:AAF7T4pSAAaf99ThPlfCDWSkkBPvXXBImhQ")

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Example user data structure
users = {}

async def energy_recovery():
    """Task for recovering energy every 100 seconds."""
    while True:
        await asyncio.sleep(100)
        for user_id in users:
            users[user_id]["energy"] = min(5000, users[user_id]["energy"] + 10)

@dp.message(Commands("..."))(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {
            "coins": 0,
            "energy": 5000,
            "level": 1,
            "feed_time": None,
            "nickname": message.from_user.first_name,
            "referrals": 0,
            "daily_reward": None
        }
    
    await message.reply("Welcome to Pies Coin Bot! \U0001F436\nCollect coins, level up, and have fun!")

@dp.message(Commands("..."))(commands=['stats'])
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.reply("You are not registered. Use /start to begin!")
        return

    user_data = users[user_id]
    stats = (
        f"\U0001F4CA Your Stats:\n"
        f"Nickname: {user_data['nickname']}\n"
        f"Coins: {user_data['coins']}\n"
        f"Energy: {user_data['energy']} / 5000\n"
        f"Level: {user_data['level']}\n"
        f"Referrals: {user_data['referrals']}\n"
    )
    await message.reply(stats)

@dp.message(Commands("..."))(commands=['collect'])
async def collect_coins(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users:
        await message.reply("You are not registered. Use /start to begin!")
        return

    user_data = users[user_id]

    if user_data["energy"] <= 0:
        await message.reply("You are out of energy! Please wait for recovery.")
        return

    # Deduct energy and add coins
    user_data["energy"] -= 10
    user_data["coins"] += 10
    await message.reply(f"\U0001F4B0 You collected 10 coins! Current coins: {user_data['coins']}")

@dp.message(Commands("..."))(commands=['update'])
async def update_repo(message: types.Message):
    """Command to update bot's code from GitHub repository."""
    try:
        # Run git pull command
        result = subprocess.run(["git", "pull"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            await message.reply(f"\U0001F680 Bot updated successfully!\n{result.stdout}")
        else:
            await message.reply(f"\U0001F6A8 Update failed:\n{result.stderr}")
    except Exception as e:
        await message.reply(f"\U0001F6A8 An error occurred:\n{str(e)}")

if __name__ == "__main__":
    # Start background tasks
    loop = asyncio.get_event_loop()
    loop.create_task(energy_recovery())

    # Start polling
    dp.start_polling(bot)(dp, skip_updates=True)
