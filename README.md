# Crypto News Aggregator (Enhanced)

This fork of the **Crypto News Aggregator** improves upon the original
project by adding two key features:

1. **Date Filtering** – Only stories published on the current day
   (based on the Asia/Jerusalem timezone) are included. This keeps the
   output focused on the most recent news.
2. **Clickable HTML List** – After scraping, an HTML page
   ([data/latest.html](data/latest.html)) is generated that lists all
   scraped headlines as links. Each headline is clickable and directs
   you to the original source. This makes it easy to browse the day’s
   news from a web browser.

The rest of the project remains the same: it monitors selected Twitter
accounts, Reddit subreddits, RSS feeds and GitHub repositories and
aggregates their updates into a unified feed.

## Sources

The scraper fetches updates from these sources:

* **Twitter** – a curated list of influential crypto voices such as
  Anthony Pompliano, Vitalik Buterin, CZ (Binance), Ivan on Tech,
  Marc Andreessen, Crypto Wendy O, Natalie Brunell, Erik Voorhees,
  Laura Shin and AltCoin Daily.
* **Reddit** – posts from crypto‑focused subreddits like
  r/CryptoCurrency, r/Bitcoin, r/Ethereum, r/CryptoMarkets, r/Dogecoin,
  r/Altcoin, r/DeFi, r/BitcoinBeginners, r/NFT and r/CryptoTechnology.
* **RSS feeds** – articles from news sites including CoinDesk, Decrypt,
  Bankless, BeInCrypto, The Block, Bitcoin Magazine, Blockworks and
  The Defiant.
* **Web3 magazines** – extended articles from sources such as Tech News 180,
  Cointelegraph Magazine and ShiftMag.
* **GitHub** – commits and releases from selected repositories
  (`0xjeffro/CryptoHub`, `ViktorVL584/Crypto-News-Aggregator`,
  `kukapay/crypto-rss-mcp`). GitHub data is fetched via
  [GitMCP](https://gitmcp.io), which helps avoid rate limits and API
  restrictions.

Results are normalized into a dictionary with `platform`, `source`,
`title`, `url`, `summary` and `published` fields, then filtered to
include only items from today.

## Repository Structure

```
crypto-news-aggregator/
├── scraper/                 # scraping code
│   ├── __init__.py
│   ├── config.py            # contains lists of sources
│   ├── crypto_news_scraper.py
│   └── storage.py           # saving utilities
├── data/
│   ├── latest.json          # latest scraped results (JSON)
│   └── latest.html          # latest scraped results as an HTML list
├── .github/workflows/
│   └── run_scraper.yml      # GitHub Actions workflow (manual dispatch)
├── requirements.txt         # python dependencies
└── README.md                # this file
```

## Setup

1. Clone the repository locally.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set the following environment variables required by the scraper:

   * `TWITTER_BEARER_TOKEN` – Twitter API Bearer Token.
   * `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` – credentials for the
     Reddit API (PRAW).
   * `REDDIT_USER_AGENT` – a user agent string to identify your script.
   * `GITHUB_TOKEN` – GitHub token for accessing repository data (optional; used for
     authenticated requests to GitMCP).

   These variables can be exported in your shell or stored in a `.env` file.

4. Run the scraper manually:

   ```bash
   python -m scraper.crypto_news_scraper
   ```

   The script will write the latest aggregated data to
   `data/latest.json` and generate a clickable list at
   [data/latest.html](data/latest.html). The HTML file shows only
   today’s news and makes it easy to click through to the original
   sources.

## Continuous scraping via GitHub Actions

The repository includes a GitHub Actions workflow that can execute the
scraper manually. The cron schedule has been disabled so it will not
run automatically without your approval. To trigger the workflow:

1. Add your secrets to the repository’s **Settings → Secrets and
   variables → Actions** section:

   * `TWITTER_BEARER_TOKEN`
   * `REDDIT_CLIENT_ID`
   * `REDDIT_CLIENT_SECRET`
   * `GITHUB_TOKEN` (you can use the default `GITHUB_TOKEN` or your own
     personal access token)

2. Visit the **Actions** tab in GitHub and click **Run workflow**.

After running, the workflow will push updated results to
`data/latest.json` and `data/latest.html` if there are changes.

## License

This project is provided for educational purposes. Use responsibly.