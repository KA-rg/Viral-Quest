# -----------------------
# Mock data for testing
# -----------------------
mock_posts = [
    {
        "id": "1",
        "shortcode": "ABC123",
        "caption": "Feeling pumped! #motivation #workout",
        "hashtags": ["motivation", "workout"],
        "likes": 120,
        "comments_count": 10,
        "is_video": True,
        "display_url": "https://example.com/image1.jpg",
        "video_url": "https://example.com/video1.mp4",
        "timestamp": "2025-09-21T10:00:00",
        "location": "Gym",
        "music_title": "Eye of the Tiger",
        "shares": 5,
        "saves": 15,
        "comments": [
            {"text": "Love this!", "owner": "user1"},
            {"text": "So motivating!", "owner": "user2"}
        ]
    },
    {
        "id": "2",
        "shortcode": "DEF456",
        "caption": "Just a funny moment #comedy #lol",
        "hashtags": ["comedy", "lol"],
        "likes": 200,
        "comments_count": 20,
        "is_video": False,
        "display_url": "https://example.com/image2.jpg",
        "video_url": None,
        "timestamp": "2025-09-20T15:30:00",
        "location": "Home",
        "music_title": None,
        "shares": 10,
        "saves": 25,
        "comments": [
            {"text": "Haha 😂", "owner": "user3"},
            {"text": "This made my day", "owner": "user4"}
        ]
    },
    {
        "id": "3",
        "shortcode": "GHI789",
        "caption": "Learn something new every day! #informative",
        "hashtags": ["informative"],
        "likes": 90,
        "comments_count": 5,
        "is_video": False,
        "display_url": "https://example.com/image3.jpg",
        "video_url": None,
        "timestamp": "2025-09-19T12:00:00",
        "location": None,
        "music_title": None,
        "shares": 2,
        "saves": 12,
        "comments": [
            {"text": "Thanks for sharing!", "owner": "user5"}
        ]
    },
    {
        "id": "4",
        "shortcode": "JKL012",
        "caption": "Just vibin' #brainrot",
        "hashtags": ["brainrot"],
        "likes": 50,
        "comments_count": 2,
        "is_video": True,
        "display_url": "https://example.com/image4.jpg",
        "video_url": "https://example.com/video2.mp4",
        "timestamp": "2025-09-18T18:45:00",
        "location": "Cafe",
        "music_title": "Lo-fi beats",
        "shares": 1,
        "saves": 5,
        "comments": [
            {"text": "Chill vibes!", "owner": "user6"}
        ]
    },
    {
        "id": "5",
        "shortcode": "MNO345",
        "caption": "Rise and grind! #motivation",
        "hashtags": ["motivation"],
        "likes": 300,
        "comments_count": 30,
        "is_video": True,
        "display_url": "https://example.com/image5.jpg",
        "video_url": "https://example.com/video3.mp4",
        "timestamp": "2025-09-17T06:00:00",
        "location": "Park",
        "music_title": "Happy Upbeat",
        "shares": 20,
        "saves": 50,
        "comments": [
            {"text": "Let's go!", "owner": "user7"},
            {"text": "Amazing!", "owner": "user8"}
        ]
    }
]

import os
import re
import csv
import tempfile
from datetime import datetime
from statistics import mean
from collections import Counter

import instaloader
from tqdm import tqdm
from transformers import pipeline

# Optional: for video meta
try:
    from moviepy.editor import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False

# -----------------------
# Config
# -----------------------
MAX_COMMENTS_PER_POST = 50
MOOD_LABELS = ["motivation", "comedy", "brainrot", "informative"]

# -----------------------
# Helpers
# -----------------------
def extract_hashtags(text):
    return re.findall(r"#(\w+)", text or "")

def init_pipelines():
    """Load ML models lazily."""
    global mood_pipeline, sentiment_pipeline
    if "mood_pipeline" not in globals():
        print("Loading transformers pipelines …")
        mood_pipeline = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli")
        sentiment_pipeline = pipeline("sentiment-analysis")

def classify_mood(text):
    if not text.strip():
        return None
    out = mood_pipeline(text, candidate_labels=MOOD_LABELS)
    return out["labels"][0]

def analyse_comment_tone(comments):
    """Return counts of sentiment labels."""
    if not comments:
        return {}
    texts = [c["text"] for c in comments if c["text"]]
    if not texts:
        return {}
    results = sentiment_pipeline(texts)
    counts = Counter(r["label"] for r in results)
    return dict(counts)

