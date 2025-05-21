from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from datetime import datetime, timedelta
from config import ADMIN_ID
from state import pending_premiums, premium_users, user_badges
import random

router = Router()

# Step 1: Show Premium Plans
@router.message(F.text == "/premium")
async def premium_intro(message: types.Message):
    user_id = message.from_user.id
    badge = user_badges.setdefault(user_id, f"P#{random.randint(1000, 9999)}")

    text = (
        "💎 <b>Premium Plans</b>\n\n"
        "• 1 Day - ₹29\n"
        "• 7 Days - ₹49\n"
        "• 30 Days - ₹99\n\n"
        f"🎫 <b>Your Badge:</b> <code>{badge}</code>\n\n"
        "Choose a plan to continue:"
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="1 Day - ₹29", callback_data="plan_1")],
        [InlineKeyboardButton(text="7 Days - ₹49", callback_data="plan_7")],
        [InlineKeyboardButton(text="30 Days - ₹99", callback_data="plan_30")]
    ])
    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

# Step 2: User selects plan and receives QR + message
@router.callback_query(F.data.startswith("plan_"))
async def select_plan(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    days = int(callback.data.split("_")[1])
    pending_premiums[user_id] = {"days": days, "utr": None, "confirmed": False}

    caption = (
        f"💳 You selected {days} day(s) Premium.\n\n"
        "Please send your UTR / transaction ID (as plain text) for verification.\n\n"
        "Example: <code>TXN1234567890</code>"
    )

    qr = FSInputFile("img/qr.jpg")  # ✅ Ensure this file exists
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_premium")]
    ])

    await callback.message.answer_photo(
        photo=qr,
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    await callback.answer()

# Step 3: User sends UTR
@router.message(F.text)
async def receive_utr(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in pending_premiums:
        return

    if pending_premiums[user_id]["confirmed"]:
        return

    pending_premiums[user_id]["utr"] = text
    pending_premiums[user_id]["confirmed"] = True
    days = pending_premiums[user_id]["days"]
    badge = user_badges.get(user_id, "UNKNOWN")

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Deny", callback_data=f"deny_{user_id}")
        ]
    ])

    await message.bot.send_message(
        ADMIN_ID,
        f"📥 <b>Premium Request</b>\n"
        f"👤 User ID: <code>{user_id}</code>\n"
        f"🎫 Badge: <code>{badge}</code>\n"
        f"📅 Days: {days}\n"
        f"🧾 UTR: <code>{text}</code>",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    await message.answer("✅ Your payment info has been submitted. Please wait for admin approval.")

# Step 4: Cancel request
@router.callback_query(F.data == "cancel_premium")
async def cancel_request(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    pending_premiums.pop(user_id, None)
    await callback.message.answer("❌ Premium request canceled.")
    await callback.answer()

# Step 5: Admin Approves
@router.callback_query(F.data.startswith("approve_"))
async def approve(callback: types.CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[1])
        days = pending_premiums[user_id]["days"]
        expires_at = datetime.now() + timedelta(days=days)
        premium_users[user_id] = expires_at
        pending_premiums.pop(user_id, None)

        await callback.bot.send_message(
            user_id,
            f"🎉 Your Premium is activated for {days} day(s).\n"
            f"Valid until: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await callback.message.answer("✅ Approved and user notified.")
    except Exception as e:
        await callback.message.answer(f"❌ Error: {e}")
    await callback.answer()

# Step 6: Admin Denies
@router.callback_query(F.data.startswith("deny_"))
async def deny(callback: types.CallbackQuery):
    try:
        user_id = int(callback.data.split("_")[1])
        pending_premiums.pop(user_id, None)

        await callback.bot.send_message(user_id, "❌ Your premium request was denied.")
        await callback.message.answer("🚫 Request denied.")
    except Exception as e:
        await callback.message.answer(f"❌ Error: {e}")
    await callback.answer()
