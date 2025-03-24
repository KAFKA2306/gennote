# search_jp.py
from datetime import datetime
from search_base import SearchBase
from post_jp import JPPostProcessor

class JPSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
        # メインの金融情報サイト
        'kabutan.jp',           # アクセス可能
        'minkabu.jp',          # アクセス可能
        'finance.yahoo.co.jp',  # アクセス可能
        'jpx.co.jp',           # アクセス可能
        'disclosure.edinet-fsa.go.jp',  # EDINETの正しいURL
        'www.release.tdnet.info',       # TDnetの正しいURL
        'www.jpx.co.jp',        # JPXの正しいURL
        
        # ニュースメディア
        'jp.reuters.com',      # 日本語サイトの正しいURL
        'reuters.com',      # 日本語サイトの正しいURL
        'jp.wsj.com',         # 日本語サイトの正しいURL
        'www.wsj.com',        # 日本語サイトの正しいURL
        'bloomberg.co.jp', # 日本語ブルームバーグの正しいURL
        'www.nikkei.com',      # 日本経済新聞
        
        # 経済研究所・シンクタンク
        'https://www.boj.or.jp/',  # 日本銀行
        'www.mof.go.jp',        # 財務省
        'www.nli-research.co.jp',  # 日本総合研究所
        'www.dlri.co.jp',      # 第一生命経済研究所
        'www.jcer.or.jp',      # 日本経済研究センター
        'www.jeri.co.jp',      # 日本経済研究所（横浜市資料より確認）
        
        # 個人投資家・アナリスト情報
        'www.shenmacro.com',   # 正しいURL
        'www.globalmacroresearch.org/jp',  # 正しいURL
        'muragoe-makoto.blog.jp',  # 正しいURL
        'note.com/utbuffett',      # 東大ぱふぇっと - 相場予測note（有料）
        'note.com/goto_finance',   # 後藤達也 - 月額500円（ベーシック）/980円（コアメンバー）
        'note.com/hirosetakao',    # 広瀬隆雄 - 個別記事課金（100-300円）
        'note.com/cjdbx883',       # 村松一之 - フォーライクス代表

    ]

        self.recency_days = 2

    def create_jp_prompt(self):
        base_prompt = self.create_base_prompt()
        jp_prompt = f"""
        {base_prompt}
        # 日本株式市場 投資戦略レポート

        【分析対象】
        ## 金融株式市況環境
        - 金利インフレ動向
        - 外国人投資家動向

        ## 1. 業種別動向
        - 上昇率TOP3業種
        - 業種別需給動向（売買代金上位）

        ## 2. 注目銘柄スクリーニング
        - ストップ高銘柄
        - 出来高急増（前日比200%以上）
        - 高ROE（15%以上）銘柄3選
        - 高DOE（5%以上）銘柄3選      
        - 株価上昇率TOP

        ## 3. 決算発表銘柄分析
        - 好決算（営業増益）銘柄
        - 上方修正銘柄
        - 増配/自社株買い発表
        - 決算後の株価反応

        ## 4. 特別注目銘柄
        - 決算短信での重要開示事項
        - 業績予想の修正
        - 事業計画の変更

        【出力形式】
        各セクションで：
        - 銘柄コード・名称（https://kabutan.jp/stock/?code=[code]形式でリンク）
        - 業績サマリー（売上高/営業利益/純利益）
        - 特記事項（決算/材料/需給）
        """
        return jp_prompt


    def execute_search(self):
        prompt = self.create_jp_prompt()
        content = self.call_perplexity_api(
            prompt, 
            self.domain_filter, 
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_jp.md'
            if self.save_content(content, filename):
                poster = JPPostProcessor()
                success = poster.post_content()
                return success
        return False

if __name__ == "__main__":
    searcher = JPSearcher()
    searcher.execute_search()
