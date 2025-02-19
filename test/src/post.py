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
