import random
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from state import media_cache, last_message, user_limits, premium_users
from datetime import datetime
from config import JOIN_REQUIRED_GROUP, MEDIA_GROUP_ID
from utils.keyboard import generate_buttons

router = Router()

async def check_user_joined(bot, user_id):
    try:
        member = await bot.get_chat_member(f"@{JOIN_REQUIRED_GROUP}", user_id)
        return member.status in ("member", "administrator", "creator")
    except:
        return False

def is_under_limit(user_id: int) -> bool:
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    if user_id in premium_users and premium_users[user_id] > now:
        return True
    if user_id not in user_limits or user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"count": 0, "date": today}
    return user_limits[user_id]["count"] < 5

def increment_usage(user_id: int):
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    if user_id not in user_limits or user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"count": 1, "date": today}
    else:
        user_limits[user_id]["count"] += 1

async def send_hidden_forward(bot, user_id: int, message_id: int):
    try:
        if user_id in last_message:
            try:
                await bot.delete_message(chat_id=user_id, message_id=last_message[user_id])
            except:
                pass
        buttons = generate_buttons(message_id)
        msg = await bot.copy_message(
            chat_id=user_id,
            from_chat_id=MEDIA_GROUP_ID,
            message_id=message_id,
            reply_markup=buttons
        )
        last_message[user_id] = msg.message_id
        increment_usage(user_id)
    except Exception as e:
        print(f"❌ Failed to copy media: {e}")

@router.callback_query(F.data == "get_media")
async def handle_get_media(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    bot = callback.message.bot

    if not await check_user_joined(bot, user_id):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔗 Join Group", url=f"https://t.me/{JOIN_REQUIRED_GROUP}")],
            [InlineKeyboardButton(text="🔄 I've Joined", callback_data="get_media")]
        ])
        await callback.message.answer(
            "🚫 <b>Access Denied</b>\n\n"
            "You must join our group to access media:\n"
            f"👉 <a href='https://t.me/{JOIN_REQUIRED_GROUP}'>Join Now</a>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()
        return

    if not is_under_limit(user_id):
        await callback.answer()
        await callback.message.answer("🚫 You've reached your daily media limit.\n\nUse /premium to unlock unlimited access.")
        return

    if not media_cache:
        await callback.message.answer("❗ No media available yet!")
        return

    message_id = random.choice(media_cache)
    await send_hidden_forward(bot, user_id, message_id)
    await callback.answer()
