"""
Configuration for the crypto news scraper. Lists of sources to monitor.
"""

TWITTER_USERNAMES = [
    "APompliano",
    "VitalikButerin",
    "cz_binance",
    "IvanonTech",
    "pmarca",
    "CryptoWendyO",
    "natbrunell",
    "ErikVoorhees",
    "laurashin",
    "AltcoinDailyio",
]

SUBREDDITS = [
    "CryptoCurrency",
    "Bitcoin",
    "Ethereum",
    "CryptoMarkets",
    "dogecoin",
    "Altcoin",
    "DeFi",
    "BitcoinBeginners",
    "NFT",
    "CryptoTechnology",
]

RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Decrypt": "https://decrypt.co/feed",
    "Bankless": "https://www.bankless.com/feed",
    "BeInCrypto": "https://beincrypto.com/feed/",
    "The Block": "https://www.theblock.co/rss",
    "Bitcoin Magazine": "https://bitcoinmagazine.com/.rss/full/",
    "Blockworks": "https://blockworks.co/rss",
    "The Defiant": "https://thedefiant.io/feed",
    "TechNews180": "https://technews180.com/feed",
    "Cointelegraph Magazine": "https://cointelegraph.com/magazine/feed",
    "ShiftMag": "https://shiftmag.io/feed",
}

GITHUB_REPOS = [
    "0xjeffro/CryptoHub",
    "ViktorVL584/Crypto-News-Aggregator",
    "kukapay/crypto-rss-mcp",
]

MAX_ITEMS_PER_SOURCE = 5
