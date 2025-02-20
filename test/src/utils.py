import logging
from datetime import datetime
import markdown
import re

def setup_logging(filename='app.log'):
    """ロギング設定"""
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def format_blog_content(content: str) -> str:
    """ブログコンテンツのフォーマット"""
    formatted = content.replace('# ', '*').replace('## ', '**')
    formatted = formatted.replace('- ', ':').replace('：', ':')
    return formatted

def remove_think_sections(content: str) -> str:
    """思考セクションの削除"""
    return re.sub(r'.*?', '', content, flags=re.DOTALL)

def convert_to_html(content: str) -> str:
    """MarkdownをHTMLに変換"""
    md = markdown.Markdown(extensions=['extra', 'nl2br'])
    return md.convert(content)
