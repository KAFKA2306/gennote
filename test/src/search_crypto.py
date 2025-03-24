# search_crypto.py
from datetime import datetime
from search_base import SearchBase
from post_crypto import CryptoPostProcessor

class CryptoSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            # グローバルトップサイト
            "cointelegraph.com",         # 月間1280万訪問者（1位）
            "utoday.com",                # 月間880万訪問者（2位）
            "coindesk.com",              # 月間500万訪問者（3位）
            "coincodex.com",             # 月間450万訪問者（4位）
            "coingape.com",              # 月間450万訪問者（5位）
            "ambcrypto.com",             # 月間430万訪問者（6位）
            "crypto.news",               # 月間410万訪問者（7位）
            "bitcoinist.com",            # 月間370万訪問者（8位）
            "dailyhodl.com",             # 月間350万訪問者（9位）
            "beincrypto.com",            # 月間330万訪問者（10位）
            
            # 地域特化型
            "bitcoin.com",               # アジア市場に強み
            "news.bitcoin.com",         # Bitcoin関連ニュース専門
            "decrypt.co",                # Web3/NFT分野に特化
            
            # 機関投資家向け
            "blockworks.co",             # 機関投資家向け分析
            "theblock.co",               # 深い市場分析
            
            # 日本関連
            "coinpost.jp",               # 日本語主要サイト
            "cryptowatch.jp",           # 日本語市場分析
            
            # 公式情報源
            "sec.gov",                   # 米国証券取引委員会
            "finra.org",                 # 金融業規制当局
            "bis.org",                   # 国際決済銀行
        ]

        self.recency_days = 1

    def create_crypto_prompt(self):
        base_prompt = self.create_base_prompt()
        crypto_prompt = f"""
        {base_prompt}
        ## 仮想通貨/暗号資産 投資家向けアナリストレポート

        市場の変化、法律や思惑の変化から、今後の投機的機会を考察する根拠の情報をお届けします。
        主要暗号資産や、暗号資産関連株の急騰や急落の背景にある要因を分析し、今後の価格変動についての示唆を提供します。

        【検索条件】
        - 重要度: 市場構造・規制・機関投資家動向（定量的に）
        - 対象通貨: BTC,ETH,SOL
        - 対象BTC関連株: MSTR, MARA,SML, COIN, Metaplanet, SBI VC trade, Remixpoint, gumi
        - 投機的な動き

        【出力形式】
        ## マクロ環境の変化
        - 金融政策（FRB/日銀）の影響
        - 機関投資家の資金フロー動向

        ## 重要イベント・ニュース
        4. [重要ニュース]
        - 価格への影響分析
        - 投資機会への示唆
        3. [重要イベントスケジュール]
        - 投資機会への示唆

        ## ETF市場の動向 
        - 投資機会への示唆

        ## BTC関連株の分析
        - 機関投資家の保有動向
        - 事業戦略の変化
        - 財務状況の変化
        - MSTR,NAV
        - Metaplanet, SBIbitbank, Remixpoint, gumi
        - 投資機会への示唆


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