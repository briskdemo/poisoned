from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_file import FSInputFile
from state import pending_premiums, premium_users, user_badges
from config import ADMIN_ID
from datetime import datetime, timedelta
import random

router = Router()

# 1. Premium Intro and Plan Selection
@router.message(F.text == "/premium")
async def premium_intro(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_badges:
        badge = f"P#{random.randint(1000, 9999)}"
        user_badges[user_id] = badge
    else:
        badge = user_badges[user_id]

    text = (
        "💎 *Premium Plans*\n\n"
        "• 1 Day - ₹29\n"
        "• 7 Days - ₹49\n"
        "• 30 Days - ₹99\n\n"
        f"🎫 *Your Badge*: `{badge}`\n\n"
        "Choose a plan below to proceed 👇"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 Day - ₹29", callback_data="plan_1")],
        [InlineKeyboardButton(text="7 Days - ₹49", callback_data="plan_7")],
        [InlineKeyboardButton(text="30 Days - ₹99", callback_data="plan_30")],
    ])
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)


# 2. Handle Plan Selection and Send QR Code for Payment
@router.callback_query(F.data.startswith("plan_"))
async def handle_plan_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    plan_days = int(callback.data.split("_")[1])

    qr = FSInputFile("data/qr.jpg")  # Your QR path
    await callback.message.answer_photo(
        photo=qr,
        caption=(
            f"💰 Please pay for {plan_days} day(s) of Premium.\n"
            "📸 After payment, send the screenshot here to activate."
        )
    )

    pending_premiums[user_id] = plan_days  # ✅ FIXED: Track user is now pending approval
    await callback.answer()


# 3. Handle Screenshot Upload and Activate Premium
@router.message(F.photo)
async def handle_screenshot(message: types.Message):
    user_id = message.from_user.id

    if user_id not in pending_premiums:
        return  # Ignore unrelated photos

    days = pending_premiums.pop(user_id)
    expires_at = datetime.now() + timedelta(days=days)
    premium_users[user_id] = expires_at

    await message.answer(
        f"✅ Premium activated for {days} day(s)!\n"
        f"🎟️ Valid until: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        f"🆕 Premium approved for user: {message.from_user.mention_html()} ({user_id})\n"
        f"Duration: {days} days.",
        parse_mode="HTML"
    )
