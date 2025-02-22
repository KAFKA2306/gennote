from datetime import datetime
import os
import requests
from dotenv import load_dotenv

from config import BASE_CONFIG, get_file_paths, SEARCH_DOMAINS
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
        self.search_domains =  ['stats.gov.cn', 'pbc.gov.cn', 'mofcom.gov.cn', 'aastocks.com', 'etnet.com.hk', 'sse.com.cn']

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
    # 香港中国金融市場AI/LLMレポート {today_date}

    以下の内容について、經濟通および関連金融サイトの中国語、広東語の最新情報に基づいて明瞭かつ具体的に引用してください。

    ## 1. 中国AI/LLM関連企業の主要ニュース
    - 本日の重要なAI/LLM関連ニュース3選（具体的な事例と影響を含む）
    - 関連する上場企業の動き
    - 各企業のティッカーシンボルは https://finance.yahoo.com/quote/[TICKER] の形式でリンク化

    ## 2. 最近のAI/LLM関係の中国企業、香港企業の決算概要
    各企業について以下の項目を明瞭かつ具体的に紹介：
    - 企業コード・名称（Yahoo Financeリンク付き）
    - 事業概要（主力製品・サービス）
    - 決算発表日
    - 決算ハイライト
    * 売上高（前年同期比）
    * 営業利益（前年同期比）
    * 純利益（前年同期比）
    * 決算発表後の株価変動
    * 年初来パフォーマンス

    ## 3. 市場動向への影響
    - 投資家の反応や市場センチメント
    - 今後の見通し
    
    注意事項：
    - 数値は具体的に記載
    - 企業名は正式名称を使用
    - すべての情報は日本語で出力
    - 平文で出力
    """

        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "search_domain_filter": self.search_domains,
            "search_recency_filter": "week"
        }
        
        return headers, payload



    def format_blog_content(self, content):
        return format_blog_content(content)

    def write_output_file(self, file_path, content):
        formatted_content = self.format_blog_content(content)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
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
            citations = result.get("choices", [{}])[0].get("message", {}).get("citations", [])
            
            # 出典情報を追加
            if citations:
                output_text += "\n\n## 参考文献\n"
                for citation in citations:
                    output_text += f"- {citation['title']}: {citation['url']}\n"
            
            self.write_output_file(paths['output'], output_text)
            print(f'処理が完了しました。出力ファイル: {paths["output"]}')
            
        except requests.exceptions.RequestException as e:
            print(f"APIエラー: {str(e)}")
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")

def main():
    processor = FinancialDataProcessor()
    processor.process_data()
    # postモジュールのインポートと使用は必要に応じて追加

if __name__ == "__main__":
    main()

import os
import requests
import base64
from datetime import datetime
import markdown
import html
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('M:/ML/ChatGPT/gennote/.env')

def clean_html_content(content):
    """HTMLコンテンツのクリーニング処理"""
    # 不要なセクション削除
    cleaned = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # BeautifulSoupでHTML解析
    soup = BeautifulSoup(cleaned, 'html.parser')
    
    # 許可するHTMLタグ
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr',
        'ul', 'ol', 'li',
        'strong', 'em', 'blockquote', 'pre',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'a', 'img', 'div', 'span'
    ]
    
    # 不要な属性削除
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            attrs = list(tag.attrs.keys())
            for attr in attrs:
                if attr not in ['href', 'src', 'alt']:
                    del tag[attr]
    
    # 整形処理
    return soup.prettify()

def post_hatenablog():
    try:
        # 認証情報の取得
        hatena_id = os.getenv('HATENA_ID')
        api_key = os.getenv('HATENA_API_KEY')
        blog_domain = 'kafkafinancialgroup.hatenablog.com'
        endpoint = f'https://blog.hatena.ne.jp/{hatena_id}/{blog_domain}/atom/entry'
        
        # 基本認証の準備
        auth_string = base64.b64encode(f"{hatena_id}:{api_key}".encode()).decode()
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # ファイル読み込み
        file_path = f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが存在しません: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Markdown変換処理
        md = markdown.Markdown(extensions=[
            'extra',
            'nl2br',
            'tables',
            'fenced_code'
        ])
        html_content = md.convert(content)
        
        # HTMLクリーニング
        cleaned_html = clean_html_content(html_content)
        
        # XMLエントリー生成
        entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom"
               xmlns:app="http://www.w3.org/2007/app">
          <title>金融AIレポート {current_date}</title>
          <author><name>{hatena_id}</name></author>
          <content type="text/x-markdown">
            {html.escape(cleaned_html)}
          </content>
          <updated>{datetime.now().isoformat()}</updated>
          <app:control>
            <app:draft>no</app:draft>
          </app:control>
        </entry>
        '''
        
        # ヘッダー設定
        headers = {
            'Content-Type': 'application/xml',
            'Authorization': f'Basic {auth_string}'
        }
        
        # APIリクエスト送信
        response = requests.post(
            endpoint,
            headers=headers,
            data=entry_xml.encode('utf-8')
        )
        
        # レスポンス処理
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