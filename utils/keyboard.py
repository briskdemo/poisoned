from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BACKUP_GROUP_LINK
from state import media_likes

def generate_buttons(media_index: int) -> InlineKeyboardMarkup:
    likes = len(media_likes.get(media_index, {}).get("likes", []))
    dislikes = len(media_likes.get(media_index, {}).get("dislikes", []))

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f"👍 {likes}", callback_data=f"like_{media_index}"),
            InlineKeyboardButton(text=f"👎 {dislikes}", callback_data=f"dislike_{media_index}")
        ],
        [
            InlineKeyboardButton(text="⏪ Previous", callback_data=f"prev_{media_index}"),
            InlineKeyboardButton(text="⏩ Next", callback_data=f"next_{media_index}")
        ],
        [
            InlineKeyboardButton(text="🔖 Bookmark", callback_data=f"bookmark_{media_index}"),
            InlineKeyboardButton(text="📅 Download", callback_data=f"download_{media_index}")
        ],
        [
            InlineKeyboardButton(text="⚠️ Report", callback_data=f"report_{media_index}")
        ],
        [
            InlineKeyboardButton(text="🔗 Backup Group", url=BACKUP_GROUP_LINK)
        ]
    ])
