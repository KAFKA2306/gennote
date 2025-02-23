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
    'booth': ["booth.pm"],

# 更新後のSEARCH_DOMAINS設定

    # 国際機関・マクロデータ
    'global_institutions': {
        'primary': {
            'domains': [
                "worldbank.org",       # 世界銀行 [2][5]
                "imf.org",             # 国際通貨基金 [2][5]
                "unctad.org",          # 国連貿易開発会議 [2]
                "un.org",              # 国連統計 [2][5]
                "bis.org",             # 国際決済銀行
                "oecd.org"             # OECD
            ],
            'weight': 2.0
        },
        'secondary': {
            'domains': [
                "fred.stlouisfed.org", # FRED経済データ [2]
                "bea.gov",             # 米国経済分析局 [2]
                "bls.gov",             # 米国労働統計局 [2]
                "ecb.europa.eu",       # 欧州中央銀行
                "boj.or.jp"            # 日本銀行
            ],
            'weight': 1.5
        }
    },


    # 金融市場データ
    'financial_markets': {
        'derivatives': {
            'domains': [
                "cmegroup.com",        # シカゴマーカンタイル取引所
                "eurex.com",            # ユーレクス
                "jpx.co.jp"            # 日本取引所グループ [既存設定を統合]
            ],
            'weight': 1.5
        },
        'equities': {
            'domains': [
                "nyse.com",            # NYSE
                "nasdaq.com",          # NASDAQ
                "lseg.com"             # ロンドン証券取引所 (LSEG) [4]
            ],
            'weight': 1.2
        }
    },
    
    # 商品・エネルギー市場
    'commodities': {
        'energy': {
            'domains': [
                "eia.gov",             # 米国エネルギー情報局 [3]
                "opec.org",            # OPEC
                "ice.com"              # インターコンチネンタル取引所
            ],
            'weight': 1.5
        },
        'metals': {
            'domains': [
                "lme.com",             # ロンドン金属取引所
                "comex.com",           # ニューヨーク商品取引所
                "gold.org"             # 世界黄金協会
            ],
            'weight': 1.2
        }
    },
    
    # 代替データソース
    'alternative_data': {
        'macro': {
            'domains': [
                "globalfinancialdata.com",  # GFD [4][6]
                "statista.com",        # Statista [3]
                "quandl.com",          # Nasdaq Data Link
                "tradingeconomics.com"
            ],
            'weight': 1.0
        },
        'sentiment': {
            'domains': [
                "tradingview.com",     # [既存設定を統合]
                "investing.com",       # [既存設定を統合]
                "hedgethink.com"       # マクロヘッジファンド分析
            ],
            'weight': 0.8
        }
    },
    
    # 地域別設定（既存設定を拡張）
    'jp_market': {
        'primary': {
            'domains': ["nikkei.com", "bloomberg.co.jp", "mof.go.jp"], # 財務省追加
            'weight': 2.0
        },
        'secondary': {
            'domains': ["reuters.co.jp", "quick.co.jp", "esri.cao.go.jp"], # 内閣府経済社会総合研究所追加
            'weight': 1.0
        }
    },
    
    'china_market': {
        'official': {
            'domains': [
                "stats.gov.cn",        # 中国国家統計局
                "pbc.gov.cn",          # 中国人民銀行
                "mofcom.gov.cn"        # 中国商務部
            ],
            'weight': 1.5
        },
        'commercial': {
            'domains': [
                "aastocks.com",        # [既存設定を統合]
                "etnet.com.hk",
                "sse.com.cn"           # 上海証券取引所
            ],
            'weight': 1.0
        }
    }





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
