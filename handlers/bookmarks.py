from aiogram import Router, types
from aiogram.filters import Command
from state import user_bookmarks

router = Router()

@router.message(Command("bookmarks"))
async def show_bookmarks(message: types.Message):
    user_id = message.from_user.id
    bookmarks = user_bookmarks.get(user_id, [])

    if not bookmarks:
        await message.answer("🔖 You don't have any bookmarks yet.")
        return

    await message.answer(f"🔖 You have {len(bookmarks)} bookmarked media.")

    for i in range(0, len(bookmarks), 5):
        for file_id in bookmarks[i:i+5]:
            try:
                await message.bot.send_document(user_id, file_id)
            except:
                try:
                    await message.bot.send_photo(user_id, file_id)
                except:
                    pass
        if i + 5 < len(bookmarks):
            await message.answer("⏩ More bookmarks...")
