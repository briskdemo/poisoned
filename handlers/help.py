from aiogram import Router, types, F

router = Router()

@router.message(F.text == "/help")
async def show_help(message: types.Message):
    await message.answer("✅ /help command is working.")
