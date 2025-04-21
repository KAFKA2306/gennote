import os
import json
import time
import logging
from datetime import datetime, timezone, timedelta
import re
import csv
import yfinance as yf
import requests

# --- 基底クラスのインポート ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
try:
    from search_base import SearchBase
    from post_base import PostBase
except ImportError:
    logging.critical("基底クラス SearchBase または PostBase のインポートに失敗しました。")
    raise

# --- ロギング設定 ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 定数 ---
PROMPT_DIR = os.path.join(SCRIPT_DIR, 'prompt')
FIND_STOCK_PROMPT_PATH = os.path.join(PROMPT_DIR, 'find_most_rising_stock_name_and_code.md')
CATEGORY_PROMPT_DIR = os.path.join(PROMPT_DIR, 'category_prompts')
OUTPUT_DIR = os.path.join(BASE_DIR, 'test', 'output')
EXCLUDED_STOCKS_FILE = os.path.join(SCRIPT_DIR, 'excluded_stocks.csv')

DOMAIN_FILTER = [
    'nikkei.com', 'bloomberg.co.jp', 'finance.yahoo.co.jp',
    'kabutan.jp', 'minkabu.jp', 'toyokeizai.net', 'diamond.jp',
    'reuters.co.jp', 'disclosure.edinet-fsa.go.jp', 'jpx.co.jp',
]
RECENCY_DAYS_DETAIL = 7
RECENCY_DAYS_FIND = 1
BLOG_TAGS_COMMON = ["株式投資", "個別株", "銘柄分析", "日本株", "JSONデータ"]
BLOG_CATEGORIES = ["マーケット", "投資", "金融"]
CATEGORIES_TO_SEARCH = [
    "basic_info", "business_info", "financial_info",
    "management_strategy", "analyst_evaluation",
]
JST = timezone(timedelta(hours=+9), 'JST')

