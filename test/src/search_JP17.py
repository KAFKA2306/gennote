from datetime import datetime
import os
import time
import requests
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Optional

from config import BASE_CONFIG, get_file_paths, SEARCH_DOMAINS
from utils import setup_logging, format_blog_content, remove_think_sections, convert_to_html
from rate_limiter import RateLimiter
from cache import ResponseCache

class JapanSectorAnalyzer:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        setup_logging('sector_analysis.log')
        
        self.api_key = BASE_CONFIG['api_key']
        self.api_url = BASE_CONFIG['api_url']
        
        self.search_domains = SEARCH_DOMAINS['jp_market']
        
        self.rate_limiter = RateLimiter()
        self.cache = ResponseCache()
        
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 1.5,
            'retry_delay': 2
        }

    def get_weighted_domains(self) -> list:
        weighted_domains = []
        for tier in self.search_domains.values():
            if 'domains' in tier:
                weighted_domains.extend(tier['domains'])
        return weighted_domains

    def create_prompt(self, today_date: str) -> str:
        return f"""
# 日本株式市場セクター調査 {today_date}

以下の8セクターについて、年初来の動向を明瞭かつ具体的に引用してください：

## セクター別動向
1. 情報通信
2. 電気機器
3. 機械
4. 化学
5. 銀行業
6. 不動産業
7. 保険業
8. 精密機器

## 4. 投資判断
- 強気セクターとその理由
- 警戒セクターとその理由
- 短期的な投資機会

注意：
- すべての数値は具体的な値で記載
- 全ての銘柄はhttps://kabutan.jp/stock/finance?code=[code] でリンクを付けること
- 数値根拠の明確な記載が必要
- 情報ソースを明記する
"""

    def create_api_request(self, today_date: str) -> tuple:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": self.create_prompt(today_date)
            }],
            "search_domain_filter": self.get_weighted_domains(),
            "search_recency_filter": "week",
            "temperature": 0,
            "presence_penalty": -0.5
        }
        
        return headers, payload

    def format_sector_report(self, content: str) -> str:
        formatted = content.replace('# ', '*').replace('## ', '**')
        formatted = formatted.replace('- ', ':').replace('：', ':')
        return formatted

    def write_sector_report(self, file_path: str, content: str):
        formatted_content = self.format_sector_report(content)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

    def make_api_request(self, headers: Dict, payload: Dict) -> requests.Response:
        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response

    def process_response(self, response: requests.Response) -> str:
        result = response.json()
        analysis_text = result.get("choices", [{}])[0].get("message", {}).get("content", "分析データを取得できませんでした")
        market_data = result.get("choices", [{}])[0].get("message", {}).get("citations", [])
        
        if market_data:
            analysis_text += "\n\n## データソース\n"
            for source in market_data:
                analysis_text += f"- {source['title']}: {source['url']}\n"
        
        return analysis_text

    def handle_error(self, error: Exception):
        logging.error(f"エラーが発生しました: {str(error)}")
        raise error

    def analyze_sectors(self):
        try:
            today_date = datetime.now().strftime('%Y-%m-%d')
            cache_key = f"sector_analysis_{today_date}"
            
            # キャッシュチェック
            cached_result = self.cache.get(cache_key)
            if cached_result:
                return cached_result

            output_path = f'M:/ML/ChatGPT/gennote/test/output/{today_date}.md'
            
            for attempt in range(self.retry_config['max_retries']):
                if not self.rate_limiter.can_process():
                    time.sleep(self.retry_config['retry_delay'])
                    continue
                    
                try:
                    headers, payload = self.create_api_request(today_date)
                    response = self.make_api_request(headers, payload)
                    
                    if response.status_code == 429:  # Rate limit exceeded
                        wait_time = float(response.headers.get('Retry-After', self.retry_config['retry_delay']))
                        time.sleep(wait_time)
                        continue
                        
                    analysis_text = self.process_response(response)
                    self.cache.set(cache_key, analysis_text)
                    self.write_sector_report(output_path, analysis_text)
                    
                    logging.info(f'セクター分析が完了しました。出力ファイル: {output_path}')
                    print(f'セクター分析が完了しました。出力ファイル: {output_path}')
                    return analysis_text
                    
                except requests.exceptions.RequestException as e:
                    wait_time = self.retry_config['backoff_factor'] ** attempt
                    time.sleep(wait_time)
                    logging.warning(f"API呼び出しに失敗しました。リトライ {attempt + 1}/{self.retry_config['max_retries']}")
                
            raise Exception("最大リトライ回数を超過しました")
            
        except Exception as e:
            self.handle_error(e)

def main():
    analyzer = JapanSectorAnalyzer()
    analyzer.analyze_sectors()

if __name__ == "__main__":
    main()






import os
import requests
import base64
from datetime import datetime
import markdown
import html
import re
from dotenv import load_dotenv

load_dotenv('M:/ML/ChatGPT/gennote/.env')

def remove_think_sections(content):
    # <think>タグとその中身を削除
    return re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

def post_hatenablog():
    try:
        hatena_id = os.getenv('HATENA_ID')
        api_key = os.getenv('HATENA_API_KEY')
        blog_domain = 'kafkafinancialgroup.hatenablog.com'
        
        endpoint = f'https://blog.hatena.ne.jp/{hatena_id}/{blog_domain}/atom/entry'
        auth_string = base64.b64encode(f"{hatena_id}:{api_key}".encode()).decode()
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md'
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが存在しません: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # <think>セクションを削除
        content = remove_think_sections(content)
        
        # Markdownの変換設定
        md = markdown.Markdown(extensions=['extra', 'nl2br'])
        content_html = md.convert(content)
        
        entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <title>金融AIレポート {current_date}</title>
    <author><name>{hatena_id}</name></author>
    <content type="text/html">
        <![CDATA[
        {content_html}
        ]]>
    </content>
    <updated>{datetime.now().isoformat()}</updated>
    <app:control xmlns:app="http://www.w3.org/2007/app">
        <app:draft>no</app:draft>
    </app:control>
</entry>'''
        
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': f'Basic {auth_string}'
        }
        
        response = requests.post(
            endpoint,
            headers=headers,
            data=entry_xml.encode('utf-8')
        )
        
        if response.status_code == 201:
            entry_url = response.headers.get('Location', 'URL not found')
            print(f'投稿成功: {entry_url}')
            return True
        else:
            print(f"APIエラー: ステータスコード {response.status_code}")
            print(f"エラー詳細: {response.text}")
            return False
            
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return False

if __name__ == "__main__":
    post_hatenablog()
