from datetime import datetime
import os
import requests
from dotenv import load_dotenv

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
    BOOTHの新着3D衣装を以下の手順で検索・紹介してください：

    検索条件：
    - サイト: BOOTH
    - カテゴリ: 3D衣装
    

    出力形式：
    各商品は以下の形式で記載してください：

    ## 商品名
    - 🔗 商品ページ: https://booth.pm/ja/items/【商品ID】
    - 💰 価格: 【価格】円
    - 🎨 クリエイター: 【ショップ名】
    - ✨ 商品の特徴:
    【商品の魅力を3行程度で説明】

    必須要件：
    1. 新着5商品を厳選
    2. 各商品に対応したIDを必ず数字で記載
    3. VRChat向けの衣装のみ選定

    禁止事項：
    - 商品IDの省略
    - 商品IDと商品タイトルの中身の不一致

    """

        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "search_domain_filter": ["booth.pm"],
            "return_citations": True  ,
            "search_recency_filter": "week",
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

if __name__ == "__main__":
    main()

import post_booth
# post_booth()
