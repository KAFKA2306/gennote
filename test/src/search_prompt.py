from datetime import datetime
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv('M:/ML/ChatGPT/gennote/.env')

from config import PROMPT_CONFIG, BASE_CONFIG
from utils import setup_logging
import pandas as pd
import requests
import os

class PromptProcessor:
    def __init__(self):
        setup_logging('prompt_processor.log')
        self.api_key = BASE_CONFIG['api_key']
        self.api_url = BASE_CONFIG['api_url']
        self.csv_path = PROMPT_CONFIG['csv_path']

    def process_prompts(self):
        try:
            df = pd.read_csv(self.csv_path)
            
            for index, row in df.iterrows():
                date = row['date']
                prompt = row['prompt']
                output_file_path = f'{BASE_CONFIG["base_path"]}/output/{date}.md'

                payload = {
                    "model": PROMPT_CONFIG['default_model'],
                    "messages": [{
                        "role": "user",
                        "content": fr"具体的かつ明瞭に平文で回答してください。{prompt}"
                    }]
                }

                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                response = requests.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")

                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(output_text)

                print(f'処理完了: {output_file_path}')

        except Exception as e:
            print(f"エラー発生: {str(e)}")

def main():
    processor = PromptProcessor()
    processor.process_prompts()

if __name__ == "__main__":
    PromptProcessor().process_prompts()
