from datetime import datetime
import os
import requests
import pandas as pd
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv('M:/ML/ChatGPT/gennote/.env')

def process_input_with_perplexity():
    # CSVファイルのパス設定
    csv_file_path = 'M:/ML/ChatGPT/gennote/test/input/prompts.csv'
    
    try:
        # CSVファイルの読み込み
        df = pd.read_csv(csv_file_path)
        
        for index, row in df.iterrows():
            date = row['date']  # 日付列
            prompt = row['prompt']  # プロンプト列
            output_file_path = f'M:/ML/ChatGPT/gennote/test/output/{date}.md'
            
            # APIリクエストの準備
            api_url = "https://api.perplexity.ai/chat/completions"
            api_key = os.getenv('PerplexityAPI_KEY')
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{
                    "role": "user",
                    "content": fr"具体的かつ明瞭に平文で回答してください。{prompt}"
                }]
            }
            
            # APIリクエストの送信
            response = requests.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            # レスポンスの処理
            result = response.json()
            output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")
            
            # 結果をファイルに書き込み
            with open(output_file_path, 'w', encoding='utf-8') as output_file:
                output_file.write(output_text)
            print(f'処理が完了しました。出力ファイル: {output_file_path}')
            
    except FileNotFoundError:
        print(f'CSVファイルが存在しません: {csv_file_path}')
    except requests.exceptions.RequestException as e:
        print(f"APIエラー: {str(e)}")
    except Exception as e:
        print(f"予期せぬエラー: {str(e)}")

if __name__ == "__main__":
    process_input_with_perplexity()
