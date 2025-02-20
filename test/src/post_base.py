from config import POST_CONFIG, BASE_CONFIG
from utils import convert_to_html, remove_think_sections
import base64
import requests
from datetime import datetime

class PostBase:
    def __init__(self):
        self.hatena_config = POST_CONFIG['hatena']
        self.base_config = BASE_CONFIG
        
    def create_auth_header(self, hatena_id, api_key):
        auth_string = base64.b64encode(f"{hatena_id}:{api_key}".encode()).decode()
        return {
            'Content-Type': self.hatena_config['content_type'],
            'Authorization': f'Basic {auth_string}'
        }

    def prepare_content(self, content):
        content = remove_think_sections(content)
        return convert_to_html(content)

class HatenaPost(PostBase):
    def post(self, content, hatena_id, api_key, blog_domain):
        try:
            endpoint = self.hatena_config['endpoint_template'].format(
                hatena_id, blog_domain
            )
            headers = self.create_auth_header(hatena_id, api_key)
            content_html = self.prepare_content(content)
            
            entry_xml = self.hatena_config['entry_template'].format(
                datetime.now().strftime("%Y-%m-%d"),
                hatena_id,
                content_html,
                datetime.now().isoformat()
            )
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            entry_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom"
       xmlns:app="http://www.w3.org/2007/app">
    <title>金融AIレポート {current_date}</title>
    <author>
        <name>{hatena_id}</name>
    </author>
    <content type="text/html"><![CDATA[
        {content_html}
    ]]></content>
    <updated>{datetime.now().isoformat()}</updated>
    <app:control>
        <app:draft>no</app:draft>
    </app:control>
</entry>'''

            response = requests.post(
                endpoint,
                headers=headers,
                data=entry_xml.encode('utf-8')
            )

            if response.status_code == 201:
                return True, response.headers.get('Location', 'URL not found')
            return False, f"APIエラー: {response.status_code}"

        except Exception as e:
            return False, str(e)
