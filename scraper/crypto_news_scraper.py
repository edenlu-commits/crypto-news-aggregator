"""
Updated crypto news scraper.

This version adds the following enhancements:

* Filters scraped items to only include entries published on the current day
  in the Asia/Jerusalem timezone. This is determined by converting each
  item's ISO‐formatted ``published`` timestamp into the local timezone and
  comparing the date component to today's date.
* Generates a simple HTML file containing a list of clickable headlines. Each
  headline links to the original source of the news item. The HTML file is
  saved alongside the JSON output in the ``data`` directory.
* Uses the GitMCP service (``https://gitmcp.io``) when retrieving recent
  commits and releases from GitHub repositories. This helps avoid GitHub
  API limitations and transient errors.

Note: To keep the code self contained, we have not modified ``storage.py``.
Instead, the HTML output is generated directly in this module.
"""

import os
import html
import requests
import feedparser
import praw
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

from .config import (
    TWITTER_USERNAMES,
    SUBREDDITS,
    RSS_FEEDS,
    GITHUB_REPOS,
    MAX_ITEMS_PER_SOURCE,
)
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
                f"https://api.twitter.com/2/users/by/username/{username}", headers=headers
            )
            if user_resp.status_code != 200:
                print(
                    f"Failed to fetch user {username}: {user_resp.status_code} {user_resp.text}"
                )
                continue
            user_id = user_resp.json()["data"]["id"]
            # Fetch user's tweets
            params = {"max_results": max_items, "tweet.fields": "created_at"}
            tweets_resp = requests.get(
                f"https://api.twitter.com/2/users/{user_id}/tweets", headers=headers, params=params
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
                results.append(
                    {
                        "platform": "twitter",
                        "source": username,
                        "title": text[:100] if len(text) > 100 else text,
                        "url": url,
                        "summary": text,
                        "published": published,
                    }
                )
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
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    except Exception as e:
        print(f"Error initializing Reddit API: {e}")
        return results
    for subreddit_name in subreddits:
        try:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.new(limit=max_items):
                title = submission.title
                summary = submission.selftext[:200] if submission.selftext else ""
                published = datetime.fromtimestamp(submission.created_utc, tz=timezone.utc).isoformat()
                results.append(
                    {
                        "platform": "reddit",
                        "source": f"r/{subreddit_name}",
                        "title": title,
                        "url": submission.url,
                        "summary": summary,
                        "published": published,
                    }
                )
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
                results.append(
                    {
                        "platform": "rss",
                        "source": source_name,
                        "title": title,
                        "url": link,
                        "summary": summary,
                        "published": published,
                    }
                )
        except Exception as e:
            print(f"Error fetching RSS feed {source_name}: {e}")
    return results


def fetch_github_updates(repos, max_items=5, token=None):
    """Fetch recent commits and releases from GitHub repositories via GitMCP."""
    results = []
    # Use the GitHub token for authenticated requests if provided
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
            commits_url = f"https://gitmcp.io/{owner}/{repo}/commits"
            commits_resp = requests.get(commits_url, headers=headers, params={"per_page": max_items})
            if commits_resp.status_code == 200:
                # Attempt to parse JSON; if GitMCP returns HTML, skip parsing
                try:
                    commits_json = commits_resp.json()
                except Exception:
                    print(f"GitMCP returned non‑JSON for commits at {repo_full}. Skipping commit parsing.")
                    commits_json = []
                for commit in commits_json:
                    message = commit.get("commit", {}).get("message", "").split("\n")[0]
                    url = commit.get("html_url") or commit.get("url")
                    published = (
                        commit.get("commit", {}).get("author", {}).get("date")
                        or datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
                    )
                    if not message:
                        continue
                    results.append(
                        {
                            "platform": "github",
                            "source": repo_full,
                            "title": message,
                            "url": url,
                            "summary": message,
                            "published": published,
                        }
                    )
            else:
                print(
                    f"Failed to fetch commits for {repo_full} from GitMCP: {commits_resp.status_code} {commits_resp.text}"
                )
        except Exception as e:
            print(f"Error fetching commits for {repo_full}: {e}")
        # Releases
        try:
            releases_url = f"https://gitmcp.io/{owner}/{repo}/releases"
            releases_resp = requests.get(releases_url, headers=headers, params={"per_page": max_items})
            if releases_resp.status_code == 200:
                try:
                    releases_json = releases_resp.json()
                except Exception:
                    print(f"GitMCP returned non‑JSON for releases at {repo_full}. Skipping release parsing.")
                    releases_json = []
                for release in releases_json[:max_items]:
                    title = release.get("name") or release.get("tag_name")
                    published = release.get("published_at") or datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
                    url = release.get("html_url") or release.get("url")
                    body = release.get("body", "")
                    if not title:
                        continue
                    results.append(
                        {
                            "platform": "github",
                            "source": repo_full,
                            "title": title,
                            "url": url,
                            "summary": body[:200] if body else "",
                            "published": published,
                        }
                    )
            else:
                print(
                    f"Failed to fetch releases for {repo_full} from GitMCP: {releases_resp.status_code} {releases_resp.text}"
                )
        except Exception as e:
            print(f"Error fetching releases for {repo_full}: {e}")
    return results


def filter_today(results, tz_name="Asia/Jerusalem"):
    """Filter results to include only items published on today's date in the given timezone."""
    today = datetime.now(ZoneInfo(tz_name)).date()
    filtered = []
    for item in results:
        date_str = item.get("published") or ""
        try:
            # Replace trailing Z with +00:00 for fromisoformat
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        try:
            local_dt = dt.astimezone(ZoneInfo(tz_name))
        except Exception:
            local_dt = dt
        if local_dt.date() == today:
            filtered.append(item)
    return filtered


def generate_html(results, output_dir="data", file_name="latest.html", tz_name="Asia/Jerusalem"):
    """Generate an HTML file listing all news items with clickable headlines."""
    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(output_dir) / file_name
    today_str = datetime.now(ZoneInfo(tz_name)).strftime("%Y-%m-%d")
    with file_path.open("w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'><title>Crypto News</title></head><body>\n")
        f.write(f"<h1>Crypto News for {today_str}</h1>\n")
        f.write("<ul>\n")
        for item in results:
            title = html.escape(item.get("title", ""))
            url = item.get("url", "#")
            platform = html.escape(item.get("platform", ""))
            source = html.escape(item.get("source", ""))
            f.write(
                f"  <li><a href='{url}' target='_blank'>{title}</a> - {platform} ({source})</li>\n"
            )
        f.write("</ul>\n")
        f.write("</body></html>\n")
    return str(file_path)


def main():
    """Run the scraper across all configured sources and save results."""
    results = []
    print("Starting crypto news scraper...")
    # Gather data from each platform
    results.extend(fetch_twitter_posts(TWITTER_USERNAMES, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_reddit_posts(SUBREDDITS, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_rss_feeds(RSS_FEEDS, MAX_ITEMS_PER_SOURCE))
    results.extend(fetch_github_updates(GITHUB_REPOS, MAX_ITEMS_PER_SOURCE))
    # Filter to today's items
    results = filter_today(results, tz_name="Asia/Jerusalem")
    # Sort by published date descending
    def _parse_date(date_str):
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception:
            return datetime.utcnow().replace(tzinfo=timezone.utc)
    results.sort(key=lambda x: _parse_date(x.get("published", "")), reverse=True)
    # Persist JSON to disk
    save_results(results, output_dir="data", output_format="json")
    # Generate HTML list
    html_path = generate_html(results, output_dir="data", file_name="latest.html")
    print(f"Scraping complete: {len(results)} items saved to data/latest.json")
    print(f"HTML list generated at {html_path}")


if __name__ == "__main__":
    main()