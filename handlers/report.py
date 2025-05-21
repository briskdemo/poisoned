from aiogram import Router, types, F
from config import ADMIN_ID
from state import media_cache, reported_media

router = Router()

@router.callback_query(F.data.startswith("report_"))
async def handle_report(callback: types.CallbackQuery):
    try:
        # Get the media index from the callback
        index = int(callback.data.split("_")[1])
        
        # Check if index is valid
        if index >= len(media_cache) or index < 0:
            await callback.answer("❌ Media no longer exists.")
            return

        # Retrieve the media type and file_id
        media_type, file_id = media_cache[index]

        # Avoid duplicate reports
        if file_id in reported_media:
            await callback.answer("⚠️ Already reported.")
            return

        # Save the report
        reported_media.append(file_id)

        # Send a report confirmation to the user
        await callback.answer("⚠️ Report sent to admin")

        # Create the report message with user info
        report_message = (
            f"⚠️ A user reported the following media (Index: {index}):\n"
            f"Media Type: {media_type}\n"
            f"File ID: <code>{file_id}</code>\n\n"
            f"Reported by: {callback.from_user.full_name} (@{callback.from_user.username})"
        )

        # Send the media to the admin
        if media_type == 'photo':
            await callback.bot.send_photo(ADMIN_ID, file_id, caption=report_message, parse_mode="HTML")
        elif media_type == 'video':
            await callback.bot.send_video(ADMIN_ID, file_id, caption=report_message, parse_mode="HTML")
        elif media_type == 'audio':
            await callback.bot.send_audio(ADMIN_ID, file_id, caption=report_message, parse_mode="HTML")
        elif media_type == 'document':
            await callback.bot.send_document(ADMIN_ID, file_id, caption=report_message, parse_mode="HTML")
        elif media_type == 'voice':
            await callback.bot.send_voice(ADMIN_ID, file_id, caption=report_message, parse_mode="HTML")

        print(f"✅ Report received for media {index} | File ID: {file_id}")
    
    except Exception as e:
        print(f"❌ Error in handle_report: {e}")
        await callback.answer("❌ Failed to report media.")
