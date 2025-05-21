from aiogram import Router, types, F
from datetime import datetime
from state import premium_users

router = Router()

@router.message(F.text == "/checkpremium")
async def check_premium(message: types.Message):
    user_id = message.from_user.id
    now = datetime.now()

    if user_id not in premium_users:
        await message.answer("❌ You are not a Premium user.")
        return

    expiry = premium_users[user_id]
    if expiry < now:
        await message.answer("⚠️ Your Premium has expired.")
        return

    remaining = expiry - now
    days = remaining.days
    hours = remaining.seconds // 3600

    await message.answer(
        f"✅ You are a Premium user!\n"
        f"⏳ Expires on: <code>{expiry.strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"🕓 Time left: {days}d {hours}h",
        parse_mode="HTML"
    )
