from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from config import ADMIN_ID
from state import total_users
from aiogram.fsm.state import State, StatesGroup

router = Router()

class BroadcastState(StatesGroup):
    waiting_for_content = State()
    preview_message = State()

# === Start broadcast ===
@router.message(Command("broadcast"))
@router.callback_query(F.data == "broadcast_start")
async def start_broadcast(event: types.Message | types.CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    if user_id != ADMIN_ID:
        if isinstance(event, types.CallbackQuery):
            await event.answer("Access Denied", show_alert=True)
        else:
            await event.answer("❌ Not allowed.")
        return

    await state.set_state(BroadcastState.waiting_for_content)

    prompt = "📢 Please send the content you want to broadcast (text, photo, video, etc.)."
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text(prompt)
        await event.answer()
    else:
        await event.answer(prompt)

# === Receive content ===
@router.message(BroadcastState.waiting_for_content)
async def preview_broadcast(message: types.Message, state: FSMContext):
    await state.update_data(content=message)
    await state.set_state(BroadcastState.preview_message)

    preview_buttons = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Confirm", callback_data="broadcast_confirm")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data="broadcast_cancel")]
    ])

    await message.answer("🧾 Preview your message:", reply_markup=preview_buttons)

    try:
        if message.photo:
            await message.bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=message.caption or "")
        elif message.video:
            await message.bot.send_video(ADMIN_ID, message.video.file_id, caption=message.caption or "")
        elif message.text:
            await message.bot.send_message(ADMIN_ID, message.text)
        elif message.document:
            await message.bot.send_document(ADMIN_ID, message.document.file_id, caption=message.caption or "")
        elif message.audio:
            await message.bot.send_audio(ADMIN_ID, message.audio.file_id, caption=message.caption or "")
        else:
            await message.answer("❌ Unsupported media type.")
            await state.clear()
    except Exception as e:
        await message.answer(f"❌ Failed to preview: {e}")
        await state.clear()

# === Confirm broadcast ===
@router.callback_query(F.data == "broadcast_confirm")
async def send_broadcast(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    content = data.get("content")

    sent = 0
    failed = 0

    await callback.message.edit_text("📤 Sending broadcast...")

    for user_id in total_users.copy():
        try:
            if content.text:
                await callback.bot.send_message(user_id, content.text)
            elif content.photo:
                await callback.bot.send_photo(user_id, content.photo[-1].file_id, caption=content.caption or "")
            elif content.video:
                await callback.bot.send_video(user_id, content.video.file_id, caption=content.caption or "")
            elif content.document:
                await callback.bot.send_document(user_id, content.document.file_id, caption=content.caption or "")
            elif content.audio:
                await callback.bot.send_audio(user_id, content.audio.file_id, caption=content.caption or "")
            sent += 1
        except:
            failed += 1

    await callback.message.edit_text(
        f"✅ Broadcast complete!\n\n📤 Sent: {sent}\n❌ Failed: {failed}"
    )
    await state.clear()

# === Cancel broadcast ===
@router.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Broadcast cancelled.")
    await callback.answer()