class StockSearcherPosterFull(SearchBase, PostBase):

    def __init__(self):
        SearchBase.__init__(self)
        PostBase.__init__(self)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        self.excluded_codes = self._load_excluded_stocks()
        logger.info(f"除外リスト読込 ({len(self.excluded_codes)}件): {EXCLUDED_STOCKS_FILE}")

    def _load_excluded_stocks(self):
        excluded_codes = set()
        if os.path.exists(EXCLUDED_STOCKS_FILE):
            try:
                with open(EXCLUDED_STOCKS_FILE, 'r', encoding='utf-8', newline='') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and re.match(r'^\d{4}$', row[0]):
                            excluded_codes.add(row[0])
            except Exception as e: logger.error(f"除外リスト読込エラー: {e}")
        return excluded_codes

    def _save_excluded_stock(self, ticker_code):
        if ticker_code not in self.excluded_codes:
            try:
                with open(EXCLUDED_STOCKS_FILE, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([ticker_code])
                self.excluded_codes.add(ticker_code)
                logger.info(f"除外リストに {ticker_code} を追加: {EXCLUDED_STOCKS_FILE}")
            except Exception as e: logger.error(f"除外リスト書込エラー ({ticker_code}): {e}")

    def _call_perplexity_api(self, prompt, domain_filter, recency_days):
        response_str = None
        try:
            response_str = self.call_perplexity_api(prompt, domain_filter, recency_days=recency_days)
            if response_str:
                json_match = re.search(r'\{.*\}', response_str, re.DOTALL)
                if json_match: return json_match.group(0)
        except Exception as e: logger.error(f"API呼出エラー: {e}")
        return None

    def find_most_rising_stock(self):
        logger.info("1. 急騰銘柄検索 (除外考慮)")
        try:
            with open(FIND_STOCK_PROMPT_PATH, 'r', encoding='utf-8') as f:
                find_stock_prompt_template = f.read()
        except FileNotFoundError:
            logger.error(f"プロンプト欠落: {FIND_STOCK_PROMPT_PATH}"); return None, None

        exclusion_instruction = ""
        if self.excluded_codes:
            codes_str = ", ".join(sorted(list(self.excluded_codes)))
            exclusion_instruction = f"\n\n## 除外指示\n以下の証券コードの銘柄は**絶対に**選択しないでください: [{codes_str}]"

        if "## 実行指示" in find_stock_prompt_template:
            find_stock_prompt = find_stock_prompt_template.replace("## 実行指示", f"{exclusion_instruction}\n\n## 実行指示")
        else: find_stock_prompt = find_stock_prompt_template + exclusion_instruction

        stock_info_json_str = self._call_perplexity_api(find_stock_prompt, DOMAIN_FILTER, RECENCY_DAYS_FIND)
        if not stock_info_json_str: return None, None

        stock_name, ticker_code = None, None
        try:
            stock_info = json.loads(stock_info_json_str)
            stock_name = stock_info.get("法人名")
            ticker_code = stock_info.get("証券コード")
            if isinstance(ticker_code, int): ticker_code = str(ticker_code)
            if ticker_code in self.excluded_codes:
                logger.warning(f"   -> 抽出銘柄 {stock_name}({ticker_code}) は除外対象。スキップ。"); return None, None
            if stock_name and ticker_code and re.match(r'^\d{4}$', ticker_code):
                logger.info(f"   -> 特定: {stock_name} ({ticker_code})"); return stock_name, ticker_code
        except json.JSONDecodeError: pass

        match_name = re.search(r'["\']法人名["\']\s*:\s*["\']([^"\']+)["\']', stock_info_json_str)
        match_code = re.search(r'["\']証券コード["\']\s*:\s*["\']?(\d{4})["\']?', stock_info_json_str)
        if match_name and match_code:
            stock_name = match_name.group(1)
            ticker_code = match_code.group(1)
            if ticker_code in self.excluded_codes:
                logger.warning(f"   -> 代替抽出銘柄 {stock_name}({ticker_code}) は除外対象。スキップ。"); return None, None
            logger.info(f"   -> 代替抽出: {stock_name} ({ticker_code})"); return stock_name, ticker_code

        logger.error("   -> 銘柄特定失敗"); return None, None

    def get_stock_data_from_yfinance(self, ticker_code):
        logger.info(f"2. yfinanceデータ取得 ({ticker_code})")
        ticker_jp = f"{ticker_code}.T"
        try:
            ticker = yf.Ticker(ticker_jp)
            info = ticker.info
            hist = ticker.history(period="2d")
            if not info or hist.empty: return None
            data_date = datetime.now(JST).strftime("%Y-%m-%d")
            stock_data = {"株価": {"現在値": hist['Close'].iloc[-1], "基準日": data_date},
                          "時価総額": {"金額": info.get('marketCap') / 1_000_000 if info.get('marketCap') else None, "基準日": data_date},
                          "発行済株式総数": info.get('sharesOutstanding'), "バリュエーション指標": [],
                          "配当利回り": info.get('dividendYield') * 100 if info.get('dividendYield') else None}
            if info.get('trailingPE'): stock_data["バリュエーション指標"].append({"名称": "PER", "値": info['trailingPE'], "基準日": data_date})
            if info.get('priceToBook'): stock_data["バリュエーション指標"].append({"名称": "PBR", "値": info['priceToBook'], "基準日": data_date})
            logger.info(f"   -> yfinanceデータ取得成功"); return stock_data
        except Exception as e: logger.error(f"   -> yfinanceエラー: {e}"); return None

    def _load_category_prompt(self, category, stock_name, ticker_code):
        prompt_path = os.path.join(CATEGORY_PROMPT_DIR, f"{category}.md")
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f: prompt_template = f.read()
            prompt = prompt_template.replace("{stock_name}", stock_name).replace("{ticker_code}", ticker_code)
            prompt_lines = prompt.splitlines()
            cleaned_lines = [line for line in prompt_lines if not line.strip().startswith('## 実行指示') and not line.strip().startswith('**企業:**')]
            return "\n".join(cleaned_lines).strip()
        except FileNotFoundError: logger.warning(f"   -> プロンプト欠落: {prompt_path}"); return None

    def search_detailed_info_by_category(self, stock_name, ticker_code, category):
        logger.info(f"3. カテゴリ情報検索: {category}")
        prompt = self._load_category_prompt(category, stock_name, ticker_code)
        if not prompt: return None
        response_text = self._call_perplexity_api(prompt, DOMAIN_FILTER, RECENCY_DAYS_DETAIL)
        if not response_text: return None
        try:
            data = json.loads(response_text)
            category_key_map = {"basic_info": "基本情報", "business_info": "事業情報", "financial_info": "財務情報",
                                "management_strategy": "経営戦略", "analyst_evaluation": "証券アナリスト評価"}
            expected_key = category_key_map.get(category)
            if expected_key and expected_key in data: logger.info(f"   -> {category} データ取得成功"); return data[expected_key]
            elif data and isinstance(data, dict) and list(data.keys())[0] == expected_key:
                 logger.info(f"   -> {category} データ取得成功 (ルートキー)"); return data[expected_key]
            else: logger.warning(f"   -> {category} データ構造不一致"); return data
        except Exception as e: logger.error(f"   -> {category} データ処理エラー: {e}"); return None

    def merge_data(self, llm_data, yfinance_data, stock_name, ticker_code):
        logger.info("4. データ統合")
        final_data = {"企業データ": [{}]}
        company_data = final_data["企業データ"][0]
        category_map = {"basic_info": "基本情報", "business_info": "事業情報", "financial_info": "財務情報",
                        "management_strategy": "経営戦略", "analyst_evaluation": "証券アナリスト評価"}
        for category_code in CATEGORIES_TO_SEARCH:
             json_key = category_map.get(category_code)
             if json_key: company_data[json_key] = llm_data.get(category_code, {})

        if company_data.get("基本情報") is None: company_data["基本情報"] = {}
        company_data["基本情報"]["法人名"] = stock_name
        company_data["基本情報"]["証券コード"] = ticker_code
        company_data["基本情報"]["最終更新日時"] = datetime.now(JST).isoformat(timespec='seconds')

        market_info = {}
        if yfinance_data:
            market_info["株価"] = yfinance_data.get("株価")
            market_info["時価総額"] = yfinance_data.get("時価総額")
            market_info["発行済株式総数"] = yfinance_data.get("発行済株式総数")
            market_info["バリュエーション指標"] = yfinance_data.get("バリュエーション指標", [])
            market_info["配当情報"] = {"配当利回り": yfinance_data.get("配当利回り")}
        company_data["市場・株式情報"] = market_info
        logger.info("   -> データ統合完了"); return final_data

    def save_to_json(self, data, stock_name, ticker_code):
        logger.info("5. JSONファイル保存")
        filename = None
        try:
            current_date = datetime.now(JST).strftime("%Y%m%d")
            filename_safe_name = re.sub(r'[\\/:*?"<>|]+', '_', stock_name)
            filename = os.path.join(OUTPUT_DIR, f"{current_date}_{filename_safe_name}_{ticker_code}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"   -> 保存成功: {filename}")
        except Exception as e: logger.error(f"   -> 保存失敗: {e}"); filename = None
        return filename

    def execute_search_and_post(self):
        logger.info("=== 処理開始 ===")
        start_time = time.time()

        stock_name, ticker_code = self.find_most_rising_stock()
        if not stock_name or not ticker_code: logger.error("処理中断: 検索対象銘柄が見つかりませんでした。"); return False

        yfinance_data = self.get_stock_data_from_yfinance(ticker_code)
        if yfinance_data is None: yfinance_data = {}

        llm_detailed_data = {}
        for category in CATEGORIES_TO_SEARCH:
            category_data = self.search_detailed_info_by_category(stock_name, ticker_code, category)
            if category_data: llm_detailed_data[category] = category_data
            time.sleep(0.2)

        final_stock_data = self.merge_data(llm_detailed_data, yfinance_data, stock_name, ticker_code)

        json_filepath = self.save_to_json(final_stock_data, stock_name, ticker_code)
        # JSONファイルが正常に保存された場合のみ、その内容をブログに投稿する
        if not json_filepath:
             logger.error("JSON保存失敗のためブログ投稿スキップ"); return False

        logger.info("6. ブログコンテンツ生成 (JSON)")
        blog_content = "# JSONデータ読込エラー"
        try:
             # 保存したJSONファイルを読み込み、ブログコンテンツとする
             with open(json_filepath, 'r', encoding='utf-8') as f:
                  # ファイル内容全体を読み込み、コードブロックで囲む
                  json_string_from_file = f.read()
                  blog_content = f"""
```
{json_string_from_file}
```
"""



             logger.info(f"   -> ブログ用JSON文字列生成完了 (From: {json_filepath})")
        except Exception as e:
             logger.error(f"   -> JSONファイル読込/文字列生成エラー: {e}")

        logger.info("7. はてなブログ投稿")
        now_jst = datetime.now(JST)
        current_date_title = now_jst.strftime("%Y-%m-%d")
        blog_title = f"【注目銘柄】{stock_name}({ticker_code}) - {current_date_title}"
        post_tags = list(set([stock_name, ticker_code] + BLOG_TAGS_COMMON))

        success = False
        try:
            entry_xml = self.create_entry_xml(
                title=blog_title, content=blog_content, tags=post_tags, categories=BLOG_CATEGORIES
            )
            success, url = self.post_to_hatena(entry_xml)
            if success:
                logger.info(f"   -> 投稿成功: {url}"); self._save_excluded_stock(ticker_code)
            else: logger.error("   -> 投稿失敗 (API応答)")
        except Exception as e: logger.error(f"   -> 投稿処理エラー: {e}")

        end_time = time.time()
        logger.info(f"=== 処理完了 ({end_time - start_time:.2f}秒) ===")
        return success

def main():
    try:
        searcher_poster = StockSearcherPosterFull()
        searcher_poster.execute_search_and_post()
    except Exception as e: logger.critical(f"実行エラー: {e}", exc_info=True)

if __name__ == "__main__":
    main()
