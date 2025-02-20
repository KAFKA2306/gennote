import os
from datetime import datetime
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv('M:/ML/ChatGPT/gennote/.env')

# 基本設定
BASE_CONFIG = {
    'api_key': os.getenv('PerplexityAPI_KEY'),
    'api_url': "https://api.perplexity.ai/chat/completions",
    'base_path': 'M:/ML/ChatGPT/gennote/test',
    'model': "sonar-reasoning-pro"
}

# レート制限設定
RATE_LIMIT_CONFIG = {
    'rate_limit': 10,
    'time_window': 60,
    'retry_config': {
        'max_retries': 3,
        'backoff_factor': 1.5,
        'retry_delay': 2
    }
}

# キャッシュ設定
CACHE_CONFIG = {
    'duration': 3600
}

# ブログ投稿設定
BLOG_CONFIG = {
    'hatena': {
        'id': os.getenv('HATENA_ID'),
        'api_key': os.getenv('HATENA_API_KEY'),
        'domain': 'kafkafinancialgroup.hatenablog.com'
    }
}

# 検索ドメイン設定
SEARCH_DOMAINS = {
    'jp_market': {
        'primary': {
            'domains': ["jpx.co.jp", "nikkei.com", "bloomberg.co.jp"],
            'weight': 2.0
        },
        'secondary': {
            'domains': ["reuters.co.jp", "quick.co.jp", "minkabu.jp"],
            'weight': 1.0
        }
    },
    'china_market': [
        "etnet.com.hk",
        "yahoo.com",
        "aastocks.com",
        "hsbc.com.hk",
        "bochk.com",
        "hangseng.com",
        "tradingview.com",
        "investing.com",
        "coinmarketcap.com"
    ],
    'booth': ["booth.pm"]
}

def get_file_paths(type='default'):
    """ファイルパスを取得する共通関数"""
    today_date = datetime.now().strftime('%Y-%m-%d')
    return {
        'input': f'{BASE_CONFIG["base_path"]}/input/{today_date}.txt',
        'output': f'{BASE_CONFIG["base_path"]}/output/{today_date}.md'
    }

# 既存の設定に追加
POST_CONFIG = {
    'hatena': {
        'endpoint_template': 'https://blog.hatena.ne.jp/{}/{}}/atom/entry',
        'content_type': 'application/xml',
        'entry_template': '''
            <?xml version="1.0" encoding="utf-8"?>
            
            
            金融AIレポート {{}}
            {{}}
            {{}}
            {{}}
            no
            
            '''
    }
}

PROMPT_CONFIG = {
    'default_model': "llama-3.1-sonar-small-128k-online",
    'csv_path': 'M:/ML/ChatGPT/gennote/test/input/prompts.csv'
}
