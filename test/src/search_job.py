# search_job.py
from datetime import datetime
from search_base import SearchBase
from post_job import JobPostProcessor

class JobSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = [
            # 主要転職プラットフォーム
           #'doda.jp', 'type.jp', 'mynavi.jp/job',
           #'en-japan.com', 'career-tasu.jp',
            
            # 専門職特化型
            'careercross.com',    # 外資系・海外
            'dj-career.com',      # 金融専門
            'jacs-recruitment.com', # 製造業
            'quant-job.jp',       # クオンツ
            'aidemy.jp/career',   # AI専門
            'data-scientist-job.com', # データサイエンス
            
            # 製造業/エンジニア
            'monoist.atmarkit.co.jp/jobs',
            'engineer-factory.jp',
            
            # 業界データ/分析
            'works-i.com',      # リクルートワークス研究所
           #'hr-analytics.jp',  # HRアナリスト
            'mhlw.go.jp',       # 厚生労働省統計
            'jil.go.jp'         # 労働政策研究機構
        ]
        self.recency_days = 90

    def create_job_prompt(self):
        job_prompt = f"""
        # 求人紹介
        ## 年収800万円以上 超厳選ハイクラス求人レポート

        【検索戦略】
        1. 各カテゴリ別に独立した検索を3段階で実施：
        - 第1検索：主要転職サイトの公式APIから生データ取得
        - 第2検索：企業公式採用ページのクローリング
        - 第3検索：HRアナリストのレポート分析

        2. 検索条件（AND条件）：
        - 年収下限：800万円以上
        - 公開期間：30日以内
        - 実績あり企業（上場企業/VCから100億円以上調達）

        【厳選カテゴリ】 
        |||
        |---|---|
        |💻 データサイエンス|AI/ML/DL・ビッグデータ分析・統計モデリング|
        |🌏 グローバル管理職|海外拠点統括・多国籍チームマネジメント|
        |✈️ 海外駐在職|北米/欧州/アジア主要都市への採用|
        |🤖 AI専門職|生成AI・LLM・コンピュータビジョン|
        |📈 DX推進職|デジタルトランスフォーメーション戦略|
        |💼 コンサルタント|戦略/IT/経営コンサルティング|
        |🏦 総合商社|資源開発・グローバルトレーディング|
        |💰 金融専門職|クオンツ・M&A・投資分析|

        【出力要件】
        各求人項目で必須チェック：
        ✅ 企業公式採用ページの直接リンク
        ✅ 年収レンジの数値明示
        ✅ 必須資格/経験年数の明文化
        ✅ 業界/職種/技術スキルの明示
        ✅ 職場環境/福利厚生の詳細記載

        【品質管理】
        以下の基準を満たさない求人は除外：
        ❌ 年収記載のない求人、最低年収が800万円未満の求人
        
        """
        return self.create_base_prompt() + job_prompt

    def execute_search(self):
        prompt = self.create_job_prompt()
        content = self.call_perplexity_api(
            prompt, 
            self.domain_filter, 
            recency_days=self.recency_days
        )
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_job.md'
            if self.save_content(content, filename):
                poster = JobPostProcessor()
                success = poster.post_content()
                return success
        return False

if __name__ == "__main__":
    searcher = JobSearcher()
    searcher.execute_search()



