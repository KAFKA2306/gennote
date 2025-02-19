from datetime import datetime
import os
import requests
from dotenv import load_dotenv

class FinancialDataProcessor:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        self.api_key = os.getenv('PerplexityAPI_KEY')
        self.api_url = "https://api.perplexity.ai/chat/completions"

    def get_file_paths(self):
        today_date = datetime.now().strftime('%Y-%m-%d')
        return {
            'input': f'M:/ML/ChatGPT/gennote/test/input/{today_date}.txt',
            'output': f'M:/ML/ChatGPT/gennote/test/output/{today_date}.md'
        }

    def create_api_request(self, today_date):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
本日{today_date}の市場データに基づき、以下のフォーマットで回答してください：

# 金融AIレポート {today_date}

## 好決算銘柄
[好決算銘柄の詳細をリストアップ]
- 銘柄コード(https://kabutan.jp/stock/finance?code=tickerのリンク埋め込み)：
- 銘柄名：
- 会社紹介：
- 決算まとめ：
- 売上高：
- 営業利益：
- 株価変動率：


## 値上がり率上位銘柄
[値上がり率上位3銘柄をリストアップ]
- 銘柄コード(https://kabutan.jp/stock/finance?code=tickerのリンク埋め込み)：
- 銘柄名：
- 会社紹介：
- 上昇率：
- 理由：

"""

        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }]
        }
        
        return headers, payload

    def format_blog_content(self, content):
        # Markdownをはてな記法に変換
        formatted = content.replace('# ', '*').replace('## ', '**')
        formatted = formatted.replace('- ', ':').replace('：', ':')
        return formatted

    def write_output_file(self, file_path, content):
        formatted_content = self.format_blog_content(content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)

    def process_data(self):
        try:
            paths = self.get_file_paths()
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            headers, payload = self.create_api_request(today_date)
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")
            
            self.write_output_file(paths['output'], output_text)
            print(f'処理が完了しました。出力ファイル: {paths["output"]}')
            
        except requests.exceptions.RequestException as e:
            print(f"APIエラー: {str(e)}")
        except Exception as e:
            print(f"エラーが発生しました: {str(e)}")

def main():
    processor = FinancialDataProcessor()
    processor.process_data()

if __name__ == "__main__":
    main()
