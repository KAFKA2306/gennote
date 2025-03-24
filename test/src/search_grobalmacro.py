from datetime import datetime
import os
import requests
from dotenv import load_dotenv

from config import BASE_CONFIG, get_file_paths, SEARCH_DOMAINS
from utils import setup_logging, format_blog_content, remove_think_sections, convert_to_html

class GlobalMacroAnalyzer:
    def __init__(self):
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        setup_logging()
        self.api_key = BASE_CONFIG['api_key']
        self.api_url = BASE_CONFIG['api_url']
        self.search_domains = [
            # グローバル金融機関
            "worldbank.org",
            "imf.org",
            "bis.org",
            "oecd.org",
            "fred.stlouisfed.org",
            "ecb.europa.eu",
            "boj.or.jp",
            
            # 金融市場
            "bloomberg.com",
            "reuters.com",
            "ft.com",
            "wsj.com",
            "nasdaq.com",
            "nyse.com",
            "jpx.co.jp",
            
            # マクロ経済データ
            "tradingeconomics.com",
            "investing.com",
            "marketwatch.com",
            "finance.yahoo.com",
            
            # 日本市場
            "nikkei.com",
            "quick.co.jp",
            "minkabu.jp",
            "mof.go.jp",
            "esri.cao.go.jp",
            
            # 中国市場
            "stats.gov.cn",
            "pbc.gov.cn",
            "sse.com.cn",
            "aastocks.com",
            "etnet.com.hk",
            
            # 商品市場
            "cmegroup.com",
            "ice.com",
            "lme.com",
            "eia.gov",
            "gold.org"
        ]


    def create_api_request(self, today_date):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""
以下の項目について、最新のグローバルマクロ経済分析を行い、具体的な数値とデータに基づいてレポートを作成してください：

1. 主要経済指標分析
- GDP成長率予測（世界・主要国）
- インフレ動向と中央銀行の政策
- 雇用統計と賃金動向
- 国際収支と資本フロー

2. 金融市場動向
- 主要通貨の為替レート推移
- 国債利回りと金融政策の影響
- 株式市場のバリュエーション
- クレジット市場のリスク評価

3. 商品市場分析
- エネルギー価格の需給動向
- 産業用金属の価格トレンド
- 農産物市場の状況
- 貴金属市場の動き

4. リスク要因とマクロ展望
- 地政学的リスクの評価
- 金融システムの安定性
- 新興国経済の見通し
- テクノロジーと生産性への影響

日付: {today_date}
        """

        payload = {
            "model": "sonar-reasoning-pro",
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "search_domain_filter": self.search_domains,
            "search_recency_filter": "week"
        }
        
        return headers, payload

    def format_macro_content(self, content, citations):
        formatted_content = "# グローバルマクロ経済分析レポート\n\n"
        formatted_content += f"作成日: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        formatted_content += content

        if citations:
            formatted_content += "\n\n## データソースと参考文献\n"
            for citation in citations:
                formatted_content += f"- [{citation['title']}]({citation['url']})\n"

        return formatted_content

    def write_output_file(self, file_path, content):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def process_macro_analysis(self):
        try:
            paths = get_file_paths()
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            headers, payload = self.create_api_request(today_date)
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            output_text = result.get("choices", [{}])[0].get("message", {}).get("content", "APIからの応答がありません")
            citations = result.get("choices", [{}])[0].get("message", {}).get("citations", [])
            
            formatted_content = self.format_macro_content(output_text, citations)
            self.write_output_file(paths['output'], formatted_content)
                      
            print(f'マクロ経済分析レポートが生成されました: {paths["output"]}')
            
        except requests.exceptions.RequestException as e:
            print(f"APIリクエストエラー: {str(e)}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {str(e)}")

def main():
    analyzer = GlobalMacroAnalyzer()
    analyzer.process_macro_analysis()

if __name__ == "__main__":
    main()