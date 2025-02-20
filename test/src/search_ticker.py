from datetime import datetime
import os
import requests
from dotenv import load_dotenv
import post

from config import BASE_CONFIG, get_file_paths
from utils import setup_logging, format_blog_content, remove_think_sections, convert_to_html
from rate_limiter import RateLimiter
from cache import ResponseCache

class FinancialDataProcessor:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        setup_logging()
        self.api_key = BASE_CONFIG['api_key']
        self.api_url = BASE_CONFIG['api_url']
        self.rate_limiter = RateLimiter()
        self.cache = ResponseCache()

    def get_file_paths(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        return {
            'input': f'M:/ML/ChatGPT/gennote/test/input/{today_date}.txt',
            'output': f'M:/ML/ChatGPT/gennote/test/output/{today_date}.md'
        }

    def create_api_request(self, today_date):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
本日{today_date}の市場データに基づき、$BABAの詳細な分析レポートを作成してください。

# 金融AIレポート {today_date}

## [基本情報](pplx://action/followup)
- ティッカーシンボル: BABA (NYSE)(https://finance.yahoo.com/quote/ticker/のリンク埋め込み)
- 企業名: アリババ・グループ・ホールディング
- 時価総額: 
- 株価: 

## [事業概要](pplx://action/followup)
- 主要事業セグメント
- 収益構造
- 最新の事業展開
- 注目のイニシアチブ

## [財務分析](pplx://action/followup)
- 直近四半期業績
  - 売上高と前年同期比
  - 営業利益と前年同期比
  - 純利益と前年同期比
  - フリーキャッシュフロー
- 主要財務指標
  - PER/PBR/PSR
  - 営業利益率
  - ROE/ROA

## [成長性分析](pplx://action/followup)
- 今後の成長戦略
- 市場予測
- リスク要因
- 投資機会

## [マクロ環境](pplx://action/followup)
- 中国経済動向
- 規制環境
- 業界動向
- 競合状況

## [テクニカル分析](pplx://action/followup)
- トレンド分析
  - 移動平均線（SMA50/200）
  - RSI（14日）
  - MACD
- ボラティリティ分析
  - ヒストリカルボラティリティ
  - ボリンジャーバンド
- サポート/レジスタンスレベル

## [比較分析](pplx://action/followup)
- 競合他社比較
  - Amazon (AMZN)
  - JD.com (JD)
  - PDD Holdings (PDD)
- 業界平均との比較
  - バリュエーション
  - 収益性
  - 成長性
"""


        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        return headers, payload

    def format_blog_content(self, content):
        return format_blog_content(content)

    def write_output_file(self, file_path, content):
        formatted_content = self.format_blog_content(content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

    def process_data(self):
        try:
            paths = self.get_file_paths()
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            headers, payload = self.create_api_request(today_date)
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")
            
            self.write_output_file(paths['output'], output_text)
            print(f'処理が完了しました。出力ファイル: {paths["output"]}')
            
        except requests.exceptions.RequestException as e:
            print(f"APIエラー: {str(e)}")
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")

def main():
    processor = FinancialDataProcessor()
    processor.process_data()
    post.main()

if __name__ == "__main__":
    main()
