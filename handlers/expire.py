import asyncio
from datetime import datetime
from state import premium_users

async def auto_expire_premium():
    while True:
        now = datetime.now()
        expired = []

        for user_id, expiry in list(premium_users.items()):
            if expiry < now:
                expired.append(user_id)

        for user_id in expired:
            premium_users.pop(user_id, None)
            print(f"⏳ Premium expired for user {user_id}")

        await asyncio.sleep(10)  # Run every 10 seconds (adjustable)
