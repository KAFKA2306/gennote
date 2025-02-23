import os
import requests
from dotenv import load_dotenv
import logging

class SearchBase:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY')
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def create_base_prompt(self):
        return """
        【基本設定】
        - 言語: 日本語
        - 具体的かつ明瞭に正確に
        """

    def call_perplexity_api(self, prompt, domain_filter=None, recency_days=None):
        headers = {
            "Authorization": f"Bearer {self.perplexity_api_key}",
            "Content-Type": "application/json"
        }
        
        # 期間指定の設定
        if recency_days:
            recency = f"{recency_days}d"
        else:
            recency = "week"
        
        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "search": {
                "domain_filter": domain_filter if domain_filter else [],
                "recency_filter": recency
            }
        }
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            self.logger.error(f"API Error: {str(e)}")
            return None



    def save_content(self, content, filename):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.info(f"Saved to {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Save Error: {str(e)}")
            return False
