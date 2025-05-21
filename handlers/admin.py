from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMIN_ID
from state import (
    total_users, media_cache, media_likes,
    user_genders, blocked_users, reported_media,
    premium_users
)

router = Router()

@router.message(Command("admin"))
@router.callback_query(F.data == "admin_panel")
async def show_admin_panel(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(event, types.CallbackQuery):
            await event.answer("Access Denied!", show_alert=True)
        else:
            await event.answer("❌ You are not allowed.")
        return

    gender_count = {"boy": 0, "girl": 0, "unknown": 0}
    for g in user_genders.values():
        gender_count[g] += 1

    text = (
        "<b>👑 Admin Panel</b>\n\n"
        f"👥 Total Users: {len(total_users)}\n"
        f"📦 Media Cached: {len(media_cache)}\n"
        f"🆔 Premium Users: {len(premium_users)}\n"
        f"🚫 Blocked Users: {len(blocked_users)}\n"
        f"⚠️ Reported Media: {len(reported_media)}\n"
        f"🧑‍💼 Boys: {gender_count['boy']} | 👧 Girls: {gender_count['girl']} | ❓ Unknown: {gender_count['unknown']}\n"
    )

    buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="broadcast_start")],
        [InlineKeyboardButton(text="📋 View Reports", callback_data="view_reports")],
        [InlineKeyboardButton(text="💎 Premium Users", callback_data="view_premium")]
    ])

    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(text, reply_markup=buttons, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, reply_markup=buttons, parse_mode="HTML")
