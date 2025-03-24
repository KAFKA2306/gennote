# search_china.py
from datetime import datetime
from search_base import SearchBase
from post_china import ChinaPostProcessor

class ChinaSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            'stats.gov.cn', 
            'pbc.gov.cn', 
            'mofcom.gov.cn', 
            'aastocks.com', 
            'etnet.com.hk', 
            'sse.com.cn'
        ]
        self.recency_days = 2

    def create_china_prompt(self):
        base_prompt = self.create_base_prompt()
        china_prompt = f"""
        {base_prompt}
        # 香港中国金融市場AI/LLMレポート
        
        【検索条件】
        - 重要度: 市場への影響度が高い順
        - 地域: 中国本土・香港
        - 分野: AI/LLM関連企業
        
        【出力形式】
        ## 1. 中国AI/LLM関連企業の主要ニュース
        - 本日の重要なAI/LLM関連ニュース3選
        - 関連する上場企業の動き
        - 各企業のティッカーシンボルは https://finance.yahoo.com/quote/[TICKER] の形式でリンク化
        
        ## 2. 最近のAI/LLM関係の中国企業、香港企業の決算概要
        各企業について：
        - 企業コード・名称（Yahoo Financeリンク付き）
        - 事業概要（主力製品・サービス）
        - 決算発表日
        - 決算ハイライト
          * 売上高（前年同期比）
          * 営業利益（前年同期比）
          * 純利益（前年同期比）
          * 決算発表後の株価変動
          * 年初来パフォーマンス
        
        ## 3. 市場動向への影響
        - 投資家の反応や市場センチメント
        - 今後の見通し
        """
        return china_prompt

    def execute_search(self):
        prompt = self.create_china_prompt()
        content = self.call_perplexity_api(
            prompt, 
            self.domain_filter, 
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_china.md'
            if self.save_content(content, filename):
                poster = ChinaPostProcessor()
                success = poster.post_content()
                return success
        return False

def main():
    searcher = ChinaSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()
