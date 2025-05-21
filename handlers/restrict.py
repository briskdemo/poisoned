from aiogram.types import Message
from datetime import datetime
from state import premium_users

async def is_premium(message: Message) -> bool:
    user_id = message.from_user.id
    now = datetime.now()

    if user_id not in premium_users:
        await message.answer(
            "🚫 This feature is only available to Premium users.\n\n"
            "👉 Use /premium to upgrade now."
        )
        return False

    expiry = premium_users[user_id]
    if expiry < now:
        await message.answer(
            "⚠️ Your Premium access has expired.\n\n"
            "🔄 Use /premium to renew it."
        )
        return False

    return True
