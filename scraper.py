import praw
from datetime import datetime
import pandas as pd
import time
import re
from langdetect import detect, LangDetectException

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT"),
    read_only=True
)

target_subreddits = [
    
    # Company-specific subreddits
    "GenZ",
    "teenagers",
    "youngadults"
    
]

def clean_text(text):
    """Clean and standardize text content"""
    if not text:
        return ""
    # Remove special characters and emojis
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_reddit_posts(post_limit_per_subreddit):
    posts_data = []
    
    for subreddit_name in target_subreddits:
        print(f"Fetching {post_limit_per_subreddit} posts from r/{subreddit_name}...")
        subreddit = reddit.subreddit(subreddit_name)
        
        for post in subreddit.new(limit=post_limit_per_subreddit):
            try:
                cleaned_title = clean_text(post.title)
                cleaned_content = clean_text(post.selftext)
                combined_text = f"{cleaned_title} {cleaned_content}"
                
                # Check if the post is in English
                try:
                    if detect(combined_text) != 'en':
                        print(f"Skipping non-English post: {post.title[:50]}...")
                        continue
                except LangDetectException:
                    print(f"Language detection failed for post: {post.title[:50]}...")
                    continue
                
                # Collect post data
                post_data = {
                    'subreddit': subreddit_name,
                    'date': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                    'title': cleaned_title,
                    'content': cleaned_content,
                    'url': post.url,
                    'score': post.score
                }
                posts_data.append(post_data)
                print(f"Retrieved post: {post.title[:50]}...")

            except Exception as e:
                print(f"Error processing post: {str(e)}")
                continue
        
        time.sleep(10)  # Delay to avoid Reddit API rate limiting
    
    df = pd.DataFrame(posts_data)
    print(f"Total posts retrieved: {len(df)}")
    return df

# Usage
df = scrape_reddit_posts(post_limit_per_subreddit=30000)  # Fetch 1000 posts per subreddit

# Save to CSV
df.to_csv('reddit_posts.csv', index=False)
