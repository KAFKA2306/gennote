# real_estate_hidden_value_research.py

from datetime import datetime
import logging
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import re
from search_base import SearchBase
from post_base import PostBase

class RealEstateHiddenValuePostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["不動産含み益", "株式投資", "バリュー投資", "隠れ資産", "企業価値", "日本株"]
        self.categories = ["マーケット", "投資", "不動産", "株式"]
        
        # Yahoo Finance APIのエンドポイント
        self.yahoo_finance_url = "https://finance.yahoo.co.jp/quote/"
    
    def format_ranking_table(self, hidden_value_data):
        """ランキングテーブルをマークダウン形式でフォーマットする"""
        table_md = "| 順位 | 企業名 | コード | 不動産含み益(億円) | 時価総額(億円) | 含み益/時価総額比率 | Yahoo Finance |\n"
        table_md += "|------|--------|--------|-----------------|--------------|------------------|---------------|\n"
        
        for i, company in enumerate(hidden_value_data, 1):
            table_md += f"| {i} | {company['name']} | {company['code']} | "
            table_md += f"{company['hidden_value']:.1f} | {company['market_cap']:.1f} | {company['ratio']:.2f} |"
            table_md += f"[Link](https://finance.yahoo.co.jp/quote/{company['code']}) |\n"
            
        return table_md

    def add_analysis_content(self, content, hidden_value_data):
        """分析コンテンツを追加する"""
        updated_content = content
        
        # トップ5企業の詳細分析
        if len(hidden_value_data) >= 5:
            updated_content += "\n\n## トップ5企業の詳細分析\n\n"
            
            for i, company in enumerate(hidden_value_data[:5], 1):
                updated_content += f"### {i}. {company['name']} ({company['code']})\n\n"
                updated_content += f"- **不動産含み益**: {company['hidden_value']:.1f}億円\n"
                updated_content += f"- **時価総額**: {company['market_cap']:.1f}億円\n"
                updated_content += f"- **含み益/時価総額比率**: {company['ratio']:.2f}\n"
                updated_content += f"- **主要保有不動産**: {company.get('major_properties', '情報なし')}\n"
                updated_content += f"- **最近の不動産戦略**: {company.get('recent_strategy', '情報なし')}\n\n"
        
        # 業種別の含み益比率分析
        updated_content += "\n\n## 業種別の不動産含み益分析\n\n"
        updated_content += "不動産含み益が多い業種としては、以下が挙げられます：\n\n"
        updated_content += "1. **商社・卸売業** - 長年の事業展開で取得した都心の一等地に多くの不動産を保有\n"
        updated_content += "2. **製造業** - 工場用地や本社ビルなど大規模な不動産を保有\n"
        updated_content += "3. **小売業** - 店舗用地を多数保有する企業が多い\n"
        updated_content += "4. **鉄道・運輸業** - 駅周辺の開発用地や沿線不動産を多数保有\n\n"
        
        # 投資戦略
        updated_content += "## 不動産含み益に着目した投資戦略\n\n"
        updated_content += "不動産含み益の高い企業に投資する際の注意点：\n\n"
        updated_content += "- **含み益の実現可能性** - 保有不動産が売却可能かどうかを見極める\n"
        updated_content += "- **本業の収益性** - 不動産に頼らない本業の収益力も重要\n"
        updated_content += "- **経営陣の姿勢** - 株主還元や資産効率向上への意欲\n"
        updated_content += "- **税制面の考慮** - 不動産売却時の税負担\n\n"
        
        return updated_content

    def post_content(self, hidden_value_data):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_real_estate_hidden_value.md'
            
            # 基本コンテンツの作成
            content = f"# 日本企業の不動産含み益ランキング分析 {current_date}\n\n"
            content += "## はじめに\n\n"
            content += "多くの日本企業は長年にわたり保有している不動産に多額の含み益を抱えています。"
            content += "これらの「隠れ資産」は企業価値を測る上で重要な指標となりますが、"
            content += "財務諸表上では適切に評価されていないことが多いです。\n\n"
            content += "本レポートでは、不動産含み益が時価総額に対して高い比率を持つ企業をランキング形式で紹介します。"
            content += "これらの企業は潜在的なバリュー株として注目に値するかもしれません。\n\n"
            
            content += "## 不動産含み益/時価総額ランキング\n\n"
            content += "以下は、不動産含み益の時価総額に対する比率が高い企業のランキングです。"
            content += "この比率が高いほど、市場が企業の保有資産を過小評価している可能性があります。\n\n"
            
            content += self.format_ranking_table(hidden_value_data)
            
            # 分析コンテンツの追加
            content = self.add_analysis_content(content, hidden_value_data)
            
            # ファイルへの保存
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # ブログへの投稿
            title = f"日本企業の不動産含み益ランキング分析 {current_date}"
            
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

class RealEstateHiddenValueSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            "nikkei.com",
            "reuters.com",
            "bloomberg.co.jp",
            "minkabu.jp",
            "morningstar.co.jp",
            "kabutan.jp",
            "jpx.co.jp",
            "tdb.co.jp",
            "mlit.go.jp",
            "fsa.go.jp",
            "mof.go.jp",
            "ir-bank.jp",
            "buffett-code.com",
            "kabudragon.com",
            "ullet.com",
            "kabupro.jp",
            "zaimu-express.net"
        ]
        self.recency_days = 365  # 不動産含み益情報は長期的なものなので期間を長めに設定
        
        # 不動産含み益が多いとされる日本企業リスト
        self.target_companies = [
            {"code": "8001.T", "name": "伊藤忠商事"},
            {"code": "8002.T", "name": "丸紅"},
            {"code": "8015.T", "name": "豊田通商"},
            {"code": "8031.T", "name": "三井物産"},
            {"code": "8053.T", "name": "住友商事"},
            {"code": "8058.T", "name": "三菱商事"},
            {"code": "9001.T", "name": "東武鉄道"},
            {"code": "9005.T", "name": "東京急行電鉄"},
            {"code": "9007.T", "name": "小田急電鉄"},
            {"code": "9008.T", "name": "京王電鉄"},
            {"code": "9009.T", "name": "京成電鉄"},
            {"code": "9020.T", "name": "JR東日本"},
            {"code": "9021.T", "name": "西日本旅客鉄道"},
            {"code": "9022.T", "name": "中央日本鉄道"},
            {"code": "3086.T", "name": "J.フロント リテイリング"},
            {"code": "3099.T", "name": "三越伊勢丹ホールディングス"},
            {"code": "8233.T", "name": "高島屋"},
            {"code": "8252.T", "name": "丸井グループ"},
            {"code": "8267.T", "name": "イオン"},
            {"code": "9983.T", "name": "ファーストリテイリング"}
        ]

    def get_market_cap(self, ticker_code):
        """Yahoo Financeから時価総額を取得する"""
        try:
            ticker = yf.Ticker(ticker_code)
            info = ticker.info
            
            if 'marketCap' in info:
                # 円単位を億円に変換
                return info['marketCap'] / 100000000
            else:
                # 情報が取得できない場合は代替手段を試みる
                self.logger.warning(f"時価総額情報が取得できませんでした: {ticker_code}")
                return self.get_market_cap_alternative(ticker_code)
                
        except Exception as e:
            self.logger.error(f"時価総額取得エラー: {str(e)}")
            return self.get_market_cap_alternative(ticker_code)

    def get_market_cap_alternative(self, ticker_code):
        """代替手段で時価総額を取得する（スクレイピングなど）"""
        try:
            url = f"https://finance.yahoo.co.jp/quote/{ticker_code}"
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 時価総額を含む要素を探す
                market_cap_element = soup.find(text=re.compile('時価総額'))
                if market_cap_element and market_cap_element.parent:
                    value_element = market_cap_element.parent.find_next('dd')
                    if value_element:
                        # 「123億4,567万円」のような形式から数値を抽出
                        value_text = value_element.text.strip()
                        value_text = re.sub(r'[^\d.]', '', value_text)
                        if value_text:
                            return float(value_text) / 100  # 万円単位を億円に変換
            
            self.logger.warning(f"代替手段でも時価総額を取得できませんでした: {ticker_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"代替時価総額取得エラー: {str(e)}")
            return None

    def create_hidden_value_prompt(self):
        """不動産含み益に関する調査プロンプトを作成する"""
        base_prompt = self.create_base_prompt()
        
        # 企業リストをテキスト形式に変換
        companies_text = "\n".join([f"- {company['name']} ({company['code']})" for company in self.target_companies])
        
        hidden_value_prompt = f"""
{base_prompt}

# 日本企業の不動産含み益調査

【調査対象企業】
{companies_text}

【調査内容】
- 各企業が保有する不動産の簿価と時価の差額（含み益）
- 含み益の時価総額に対する比率
- 含み益が大きい主な不動産の所在地・用途
- 不動産戦略（売却予定、再開発計画など）

【出力形式】
以下の形式でJSON形式のデータを出力してください。

```json
{{
  "企業コード": {{
    "hidden_value": 不動産含み益（億円）,
    "major_properties": "主要保有不動産の概要",
    "recent_strategy": "最近の不動産戦略"
  }},
  ...
}}
```

【注意点】
- 含み益の金額は億円単位で、数値のみを出力
- 情報が入手できない場合は、業種や企業規模から妥当な推定値を出力
- 主要保有不動産と不動産戦略は簡潔に記述
"""
        return hidden_value_prompt

    def get_hidden_value_data(self):
        """不動産含み益データを取得する"""
        prompt = self.create_hidden_value_prompt()
        
        # APIを呼び出して不動産含み益データを取得
        response_text = self.call_perplexity_api(
            prompt,
            self.domain_filter,
            recency_days=self.recency_days
        )
        
        if not response_text:
            self.logger.error("不動産含み益データの取得に失敗しました")
            return {}
            
        # JSONデータを抽出
        json_match = re.search(r'``````', response_text, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)
            try:
                return eval(json_str)  # JSONを辞書に変換
            except Exception as e:
                self.logger.error(f"JSONパースエラー: {str(e)}")
                return {}
        else:
            self.logger.error("JSONデータが見つかりませんでした")
            return {}

    def calculate_hidden_value_ratio(self):
        """不動産含み益と時価総額の比率を計算し、ランキングを作成する"""
        # 不動産含み益データを取得
        hidden_value_data = self.get_hidden_value_data()
        
        result = []
        
        for company in self.target_companies:
            code = company["code"]
            name = company["name"]
            
            # 不動産含み益を取得
            company_data = hidden_value_data.get(code, {})
            hidden_value = company_data.get("hidden_value", 0)
            
            # 時価総額を取得
            market_cap = self.get_market_cap(code)
            
            # 時価総額が取得できない場合はスキップ
            if market_cap is None:
                continue
                
            # 比率を計算
            ratio = hidden_value / market_cap if market_cap > 0 else 0
            
            result.append({
                "code": code,
                "name": name,
                "hidden_value": hidden_value,
                "market_cap": market_cap,
                "ratio": ratio,
                "major_properties": company_data.get("major_properties", ""),
                "recent_strategy": company_data.get("recent_strategy", "")
            })
        
        # 比率でソート
        result.sort(key=lambda x: x["ratio"], reverse=True)
        
        return result

    def execute_search(self):
        try:
            # 不動産含み益と時価総額の比率を計算
            hidden_value_ranking = self.calculate_hidden_value_ratio()
            
            if not hidden_value_ranking:
                self.logger.error("ランキングデータの作成に失敗しました")
                return False
                
            # 投稿処理
            poster = RealEstateHiddenValuePostProcessor()
            success = poster.post_content(hidden_value_ranking)
            
            return success
        except Exception as e:
            self.logger.error(f"調査実行エラー: {str(e)}")
            return False

def main():
    searcher = RealEstateHiddenValueSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()