from aiogram import Bot
from aiogram.enums import ChatMemberStatus
from config import GROUP_USERNAME, ADMIN_ID

async def is_user_member(bot: Bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=f"@{GROUP_USERNAME}", user_id=user_id)
        return member.status == ChatMemberStatus.MEMBER
    except:
        return False

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID
