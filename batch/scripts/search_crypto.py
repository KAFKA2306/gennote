# search_crypto.py
from datetime import datetime
from search_base import SearchBase
from post_crypto import CryptoPostProcessor

class CryptoSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = ["coindesk.com", "cointelegraph.com", "cryptowatch.jp","finance.yahoo.com","kitco.com","binance.com","cryptobriefing.com"]
        self.recency_days = 7

    def create_crypto_prompt(self):
        base_prompt = self.create_base_prompt()
        crypto_prompt = f"""
        {base_prompt}
        ## 仮想通貨/暗号資産マーケットレポート

        【検索条件】
        - 重要度: 市場への影響度が高い順
        - 対象通貨: BTC/ETH/主要アルトコイン
        - 指標: 価格変動/取引量/時価総額/出来高

        【出力形式】
        # 本日のハイライト
        - 最重要ニュース3点を箇条書きで簡潔に

        ## 主要通貨の動向
        ### ビットコイン（BTC）
        - 💰 現在価格: $xx,xxx (前日比 xx%)
        - 💫 主な材料: [重要イベント/ニュース]

        ## 注目ニュース
        1. [最重要ニュース]
        - 影響度: 高/中/低
        - 市場への影響を3行で解説
        
        2. [重要ニュース]
        - 影響度: 高/中/低
        - 市場への影響を3行で解説

        ## 市場分析
        - 機関投資家の動向
        - 規制関連の動き

        ## 今後の注目ポイント
        - 重要イベントスケジュール
        """
        return crypto_prompt


    def execute_search(self):
        prompt = self.create_crypto_prompt()
        # 24時間以内のニュースを取得するため1日を指定
        content = self.call_perplexity_api(prompt, self.domain_filter, recency_days=self.recency_days)

        content = self.call_perplexity_api(prompt, self.domain_filter)
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_crypto.md'
            if self.save_content(content, filename):
                # 投稿処理
                poster = CryptoPostProcessor()
                success = poster.post_content()
                return success
        return False

def main():
    searcher = CryptoSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()