import os
from typing import Optional


def safe_filename(name: str) -> str:
    """Keep simple, remove http/https and bad chars for report filenames."""
    import re
    s = name.replace("http://", "").replace("https://", "")
    s = re.sub(r'[^A-Za-z0-9\-_.]', '_', s)
    return s


ALLOWED_AVATAR_EXTENSIONS = ("png", "jpg", "jpeg", "webp")


def find_user_avatar(static_folder: str, user_id: int) -> Optional[str]:
    """Return a static-relative path to the user's avatar if it exists.

    Files are stored as ``profile_pics/user_<id>.<ext>`` under the app's
    static folder. This function checks for any allowed extension.
    """
    base_dir = os.path.join(static_folder, "profile_pics")
    if not os.path.isdir(base_dir):
        return None

    for ext in ALLOWED_AVATAR_EXTENSIONS:
        candidate = os.path.join(base_dir, f"user_{user_id}.{ext}")
        if os.path.exists(candidate):
            # Return path relative to the static folder
            return f"profile_pics/user_{user_id}.{ext}"

    return None
