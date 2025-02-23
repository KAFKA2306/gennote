# post_base.py
import os
import requests
import base64
import markdown
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
from datetime import datetime
from xml.sax.saxutils import escape

class PostBase:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        self.hatena_id = os.getenv('HATENA_ID')
        self.hatena_api_key = os.getenv('HATENA_API_KEY')
        self.blog_domain = 'kafkafinancialgroup.hatenablog.com'
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def clean_content(self, content):
        """下位互換性のために残す"""
        return self.clean_html_content(content)

    def clean_html(self, content):
        """下位互換性のために残す"""
        return self.clean_html_content(content)

    def clean_html_content(self, content):
        """HTMLコンテンツのクリーニング処理"""
        # Thinkセクションの削除
        #content = re.sub(r'## Think\n.*?(?=\n##|$)', '', content, flags=re.DOTALL)
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        # 引用番号の削除
        content = re.sub(r'\[\d+\]', '', content)
   
        # Markdownの前処理
        content = self._clean_markdown_symbols(content)
        
        # Markdown変換
        md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables', 'fenced_code'])
        html_content = md.convert(content)
        
        # BeautifulSoupでHTML解析
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 許可するHTMLタグ
        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'hr',
            'ul', 'ol', 'li',
            'strong', 'em', 'blockquote', 'pre', 'code',
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

        return str(soup)

    def _clean_markdown_symbols(self, content):
        """Markdownシンボルの整理"""
        content = re.sub(r'^###\s', '#### ', content, flags=re.MULTILINE)
        content = re.sub(r'^##\s', '### ', content, flags=re.MULTILINE)
        content = re.sub(r'^#\s', '## ', content, flags=re.MULTILINE)
        content = re.sub(r'^\*\s', '- ', content, flags=re.MULTILINE)
        content = re.sub(r'^\+\s', '- ', content, flags=re.MULTILINE)
        return content

    def create_entry_xml(self, title, content, tags=None, categories=None):
        # HTMLクリーニング
        cleaned_html = self.clean_html_content(content)
        
        # タグとカテゴリの処理
        category_xml = ""
        if tags:
            category_xml += "\n".join([f"<category term='{escape(tag)}' />" for tag in tags])
        if categories:
            category_xml += "\n".join([
                f"<category term='{escape(category)}' scheme='http://www.hatena.ne.jp/info/xmlns#category' />"
                for category in categories
            ])

        entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
  <title>{escape(title)}</title>
  <author><name>{self.hatena_id}</name></author>
  {category_xml}
  <content type="text/html">
    {escape(cleaned_html)}
  </content>
  <updated>{datetime.now().isoformat()}</updated>
  <app:control>
    <app:draft>no</app:draft>
  </app:control>
</entry>'''

        return entry_xml

    def post_to_hatena(self, entry_xml):
        endpoint = f'https://blog.hatena.ne.jp/{self.hatena_id}/{self.blog_domain}/atom/entry'
        auth = base64.b64encode(f"{self.hatena_id}:{self.hatena_api_key}".encode()).decode()

        try:
            response = requests.post(
                endpoint,
                headers={
                    'Content-Type': 'application/xml; charset=utf-8',
                    'Authorization': f'Basic {auth}'
                },
                data=entry_xml.encode('utf-8')
            )
            
            if response.status_code == 201:
                self.logger.info(f'投稿成功: {response.headers.get("Location")}')
                return True, response.headers.get('Location')
            else:
                self.logger.error(f"APIエラー: ステータスコード {response.status_code}")
                self.logger.error(f"エラー詳細: {response.text}")
                return False, None

        except Exception as e:
            self.logger.error(f"Post Error: {str(e)}")
            return False, None
