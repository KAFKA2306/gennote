from datetime import datetime
import os
import requests
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv('M:/ML/ChatGPT/gennote/.env')

def process_input_with_perplexity():
    # 日付フォーマットの設定
    today_date = datetime.now().strftime('%Y-%m-%d')
    
    # ファイルパスの設定
    input_file_path = f'M:/ML/ChatGPT/gennote/test/input/{today_date}.txt'
    output_file_path = f'M:/ML/ChatGPT/gennote/test/output/{today_date}.md'
    
    try:
        # 入力ファイルの読み込み
        with open(input_file_path, 'r', encoding='utf-8') as input_file:
            input_data = input_file.read()
    except FileNotFoundError:
        print(f'入力ファイルが存在しません: {input_file_path}')
        return
    
    # APIリクエストの準備
    api_url = "https://api.perplexity.ai/chat/completions"
    api_key = os.getenv('PerplexityAPI_KEY')
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [
            {
                "role": "user",
                    "content": fr"具体的かつ明瞭に平文で回答してください。{input_data}",
            }
        ]
    }
    
    try:
        # APIリクエストの送信
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        # レスポンスの処理
        result = response.json()
        print(result)
        output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")
        
        # 結果をファイルに書き込み
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(output_text)
            
        print(f'処理が完了しました。出力ファイル: {output_file_path}')
        
    except requests.exceptions.RequestException as e:
        print(f"APIエラー: {str(e)}")

if __name__ == "__main__":
    process_input_with_perplexity()