def download_and_get_video_meta(url):
    """Download a video temporarily and return duration, first-3s hook metric."""
    if not MOVIEPY_AVAILABLE or not url:
        return None, None
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    try:
        import requests
        r = requests.get(url, stream=True)
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                tmp.write(chunk)
        tmp.close()
        clip = VideoFileClip(tmp.name)
        duration = clip.duration
        # naive "hook performance" = ratio of first 3 s to total length
        hook_ratio = min(3, duration) / duration
        clip.close()
        return duration, hook_ratio
    except Exception:
        return None, None
    finally:
        try:
            os.remove(tmp.name)
        except OSError:
            pass

# -----------------------
# Instagram fetch
# -----------------------
def get_posts_instaloader(username, max_posts=20, login_user=None, login_pass=None):
    L = instaloader.Instaloader(download_videos=False,
                                save_metadata=False,
                                download_comments=False)
    if login_user and login_pass:
        L.login(login_user, login_pass)
    profile = instaloader.Profile.from_username(L.context, username)
    posts = []
    for i, post in enumerate(tqdm(profile.get_posts(), total=max_posts)):
        if i >= max_posts:
            break
        data = {
            "id": str(post.mediaid),
            "shortcode": post.shortcode,
            "caption": post.caption or "",
            "hashtags": extract_hashtags(post.caption or ""),
            "likes": post.likes,
            "comments_count": post.comments_count,
            "is_video": post.is_video,
            "display_url": post.url,
            "video_url": post.video_url if post.is_video else None,
            "timestamp": post.date_utc.isoformat(),
            # New fields
            "location": post.location.name if post.location else None,
            "music_title": None,   # Placeholder (needs Graph API)
            "shares": None,        # Placeholder (needs Graph API)
            "saves": None,         # Placeholder (needs Graph API)
        }
        comments = []
        try:
            for c in post.get_comments():
                comments.append({
                    "text": getattr(c, "text", ""),
                    "owner": getattr(getattr(c, "owner", None), "username", None)
                })
                if len(comments) >= MAX_COMMENTS_PER_POST:
                    break
        except Exception:
            pass
        data["comments"] = comments
        posts.append(data)
    return posts

# -----------------------
# Main analysis
# -----------------------
def analyse_posts(posts, csv_path):
    init_pipelines()
    rows = []
    for p in tqdm(posts, desc="Analysing"):
        mood = classify_mood(p["caption"])
        tone_counts = analyse_comment_tone(p["comments"])
        duration, hook_ratio = (None, None)
        if p["is_video"]:
            duration, hook_ratio = download_and_get_video_meta(p["video_url"])
        rows.append({
            "id": p["id"],
            "shortcode": p["shortcode"],
            "timestamp": p["timestamp"],
            "likes": p["likes"],
            "comments_count": p["comments_count"],
            "shares": p["shares"],
            "saves": p["saves"],
            "caption": p["caption"],
            "hashtags": ",".join(p["hashtags"]),
            "mood": mood,
            "comment_tone": tone_counts,
            "video_duration": duration,
            "hook_ratio_first3s": hook_ratio,
            "location": p["location"],
            "music_title": p["music_title"],
        })
    # write CSV
    keys = rows[0].keys()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return rows

def print_suggestions(rows):
    # Basic insights
    moods = [r["mood"] for r in rows if r["mood"]]
    most_common_mood = Counter(moods).most_common(1)
    hashtags = [h for r in rows for h in (r["hashtags"].split(",") if r["hashtags"] else [])]
    top_hashtags = [h for h, _ in Counter(hashtags).most_common(5)]
    avg_hook = mean([r["hook_ratio_first3s"] for r in rows if r["hook_ratio_first3s"]]) \
               if any(r["hook_ratio_first3s"] for r in rows) else None

    print("\n--- Suggestions ---")
    if most_common_mood:
        print(f"• Most frequent mood detected: {most_common_mood[0][0]}")
    if top_hashtags:
        print(f"• Top hashtags to refine around: {', '.join(top_hashtags)}")
    if avg_hook:
        print(f"• Average first-3-seconds hook ratio: {avg_hook:.2f}")
        if avg_hook < 0.2:
            print("  Consider stronger hooks or A/B thumbnails.")
    print("• Post when your audience is most active (use IG Insights to get actual active hours).")
    print("• Tailor colour palette & fonts to the dominant mood for stronger branding.")

# -----------------------
# Run
# -----------------------
if __name__ == "__main__":
    class Args:
        def __init__(self, username, max_posts=10, login_user=None, login_pass=None, out="ig_posts.csv"):
            self.username = username
            self.max_posts = max_posts
            self.login_user = login_user
            self.login_pass = login_pass
            self.out = out

    # Example: replace with your own account
    args = Args(username='instagram', max_posts=5)

    posts = get_posts_instaloader(args.username,
                                  max_posts=args.max_posts,
                                  login_user=args.login_user,
                                  login_pass=args.login_pass)
    rows = analyse_posts(posts, args.out)
    print(f"\nCSV saved to {args.out}")
    print_suggestions(rows)
