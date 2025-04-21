# search_real_estate.py - 不動産市場分析レポート生成スクリプト

from datetime import datetime
import os
import logging
import re
import json
import requests
from bs4 import BeautifulSoup

from search_base import SearchBase
from post_base import PostBase

class RealEstatePostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["不動産市場", "REIT", "商業不動産", "住宅市場", "不動産投資", "J-REIT"]
        self.categories = ["マーケット", "投資", "不動産"]
        
        # Yahoo Finance APIのエンドポイント（実際のAPIキーが必要な場合は設定）
        self.yahoo_finance_url = "https://finance.yahoo.co.jp/quote/"
        
        # J-REIT関連銘柄
        self.jreit_stocks = {
            "オフィス系": [
                {"code": "8951.T", "name": "日本ビルファンド投資法人"},
                {"code": "8952.T", "name": "ジャパンリアルエステイト投資法人"},
                {"code": "8953.T", "name": "日本リテールファンド投資法人"}
            ],
            "住宅系": [
                {"code": "3269.T", "name": "アドバンス・レジデンス投資法人"},
                {"code": "3278.T", "name": "ケネディクス・レジデンシャル・ネクスト投資法人"},
                {"code": "8979.T", "name": "スターツプロシード投資法人"}
            ],
            "商業施設系": [
                {"code": "3462.T", "name": "野村マスターファンド投資法人"},
                {"code": "8954.T", "name": "オリックス不動産投資法人"},
                {"code": "8960.T", "name": "ユナイテッド・アーバン投資法人"}
            ],
            "物流施設系": [
                {"code": "3466.T", "name": "ラサールロジポート投資法人"},
                {"code": "3471.T", "name": "三菱地所物流リート投資法人"}
            ],
            "ホテル系": [
                {"code": "3308.T", "name": "日本ヘルスケア投資法人"},
                {"code": "3463.T", "name": "いちごホテルリート投資法人"},
                {"code": "8985.T", "name": "ジャパン・ホテル・リート投資法人"}
            ],
            "総合系": [
                {"code": "8964.T", "name": "フロンティア不動産投資法人"},
                {"code": "8982.T", "name": "トップリート投資法人"},
                {"code": "8984.T", "name": "大和ハウスリート投資法人"}
            ]
        }
        
        # 不動産関連企業
        self.real_estate_companies = [
            {"code": "8801.T", "name": "三井不動産"},
            {"code": "8802.T", "name": "三菱地所"},
            {"code": "8803.T", "name": "平和不動産"},
            {"code": "8804.T", "name": "東京建物"},
            {"code": "8830.T", "name": "住友不動産"},
            {"code": "3289.T", "name": "東急不動産ホールディングス"},
            {"code": "8934.T", "name": "サンフロンティア不動産"},
            {"code": "3231.T", "name": "野村不動産ホールディングス"},
        ]

    def get_stock_price(self, stock_code):
        """Yahoo Financeから株価情報を取得する"""
        try:
            url = f"{self.yahoo_finance_url}{stock_code}"
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 検索結果に基づいて修正したセレクター
                price_element = soup.select_one(f'[data-symbol="{stock_code}"][data-field="regularMarketPrice"]')
                if price_element:
                    return price_element.text.strip()
                    
                # 別の方法も試す
                price_element = soup.select_one('//*[@class="D(ib) Mend(20px)"]/span')
                if price_element:
                    return price_element.text.strip()
            
            return "価格情報取得不可"
        except Exception as e:
            self.logger.error(f"株価情報取得エラー: {str(e)}")
            return "価格情報取得不可"


    def add_hyperlinks_and_citations(self, content):
        """コンテンツにハイパーリンクと引用を追加する"""
        updated_content = content
        
        # セクションごとに参考リンクを追加
        sections = re.split(r'## \d+\.', updated_content)
        
        # J-REIT関連銘柄情報を追加
        updated_content += "\n\n## J-REIT関連銘柄情報\n\n"
        
        for category, stocks in self.jreit_stocks.items():
            updated_content += f"### {category}\n\n"
            for stock in stocks:
                price = self.get_stock_price(stock["code"])
                updated_content += f"- [{stock['name']} ({stock['code']})](https://finance.yahoo.co.jp/quote/{stock['code']}) - {price}\n"
            updated_content += "\n"
        
        # 不動産関連企業情報を追加
        updated_content += "## 不動産関連企業\n\n"
        for company in self.real_estate_companies:
            price = self.get_stock_price(company["code"])
            updated_content += f"- [{company['name']} ({company['code']})](https://finance.yahoo.co.jp/quote/{company['code']}) - {price}\n"      

        return updated_content

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_real_estate.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                
            title = f"不動産市場分析レポート {current_date}"
            
            # ハイパーリンクと引用を追加
            content_with_links = self.add_hyperlinks_and_citations(content)
            
            entry_xml = self.create_entry_xml(
                title=title,
                content=content_with_links,
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

class RealEstateSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            # 不動産データ・分析
            "zillow.com",           # 米国不動産データ
            "redfin.com",           # 米国不動産市場分析
            "realtor.com",          # 全米不動産協会
            "corelogic.com",        # 不動産データ分析
            "spglobal.com",         # S&P不動産指数
            "realestate.co.jp",     # 日本不動産情報
            "athome.co.jp",         # 日本不動産ポータル
            "homes.co.jp",          # LIFULL HOME'S
            "suumo.jp",             # SUUMO
            
            # REIT・不動産投資
            "nareit.com",           # 全米REIT協会
            "reit.or.jp",           # 日本REIT協会
            "ares.or.jp",           # 不動産証券化協会
            "greenstreet.com",      # 不動産投資分析
            "msci.com",             # MSCI不動産指数
            "smtri.jp",             # 住友不動産三井トラスト不動産投資顧問
            "jreit.jp",             # J-REIT.jp
            
            # 不動産市場レポート
            "cbre.com",             # CBREグローバル不動産
            "jll.com",              # JLL不動産サービス
            "cushmanwakefield.com", # クッシュマン不動産
            "colliers.com",         # コリアーズ不動産
            "savills.com",          # サヴィルズ不動産
            "miki-shoji.co.jp",     # 三鬼商事
            "xymax.co.jp",          # ザイマックス
            
            # 政府・公的機関
            "mlit.go.jp",           # 国土交通省
            "reins.or.jp",          # 不動産流通機構
            "huduser.gov",          # 米国住宅都市開発省
            "freddiemac.com",       # フレディマック
            "fanniemae.com",        # ファニーメイ
            "retpc.jp",             # 不動産投資市場調査会
            "tdb.co.jp",            # 帝国データバンク
            
            # 不動産経済・ニュース
            "nar.realtor",          # 全米不動産協会
            "inman.com",            # 不動産ニュース
            "housingwire.com",      # 住宅市場ニュース
            "fudosankeisei.co.jp",  # 不動産経済研究所
            "nli-research.co.jp",   # ニッセイ基礎研究所
            "fudousan-keizai.co.jp", # 不動産経済
            "ken-eyenet.jp",        # 不動産流通研究所
            
            # 国際不動産
            "globalpropertyguide.com", # グローバル不動産ガイド
            "knightfrank.com",      # ナイトフランク不動産
            "juwai.com",            # 中国系国際不動産
            "propertyfinder.ae",    # 中東不動産
            "domain.com.au",        # オーストラリア不動産
            "rightmove.co.uk",      # イギリス不動産
            "immobilienscout24.de"  # ドイツ不動産
        ]
        self.recency_days = 31

    def create_real_estate_prompt(self):
        base_prompt = self.create_base_prompt()
        real_estate_prompt = f"""
{base_prompt}

# 不動産市場分析レポート

【検索条件】
- 対象: グローバル不動産市場、日本不動産市場、REIT市場
- 期間: 直近の動向

【出力形式】

## 1. グローバル不動産市場の概況

- 主要国・地域の不動産価格トレンド（米国、欧州、アジア太平洋）
- 金利環境（中央銀行の政策と市場反応）
- 商業不動産の稼働率と賃料動向（オフィス、商業施設、物流施設）

## 2. 日本の不動産市場

- 住宅市場の価格動向（東京、大阪、名古屋など主要都市別分析）
- オフィス市場の需給バランス（空室率、賃料推移、新規供給）

## 3. REIT市場分析

- グローバルREIT指数のパフォーマンス（セクター別比較）
- J-REITの最新動向（オフィス系、住宅系、商業系、物流系、ホテル系）

## 4. 不動産テクノロジーと新トレンド

- プロップテック企業の最新動向

## 5. 投資見通しとリスク分析

- 不動産市場のリスク要因（金利上昇、景気後退、規制変更）
- 有望な投資セクターと地域（成長性、利回り、安定性の観点から）
- 金融政策変更の潜在的影響（中央銀行の政策転換シナリオ）
- 中長期的な不動産市場の見通し（人口動態、テクノロジー、都市化の影響）

"""
        return real_estate_prompt

    def execute_search(self):
        prompt = self.create_real_estate_prompt()
        
        content = self.call_perplexity_api(
            prompt,
            self.domain_filter,
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_real_estate.md'
            
            if self.save_content(content, filename):
                # 投稿処理
                poster = RealEstatePostProcessor()
                success = poster.post_content()
                return success
                
        return False

def main():
    searcher = RealEstateSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()