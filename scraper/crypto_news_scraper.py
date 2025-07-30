import os
import requests
import feedparser
import praw
from datetime import datetime, timezone

from .config import TWITTER_USERNAMES, SUBREDDITS, RSS_FEEDS, GITHUB_REPOS, MAX_ITEMS_PER_SOURCE
from .storage import save_results


def fetch_twitter_posts(usernames, max_items=5, bearer_token=None):
    """Fetch recent tweets for each username using Twitter API v2."""
    results = []
    bearer_token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("Warning: TWITTER_BEARER_TOKEN not provided. Skipping Twitter scraping.")
        return results
    headers = {"Authorization": f"Bearer {bearer_token}"}
    for username in usernames:
        try:
            # Look up user ID
            user_resp = requests.get(
                f"https://api.twitter.com/2/users/by/username/{username}",
                headers=headers
            )
            if user_resp.status_code != 200:
                print(f"Failed to fetch user {username}: {user_resp.status_code} {user_resp.text}")
                continue
            user_id = user_resp.json()["data"]["id"]
            # Fetch user's tweets
            params = {"max_results": max_items, "tweet.fields": "created_at"}
            tweets_resp = requests.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets",
                headers=headers,
                params=params
            )
            if tweets_resp.status_code != 200:
                print(
                    f"Failed to fetch tweets for {username}: {tweets_resp.status_code} {tweets_resp.text}"
                )
                continue
            for tweet in tweets_resp.json().get("data", []):
                text = tweet.get("text", "")
                tweet_id = tweet.get("id")
                created_at = tweet.get("created_at")
                published = created_at or datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
                url = f"https://twitter.com/{username}/status/{tweet_id}"
                results.append({
                    "platform": "twitter",
                    "source": username,
                    "title": text[:100] if len(text) > 100 else text,
                    "url": url,
                    "summary": text,
                    "published": published
                })
        except Exception as e:
            print(f"Error fetching Twitter data for {username}: {e}")
    return results


def fetch_reddit_posts(subreddits, max_items=5, client_id=None, client_secret=None, user_agent=None):
    """Fetch recent posts from specified subreddits using PRAW."""
    results = []
    client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
    client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = user_agent or os.getenv("REDDIT_USER_AGENT", "crypto_news_scraper/0.1")
    if not client_id or not client_secret:
        print("Warning: Reddit API credentials not provided. Skipping Reddit scraping.")
        return results
    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
        return results
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.new(limit=max_items):
                title = submission.title
                summary = submission.selftext[:200] if submission.selftext else ""
                published = datetime.fromtimestamp(
                    submission.created_utc, tz=timezone.utc
                ).isoformat()
                results.append({
                    "platform": "reddit",
                    "source": f"r/{subreddit_name}",
                    "title": title,
                    "url": submission.url,
                    "summary": summary,
                    "published": published
                })
        except Exception as e:
            print(f"Error fetching Reddit data for r/{subreddit_name}: {e}")
    return results


def fetch_rss_feeds(feed_map, max_items=5):
    """Parse and collect entries from a dict of RSS feed URLs."""
    results = []
    for source_name, feed_url in feed_map.items():
        try:
            parsed = feedparser.parse(feed_url)
            entries = parsed.entries[:max_items]
            for entry in entries:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", "") or entry.get("description", "")
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                        published = dt.isoformat()
                    except Exception:
                        published = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
                else:
                    published = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
                results.append({
                    "platform": "rss",
                    "source": source_name,
                    "title": title,
                    "url": link,
                    "summary": summary,
                    "published": published
                })
        except Exception as e:
            print(f"Error fetching RSS feed {source_name}: {e}")
    return results


def fetch_github_updates(repos, max_items=5, token=None):
    """Fetch recent commits and releases from GitHub repositories."""
    results = []
    token = token or os.getenv("GITHUB_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"
    for repo_full in repos:
        try:
            owner, repo = repo_full.split("/")
        except ValueError:
            print(f"Invalid repo format: {repo_full}")
            continue
        # Commits
        try:
            commits_resp = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                headers=headers,
                params={"per_page": max_items}
            )
            if commits_resp.status_code == 200:
                for commit in commits_resp.json():
                    message = commit["commit"]["message"].split("\n")[0]
                    url = commit["html_url"]
                    published = commit["commit"]["author"]["date"]
                    results.append({
                        "platform": "github",
                        "source": repo_full,
                        "title": message,
                        "url": url,
                        "summary": message,
                        "published": published
                    })
            else:
                print(f"Failed to fetch commits for {repo_full}: {commits_resp.status_code} {commits_resp.text}")
        except Exception as e:
            print(f"Error fetching commits for {repo_full}: {e}")
        # Releases
        try:
            releases_resp = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/releases",
                headers=headers,
                params={"per_page": max_items}
            )
            if releases_resp.status_code == 200:
                for release in releases_resp.json()[:max_items]:
                    title = release.get("name") or release.get("tag_name")
                    published = release.get("published_at")
                    url = release.get("html_url")
                    body = release.get("body", "")
                    results.append({
                        "platform": "github",
                        "source": repo_full,
                        "title": title,
                        "url": url,
                        "summary": body[:200] if body else "",
                        "published": published
                    })
            else:
                print(f"Failed to fetch releases for {repo_full}: {releases_resp.status_code} {releases_resp.text}")
        except Exception as e:
            print(f"Error fetching releases for {repo_full}: {e}")
    return results


def main():
    """Run the scraper across all configured sources and save results."""
    results = []
    print("Starting crypto news scraper...")
    # Gather data from each platform
    results.extend(fetch_twitter_posts(TWITTER_USERNAMES, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_reddit_posts(SUBREDDITS, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_rss_feeds(RSS_FEEDS, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_github_updates(GITHUB_REPOS, MAX_ITEMS_PER_SOURCE))
    # Sort by published date descending
    def _parse_date(date_str):
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.utcnow().replace(tzinfo=timezone.utc)
    results.sort(key=lambda x: _parse_date(x["published"]), reverse=True)
    # Persist to disk
    save_results(results, output_dir="data", output_format="json")
    print(f"Scraping complete: {len(results)} items saved to data/latest.json")


if __name__ == "__main__":
    main()
