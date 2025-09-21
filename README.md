# ByteSquad
# Instagram Post Analysis with AI/ML

Analyze Instagram posts to extract insights such as post mood, comment sentiment, hashtags, video performance, and engagement metrics using Python and the Instagram Graph API.


---
![Alt text]("main.png")
## Features

- Fetch posts from Instagram using **Instagram Graph API**.
- Extract post details: caption, hashtags, likes, comments, shares, saves, video URLs, and location.
- Analyze post **mood** using zero-shot classification.
- Analyze **comment sentiment** (positive, negative, neutral).
- Calculate video **duration** and **first-3-seconds hook ratio**.
- Export results to **CSV**.
- Provide **suggestions** based on the analysis (e.g., top hashtags, dominant mood, hook performance).

---

## Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/instagram-analysis.git
cd instagram-analysis 
```

2. **Create a virtual environment (optional but recommended)**
```bash
python -m venv venv
source venv/bin/activate       # Linux / macOS
venv\Scripts\activate          # Windows
```

3. **Install independecies**
```bash
pip install -r requirements.txt
```
requirment.txt must include
requests
tqdm
pandas
transformers
torch
moviepy

![Alt text]("main.png")




