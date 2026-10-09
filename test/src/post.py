import base64
import hashlib
import html
import json
import os
import re
from datetime import datetime
from pathlib import Path

import markdown
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('M:/ML/ChatGPT/gennote/.env')


def clean_html_content(content):
    """HTMLコンテンツのクリーニング処理"""
    cleaned = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    soup = BeautifulSoup(cleaned, 'html.parser')
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'hr', 'ul', 'ol',
        'li', 'strong', 'em', 'blockquote', 'pre', 'table', 'thead', 'tbody',
        'tr', 'th', 'td', 'a', 'img', 'div', 'span'
    ]
    for tag in soup.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
        else:
            for attr in list(tag.attrs):
                if attr not in ['href', 'src', 'alt']:
                    del tag[attr]
    return soup.prettify()


def publication_id(title, content):
    payload = json.dumps({'title': title, 'content': content}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()


def _read_state(path):
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def _write_state(path, state):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def publish_entry(title, content, endpoint, headers, state_path, http_post=requests.post):
    """Publish once, persisting confirmed or uncertain completion evidence."""
    state_path = Path(state_path)
    identity = publication_id(title, content)
    state = _read_state(state_path)
    previous = state.get(identity)
    if previous and previous.get('status') == 'confirmed':
        return previous
    if previous and previous.get('status') == 'uncertain':
        return previous

    entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
    <entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
      <title>{html.escape(title)}</title>
      <content type="text/x-markdown">{html.escape(content)}</content>
      <updated>{datetime.now().isoformat()}</updated>
      <app:control><app:draft>no</app:draft></app:control>
    </entry>'''
    try:
        response = http_post(endpoint, headers=headers, data=entry_xml.encode('utf-8'))
    except requests.RequestException as exc:
        result = {'publicationId': identity, 'status': 'uncertain', 'reason': type(exc).__name__}
        state[identity] = result
        _write_state(state_path, state)
        return result

    location = response.headers.get('Location')
    if response.status_code == 201 and location:
        result = {'publicationId': identity, 'status': 'confirmed', 'remoteUrl': location}
    elif response.status_code == 201:
        result = {'publicationId': identity, 'status': 'uncertain', 'reason': 'missing_remote_identity'}
    else:
        result = {'publicationId': identity, 'status': 'failed', 'httpStatus': response.status_code}
    state[identity] = result
    _write_state(state_path, state)
    return result


def post_hatenablog():
    try:
        hatena_id = os.getenv('HATENA_ID')
        api_key = os.getenv('HATENA_API_KEY')
        blog_domain = 'kafkafinancialgroup.hatenablog.com'
        endpoint = f'https://blog.hatena.ne.jp/{hatena_id}/{blog_domain}/atom/entry'
        auth_string = base64.b64encode(f"{hatena_id}:{api_key}".encode()).decode()
        current_date = datetime.now().strftime('%Y-%m-%d')
        file_path = Path(f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md')
        if not file_path.exists():
            raise FileNotFoundError(f'ファイルが存在しません: {file_path}')
        content = file_path.read_text(encoding='utf-8')
        md = markdown.Markdown(extensions=['extra', 'nl2br', 'tables', 'fenced_code'])
        cleaned_html = clean_html_content(md.convert(content))
        title = f'金融AIレポート {current_date}'
        headers = {'Content-Type': 'application/xml', 'Authorization': f'Basic {auth_string}'}
        state_path = Path(__file__).parent.parent / 'publication-state.json'
        result = publish_entry(title, cleaned_html, endpoint, headers, state_path)
        print(json.dumps(result, ensure_ascii=False))
        return result['status'] == 'confirmed'
    except Exception as exc:
        print(f'エラー発生: {exc}')
        return False


if __name__ == '__main__':
    post_hatenablog()
