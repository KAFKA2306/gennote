# search_energy_markets.py

from datetime import datetime
import os
import logging

from search_base import SearchBase
from post_base import PostBase

class EnergyMarketsPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["エネルギー市場", "再生可能エネルギー", "石油", "天然ガス", "原子力"]
        self.categories = ["マーケット", "投資", "エネルギー"]

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_energy_markets.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = f"エネルギー市場分析レポート {current_date}"
            
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

class EnergyMarketsSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            # エネルギー政策・規制機関
            "iea.org",           # 国際エネルギー機関
            "eia.gov",           # 米国エネルギー情報局
            "energy.gov",        # 米国エネルギー省
            "enecho.meti.go.jp", # 経済産業省資源エネルギー庁
            "ferc.gov",          # 米国連邦エネルギー規制委員会
            
            # 石油・ガス関連
            "opec.org",          # 石油輸出国機構
            "ief.org",           # 国際エネルギーフォーラム
            "cedigaz.org",       # 天然ガス情報センター
            "ogj.com",           # Oil & Gas Journal
            
            # 再生可能エネルギー
            "irena.org",         # 国際再生可能エネルギー機関
            "ren21.net",         # 再生可能エネルギー政策ネットワーク
            "seia.org",          # 米国太陽エネルギー産業協会
            "gwec.net",          # 世界風力エネルギー協会
            
            # 原子力
            "iaea.org",          # 国際原子力機関
            "world-nuclear.org", # 世界原子力協会
            "nei.org",           # 米国原子力エネルギー協会
            
            # エネルギー市場・取引
            "cmegroup.com",      # シカゴ・マーカンタイル取引所
            "ice.com",           # インターコンチネンタル取引所
            "platts.com",        # S&Pグローバル・プラッツ
            "argusmedia.com",    # アーガスメディア
            
            # ニュース・分析
            "bloomberg.com",
            "reuters.com",
            "spglobal.com",
            "rystadenergy.com",
            "woodmac.com",       # ウッド・マッケンジー
            
            # 企業情報
            "bp.com",
            "exxonmobil.com",
            "shell.com",
            "chevron.com",
            "total.com",
            "nexteraenergy.com",
            "iberdrola.com"
        ]
        self.recency_days = 7

    def create_energy_markets_prompt(self):
        base_prompt = self.create_base_prompt()
        energy_markets_prompt = f"""
{base_prompt}

# エネルギー市場分析レポート

【検索条件】
- 重要度: 市場への影響度が高い順
- 対象: 石油、天然ガス、再生可能エネルギー、原子力
- 期間: 直近の動向と今後の見通し

【出力形式】

## 1. エネルギー市場の概況

- 原油・天然ガス価格の最新動向
- 主要エネルギー指標の分析
- 需給バランスの変化
- 地政学的要因の影響

## 2. 石油・天然ガス市場

- 原油価格の変動要因
- 主要産油国の生産動向
- 在庫水準と需要予測
- LNG市場の動向と価格トレンド

## 3. 再生可能エネルギー市場

- 太陽光・風力発電の最新コスト動向
- 政策変更と補助金制度の影響
- 蓄電技術の進展
- グリーン水素の開発状況

## 4. 原子力エネルギー

- 原子力発電所の稼働状況
- 新規建設プロジェクト
- 規制環境の変化
- 小型モジュール炉(SMR)の開発動向

## 5. エネルギー転換と投資機会

- 脱炭素化政策の影響
- エネルギー企業の戦略転換
- 有望な投資セクターと企業
- リスク要因と注目ポイント
"""
        return energy_markets_prompt

    def execute_search(self):
        prompt = self.create_energy_markets_prompt()
        
        content = self.call_perplexity_api(
            prompt,
            self.domain_filter,
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_energy_markets.md'
            
            if self.save_content(content, filename):
                # 投稿処理
                poster = EnergyMarketsPostProcessor()
                success = poster.post_content()
                return success
                
        return False

def main():
    searcher = EnergyMarketsSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()
