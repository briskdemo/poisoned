from aiogram import Router, types, F
from handlers.media_flow import send_hidden_forward
from state import media_cache, media_likes, user_bookmarks, user_limits, premium_users
from datetime import datetime
from handlers.restrict import is_premium
from config import JOIN_REQUIRED_GROUP

router = Router()

# ✅ Group join check
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

@router.callback_query(F.data.startswith(("like_", "dislike_", "prev_", "next_", "bookmark_", "download_")))
async def handle_buttons(callback: types.CallbackQuery):
    action, index = callback.data.split("_")
    index = int(index)
    user_id = callback.from_user.id
    bot = callback.message.bot

    # 🔒 Enforce join requirement
    if not await check_user_joined(bot, user_id):
        await callback.message.answer(
            "🚫 Please join our group to access media:\n"
            f"👉 <a href='https://t.me/{JOIN_REQUIRED_GROUP}'>Join @ppbackup01</a>",
            parse_mode="HTML"
        )
        await callback.answer()
        return

    if action == "like":
        media_likes[index]["likes"].add(user_id)
        media_likes[index]["dislikes"].discard(user_id)
        await send_hidden_forward(bot, user_id, index)
        await callback.answer("❤️ Liked!")

    elif action == "dislike":
        media_likes[index]["dislikes"].add(user_id)
        media_likes[index]["likes"].discard(user_id)
        await send_hidden_forward(bot, user_id, index)
        await callback.answer("💔 Disliked!")

    elif action == "prev":
        await send_hidden_forward(bot, user_id, index - 1)
        await callback.answer()

    elif action == "next":
        if not is_under_limit(user_id):
            await callback.answer()
            await callback.message.answer("🚫 You reached your daily media limit.\nUse /premium to unlock unlimited access.")
            return

        await send_hidden_forward(bot, user_id, index + 1)
        increment_usage(user_id)
        await callback.answer()

    elif action == "bookmark":
        file_id = media_cache[index][1]
        user_bookmarks.setdefault(user_id, []).append(file_id)
        await callback.answer("🔖 Bookmarked!")

    elif action == "download":
        if not await is_premium(callback.message):
            await callback.answer("🚫 Only Premium users can download.")
            return

        media_type, file_id = media_cache[index % len(media_cache)]
        try:
            if media_type == 'photo':
                await bot.send_photo(user_id, file_id, caption="✅ Tap and Save to Gallery!")
            elif media_type == 'video':
                await bot.send_video(user_id, file_id, caption="✅ Tap and Save to Gallery!")
            elif media_type == 'audio':
                await bot.send_audio(user_id, file_id, caption="✅ Tap and Save!")
            elif media_type == 'document':
                await bot.send_document(user_id, file_id, caption="✅ Tap and Save!")
            elif media_type == 'voice':
                await bot.send_voice(user_id, file_id, caption="✅ Tap and Save!")

            await callback.answer("📁 File Sent!")
        except Exception as e:
            print(f"❌ Error in download: {e}")
