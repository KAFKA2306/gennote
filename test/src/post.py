import os
import requests
import base64
from datetime import datetime
from pathlib import Path
import markdown
import html
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from publication import publish_once

load_dotenv('M:/ML/ChatGPT/gennote/.env')


def clean_html_content(content):
    """HTMLコンテンツのクリーニング処理"""
    cleaned = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    soup = BeautifulSoup(cleaned, 'html.parser')
    allowed_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'pre', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'a', 'img', 'div', 'span']
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            for attr in list(tag.attrs.keys()):
                if attr not in ['href', 'src', 'alt']:
                    del tag[attr]
    return soup.prettify()


def post_hatenablog():
    try:
        hatena_id = os.getenv('HATENA_ID')
        api_key = os.getenv('HATENA_API_KEY')
        blog_domain = 'kafkafinancialgroup.hatenablog.com'
        endpoint = f'https://blog.hatena.ne.jp/{hatena_id}/{blog_domain}/atom/entry'
        auth_string = base64.b64encode(f"{hatena_id}:{api_key}".encode()).decode()
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_path = Path(f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md')
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {file_path}")
        content = file_path.read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables', 'fenced_code'])
        cleaned_html = clean_html_content(md.convert(content))
        entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
        <entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
          <title>金融AIレポート {current_date}</title>
          <author><name>{hatena_id}</name></author>
          <content type="text/x-markdown">{html.escape(cleaned_html)}</content>
          <updated>{datetime.now().isoformat()}</updated>
          <app:control><app:draft>no</app:draft></app:control>
        </entry>'''
        headers = {'Content-Type': 'application/xml', 'Authorization': f'Basic {auth_string}'}

        def create(_article):
            return requests.post(endpoint, headers=headers, data=entry_xml.encode('utf-8'), timeout=30)

        state_path = Path(__file__).resolve().parents[1] / 'publication-state.json'
        result = publish_once(content, state_path, create)
        if result['status'] == 'confirmed':
            print(f"投稿確認済み: {result['remote_url']}")
            return True
        print(f"投稿状態を確認できません: {result}")
        return False
    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return False


if __name__ == "__main__":
    post_hatenablog()
