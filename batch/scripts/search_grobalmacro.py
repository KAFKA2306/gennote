# search_grobalmacro.py

from datetime import datetime
import os
import sys
import logging

from search_base import SearchBase
from post_base import PostBase

class GlobalMacroPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["グローバルマクロ", "経済分析", "金融市場"]
        self.categories = ["マーケット", "投資", "経済"]

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_globalmacro.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = f"グローバルマクロ経済分析レポート {current_date}"
            
            entry_xml = self.create_entry_xml(
                title=title,
                content=content,
                tags=self.tags,
                categories=self.categories
            )
            
            success, url = self.post_to_hatena(entry_xml)
            if success:
                self.logger.info(f"投稿URL: {url}")
            return success
            
        except Exception as e:
            self.logger.error(f"Post Process Error: {str(e)}")
            return False

class GlobalMacroSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
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
        self.recency_days = 7

    def create_globalmacro_prompt(self):
        base_prompt = self.create_base_prompt()
        globalmacro_prompt = f"""
{base_prompt}

# グローバルマクロ経済分析レポート

【検索条件】
- 重要度: 市場への影響度が高い順
- 地域: グローバル（主要国・地域）
- 分野: マクロ経済指標、金融政策、市場動向

【出力形式】

## 1. 主要経済指標分析

- GDP成長率予測（世界・主要国）
- インフレ動向と中央銀行の政策
- 雇用統計と賃金動向
- 国際収支と資本フロー

## 2. 金融市場動向

- 主要通貨の為替レート推移
- 国債利回りと金融政策の影響
- 株式市場のバリュエーション
- クレジット市場のリスク評価

## 3. 商品市場分析

- エネルギー価格の需給動向
- 産業用金属の価格トレンド
- 農産物市場の状況
- 貴金属市場の動き

## 4. リスク要因とマクロ展望

- 地政学的リスクの評価
- 金融システムの安定性
- 新興国経済の見通し
- テクノロジーと生産性への影響
"""
        return globalmacro_prompt

    def execute_search(self):
        prompt = self.create_globalmacro_prompt()
        
        content = self.call_perplexity_api(
            prompt,
            self.domain_filter,
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_globalmacro.md'
            
            if self.save_content(content, filename):
                # 投稿処理
                poster = GlobalMacroPostProcessor()
                success = poster.post_content()
                return success
                
        return False

def main():
    searcher = GlobalMacroSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()
