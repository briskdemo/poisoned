import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from config import BOT_TOKEN, bot_properties, MEDIA_GROUP_ID
from handlers import start, media_flow, bookmarks, buttons, admin, report, broadcast, premium
from state import media_cache, media_likes

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=bot_properties)
dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(media_flow.router)
dp.include_router(bookmarks.router)
dp.include_router(buttons.router)
dp.include_router(admin.router)
dp.include_router(report.router)
dp.include_router(broadcast.router)
dp.include_router(premium.router)

# ✅ Cache media from @allmalltoi silently
@dp.message(F.photo | F.video | F.audio | F.document | F.voice)
async def cache_media_from_group(message: types.Message):
    if message.chat.id == MEDIA_GROUP_ID:
        media_cache.append(message.message_id)
        media_likes[len(media_cache) - 1] = {"likes": set(), "dislikes": set()}
        if len(media_cache) > 100:
            media_cache.pop(0)

async def main():
    logger.info("✅ Bot is starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Bot failed to start: {e}")

if __name__ == "__main__":
    asyncio.run(main())
