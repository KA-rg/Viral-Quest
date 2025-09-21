import sys
import json
import re
from statistics import mean
from collections import Counter

USE_REAL = False  # Default: Mock Mode
try:
    import instaloader
    USE_REAL = True
except ImportError:
    USE_REAL = False

MOOD_LABELS = ["motivation", "comedy", "brainrot", "informative"]

# -----------------------
# Mock Data
# -----------------------
SAMPLE_POSTS = [
    {"caption": "Life is beautiful! #motivation #life", "hashtags": ["motivation","life"], "likes": 120, "comments_count": 10},
    {"caption": "Coding memes 😂 #comedy #coding", "hashtags": ["comedy","coding"], "likes": 150, "comments_count": 20},
    {"caption": "Learn something new every day! #informative #learning", "hashtags": ["informative","learning"], "likes": 200, "comments_count": 15},
    {"caption": "Just chilling #brainrot #fun", "hashtags": ["brainrot","fun"], "likes": 90, "comments_count": 5},
]

# -----------------------
# Helpers
# -----------------------
def classify_mood(text):
    """Return mood based on hashtags (mock)."""
    text_lower = text.lower()
    for mood in MOOD_LABELS:
        if mood in text_lower:
            return mood
    return "motivation"

def extract_hashtags(text):
    return re.findall(r"#(\w+)", text or "")

# -----------------------
# Fetch real posts
# -----------------------
def get_real_posts(username, max_posts=5):
    posts = []
    try:
        L = instaloader.Instaloader(download_videos=False, save_metadata=False, download_comments=False)
        profile = instaloader.Profile.from_username(L.context, username)
        for i, post in enumerate(profile.get_posts()):
            if i >= max_posts:
                break
            posts.append({
                "caption": post.caption or "",
                "hashtags": extract_hashtags(post.caption or ""),
                "likes": post.likes,
                "comments_count": post.comments_count
            })
    except Exception:
        return []  # Private or blocked
    return posts

# -----------------------
# Generate Suggestions
# -----------------------
def generate_suggestions(posts):
    if not posts:
        return {"message": "No posts found or account is private/non-existent."}

    captions = [p["caption"] for p in posts]
    all_hashtags = [h for p in posts for h in p["hashtags"]]
    likes = [p["likes"] for p in posts]
    comments = [p["comments_count"] for p in posts]

    moods = [classify_mood(c) for c in captions]
    most_common_mood = Counter(moods).most_common(1)[0][0] if moods else None
    top_hashtags = [h for h, _ in Counter(all_hashtags).most_common(5)]
    avg_likes = mean(likes) if likes else 0
    avg_comments = mean(comments) if comments else 0

    return {
        "most_common_mood": most_common_mood,
        "top_hashtags": top_hashtags,
        "average_likes": round(avg_likes,2),
        "average_comments": round(avg_comments,2)
    }

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    username = sys.argv[1] if len(sys.argv) > 1 else "demo_user"
    max_posts = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    mode = sys.argv[3] if len(sys.argv) > 3 else "mock"  # "mock" or "real"

    if mode == "real" and USE_REAL:
        posts = get_real_posts(username, max_posts)
    else:
        posts = SAMPLE_POSTS[:max_posts]

    suggestions = generate_suggestions(posts)
    print(json.dumps({"status": "success", "data": suggestions}))
