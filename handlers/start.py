from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.checks import is_admin
from state import total_users, user_genders
from config import GROUP_USERNAME

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    total_users.add(user_id)

    # ✅ Prevent KeyError: set pending if new user
    if user_id not in user_genders:
        user_genders[user_id] = "pending"

    # ✅ Ask for gender if still pending
    if user_genders[user_id] == "pending":
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👦 Boy", callback_data="gender_boy"),
             InlineKeyboardButton(text="👧 Girl", callback_data="gender_girl")],
            [InlineKeyboardButton(text="❌ Skip", callback_data="gender_skip")]
        ])
        await message.answer("👋 Please select your gender:", reply_markup=keyboard)
        return

    # ✅ Buttons after gender is already set
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Get Media", callback_data="get_media")],
        [InlineKeyboardButton(text="🆘 Help", callback_data="show_help")]
    ])

    if is_admin(user_id):
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")]
        )

    await message.answer(
        "🎮 <b>Welcome to Media Bot!</b>\n\n"
        f"Join our group to access exclusive media:\n"
        f"👉 <a href='https://t.me/{GROUP_USERNAME}'>Click to Join</a>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("gender_"))
async def handle_gender_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    choice = callback.data.split("_")[1]
    user_genders[user_id] = choice if choice in ["boy", "girl"] else "unknown"
    await callback.answer("✅ Gender saved!")

    try:
        await callback.message.delete()
    except:
        pass

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Get Media", callback_data="get_media")],
        [InlineKeyboardButton(text="🆘 Help", callback_data="show_help")]
    ])

    if is_admin(user_id):
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text="⚙️ Admin Panel", callback_data="admin_panel")]
        )

    await callback.message.bot.send_message(
        chat_id=user_id,
        text=(
            "🎮 <b>Welcome to Media Bot!</b>\n\n"
            f"Join our group to access exclusive media:\n"
            f"👉 <a href='https://t.me/{GROUP_USERNAME}'>Click Here</a>"
        ),
        reply_markup=keyboard,
        parse_mode="HTML"
    )