"""

以下が年収800万円以上のハイクラス求人情報の厳選リストです：

### 💼 Geniee  
**[[AIテックプロダクト開発]](pplx://action/followup)** `¥9M ~ ¥20M`  
- 🔗 [求人詳細](https://japan-dev.com/ml-data-science-jobs-in-japan?lang=jp)  
- 📍 東京/フルリモート可  
- ⚙️ 自然言語処理/PyTorch/大規模言語モデル  
- 📈 AI業界最高水準 年収成長率12%  

### 💼 PayPay  
**[[支払いプラットフォーム開発]](pplx://action/followup)** `¥12M ~ ¥16M`  
- 🔗 [求人詳細](https://japan-dev.com/ml-data-science-jobs-in-japan?lang=jp)  
- 📍 東京/ハイブリッド勤務  
- ⚙️ リアルタイム決済システム/分散処理  
- 📈 FinTech業界トップクラス 需要急増中  

### 💼 日産自動車  
**[[グローバル人事戦略]](pplx://action/followup)** `¥10M ~ ¥15M`  
- 🔗 [求人詳細](https://tenshoku.mynavi.jp/global/list/min0800/kw%E3%82%B0%E3%83%AD%E3%83%BC%E3%83%90%E3%83%AB%E4%BA%BA%E4%BA%8B/)  
- 📍 横浜本社/海外出張あり  
- ⚙️ 国際人事制度設計/英語ビジネスレベル  
- 📈 自動車業界最高水準待遇  

### 💼 三菱ケミカル  
**[[グローバルHRISマネージャー]](pplx://action/followup)** `¥10M ~ ¥12.5M`  
- 🔗 [求人詳細](https://tenshoku.mynavi.jp/global/list/min0800/kw%E3%82%B0%E3%83%AD%E3%83%BC%E3%83%90%E3%83%AB%E4%BA%BA%E4%BA%8B/)  
- 📍 東京本社/ハイブリッド  
- ⚙️ SAP SuccessFactors/多国籍チーム管理  
- 📈 化学業界最高クラス福利厚生  

### 💼 デクセリアルズ  
**[[半導体プロセスエンジニア]](pplx://action/followup)** `¥10M ~ ¥12M`  
- 🔗 [求人詳細](https://doda.jp/DodaFront/View/JobSearchList/j_ind__0208S/-oc__044402S/-ha__80,0/-preBtn__2/)  
- 📍 愛知県大府市  
- ⚙️ 微細加工技術/クリーンルーム経験  
- 📈 半導体需要急拡大に伴い年収15%UP  

### 💼 日本IBM  
**[[量子コンピューティング研究員]](pplx://action/followup)** `¥12M ~ ¥18M`  
- 🔗 [求人詳細](https://jp.indeed.com/q-data-scientist-900%E4%B8%87%E5%86%86-l-%E6%9D%B1%E4%BA%AC%E9%83%BD-%E6%B1%82%E4%BA%BA.html)  
- 📍 東京・品川  
- ⚙️ Qiskit/量子アルゴリズム開発  
- 📈 量子技術分野で国内最高待遇  

### 💼 楽天グループ  
**[[AIプラットフォーム開発]](pplx://action/followup)** `¥11M ~ ¥14M`  
- 🔗 [求人詳細](https://japan-dev.com/ml-data-science-jobs-in-japan?lang=jp)  
- 📍 東京・世田谷/リモート可  
- ⚙️ TensorFlow/Kubernetes/大規模分散処理  
- 📈 デジタル変革推進で需要急増  

### 💼 三菱UFJ銀行  
**[[デリバティブクオンツ]](pplx://action/followup)** `¥15M ~ ¥25M`  
- 🔗 [求人詳細](https://doda.jp/DodaFront/View/JobSearchList/j_ar__99/-oc__01L/-ha__80,0/-preBtn__1/)  
- 📍 東京・丸の内  
- ⚙️ Python/C++/確率微分方程式  
- 📈 金融業界最高水準 ボーナス含む  

### 💼 トヨタ自動車  
**[[自動運転AI開発]](pplx://action/followup)** `¥12M ~ ¥20M`  
- 🔗 [求人詳細](https://www.r-agent.com/kensaku/syokusyu/ocpt1-10/ocpt2-01/ocpt3-05/select03-02/select01-06/)  
- 📍 愛知県豊田市  
- ⚙️ ROS/Deep Learning/センサフュージョン  
- 📈 自動車業界で最高技術評価  

### 💼 ソフトバンク  
**[[DX推進戦略コンサルタント]](pplx://action/followup)** `¥13M ~ ¥18M`  
- 🔗 [求人詳細](https://mid-tenshoku.com/backoffice/jinji/800man/17/)  
- 📍 東京・汐留  
- ⚙️ デジタルトランスフォーメーション戦略  
- 📈 成長率28%の急成長領域
"""