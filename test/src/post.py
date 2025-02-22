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
