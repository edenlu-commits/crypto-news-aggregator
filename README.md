# Crypto News Aggregator

This project provides a simple Python-based scraper that monitors top cryptocurrency social and news sources and aggregates the latest updates into a unified JSON feed. The scraper collects data from Twitter accounts, Reddit subreddits, RSS feeds from Web3 news sites and notable GitHub repositories, normalizes the information into a consistent format, and saves the results to `data/latest.json`.

## Sources

The scraper fetches updates from these sources:

- **Twitter**: a curated list of influential crypto voices such as Anthony Pompliano, Vitalik Buterin, CZ (Binance), Ivan on Tech, Marc Andreessen, Crypto Wendy O, Natalie Brunell, Erik Voorhees, Laura Shin and AltCoin Daily.
- **Reddit**: posts from crypto-focused subreddits like r/CryptoCurrency, r/Bitcoin, r/Ethereum, r/CryptoMarkets, r/Dogecoin, r/Altcoin, r/DeFi, r/BitcoinBeginners, r/NFT and r/CryptoTechnology.
- **RSS feeds**: articles from news sites including CoinDesk, Decrypt, Bankless, BeInCrypto, The Block, Bitcoin Magazine, Blockworks and The Defiant.
- **Web3 magazines**: extended articles from sources such as Tech News 180, Cointelegraph Magazine and ShiftMag.
- **GitHub**: commits and releases from selected repositories (`0xjeffro/CryptoHub`, `ViktorVL584/Crypto-News-Aggregator`, `kukapay/crypto-rss-mcp`).

Results are normalized into a dictionary with `platform`, `source`, `title`, `url`, `summary` and `published` fields.

## Repository Structure

```
crypto-news-aggregator/
├── scraper/                 # scraping code
│   ├── __init__.py
│   ├── config.py            # contains lists of sources
│   ├── crypto_news_scraper.py
│   └── storage.py           # saving utilities
├── data/
│   └── latest.json          # latest scraped results
├── .github/workflows/
│   └── run_scraper.yml      # GitHub Actions workflow
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

   - `TWITTER_BEARER_TOKEN` – Twitter API Bearer Token.
   - `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` – credentials for Reddit API (PRAW).
   - `REDDIT_USER_AGENT` – a user agent string to identify your script.
   - `GITHUB_TOKEN` – GitHub token for accessing repository data.

   These variables can be exported in your shell or stored in a `.env` file.

4. Run the scraper manually:

   ```bash
   python scraper/crypto_news_scraper.py
   ```

   The script will write the latest aggregated data to `data/latest.json` and optionally to `data/latest.csv`.

## Continuous scraping via GitHub Actions

The repository includes a GitHub Actions workflow that executes the scraper every 30 minutes. To enable automatic scraping:

1. Add your secrets to the repository's **Settings → Secrets and variables → Actions** section:

   - `TWITTER_BEARER_TOKEN`
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `GITHUB_TOKEN` (you can use the default `GITHUB_TOKEN` or your own personal access token)

2. Commit any additional changes to trigger the workflow. The workflow will run on schedule and push updated results to `data/latest.json`.

## License

This project is provided for educational purposes. Use responsibly.
