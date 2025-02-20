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
    return re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)

def enhance_content(content):
    content = re.sub(r'(価格：\d+円)', r'**\1**', content)
    content = re.sub(r'(https://booth\.pm/ja/items/\d+)', 
                    r'<div class="item-link">\1</div>', content)
    return content

def add_image_previews(content):
    pattern = r'https://booth\.pm/ja/items/(\d+)'
    replacement = (
        r'<div class="item-card">'
        r'<a href="https://booth.pm/ja/items/\1" target="_blank">'
        r'<img class="item-thumb" src="https://booth.pximg.net/\1/booth_thumb.jpg" '
        r'alt="衣装プレビュー" loading="lazy">'
        r'</a>'
        r'<div class="item-info">\1</div>'
        r'</div>'
    )
    return re.sub(pattern, replacement, content)

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
        
        content = remove_think_sections(content)
        content = enhance_content(content)
        content = add_image_previews(content)
        
        md = markdown.Markdown(extensions=['extra', 'nl2br'])
        content_html = md.convert(content)
        
        entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom">
    <title>✨今日のかわいい衣装たち！ {current_date}｜BOOTH新作ピックアップ</title>
    <author><name>{hatena_id}</name></author>
    <content type="text/html">
        <![CDATA[
        <style>
            .container {{
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            .item-card {{
                background: white;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            }}
            .item-thumb {{
                width: 100%;
                max-width: 600px;
                border-radius: 8px;
                margin: 10px auto;
                display: block;
            }}
            .item-info {{
                padding: 15px 0;
            }}
            .item-price {{
                color: #ff6b9d;
                font-size: 1.2em;
                font-weight: 600;
                margin: 10px 0;
            }}
            .header {{
                background: #fff8fa;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 30px;
                text-align: center;
            }}
            .footer {{
                background: #fff8fa;
                padding: 20px;
                border-radius: 12px;
                margin-top: 30px;
            }}
            .new-tag {{
                display: inline-block;
                background: #ff6b9d;
                color: white;
                padding: 3px 10px;
                border-radius: 12px;
                font-size: 0.9em;
                margin-left: 10px;
            }}
        </style>
        
        <div class="container">
            <div class="header">
                <h2>💝 今日のBOOTH新作衣装</h2>
                <p>かわいい衣装をピックアップしてお届けします！</p>
            </div>

            {content_html}
            
        </div>
        ]]>
    </content>
    <category term="BOOTH" />
    <category term="3D衣装" />
    <category term="VRChat" />
    <category term="バーチャルYouTuber" />
    <category term="かわいい" />
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
            print(f'投稿成功✨: {entry_url}')
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
