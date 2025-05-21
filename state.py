# === Media-related ===
media_cache = []  # Stores message_ids from @allmalltoi
media_likes = {}  # media_id: {"likes": set(), "dislikes": set()}
reported_media = []  # List of reported media IDs

# === User-related ===
user_bookmarks = {}  # user_id: [media_ids]
blocked_users = set()  # Set of user_ids
user_genders = {}  # user_id: 'boy' / 'girl' / 'unknown'
total_users = set()  # Track all unique users

# === Premium system ===
premium_users = {}  # user_id: datetime expiry
user_limits = {}    # user_id: {"count": int, "date": "YYYY-MM-DD"}
user_badges = {}    # user_id: str badge code

pending_premiums = {}  # user_id: {
                       #     "days": int,
                       #     "photo_id": str | None,
                       #     "utr": str | None,
                       #     "waiting": bool,
                       #     "confirmed": bool
                       # }

# === Tracking ===
last_message = {}  # user_id: message_id
