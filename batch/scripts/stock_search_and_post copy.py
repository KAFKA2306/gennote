# stock_search_and_post.py
from datetime import datetime
import os
import json
from search_base import SearchBase
from post_base import PostBase

class StockSearcherPoster(SearchBase, PostBase):
    def __init__(self):
        SearchBase.__init__(self)
        PostBase.__init__(self)
        self.domain_filter = [
            'nikkei.com',
            'bloomberg.co.jp',
            'finance.yahoo.co.jp',
            'kabutan.jp',
            ' MinKabu Press',
            'toyokeizai.net',
            'diamond.jp',
            'reuters.co.jp'
        ]
        self.recency_days = 7
        self.tags = ["株式投資", "個別株"]
        self.categories = ["マーケット", "投資", "金融"]

    def execute_search_and_post(self):
        try:
            # 1. Find most rising stock
            find_stock_prompt_path = 'batch/scripts/prompt/find_most_rising_stock_name_and_code.md'
            with open(find_stock_prompt_path, 'r', encoding='utf-8') as f:
                find_stock_prompt = f.read()
            
            stock_info_json = self.call_perplexity_api(find_stock_prompt, self.domain_filter, recency_days=1)
            if not stock_info_json:
                self.logger.error("急騰銘柄の検索に失敗しました。")
                return False

            try:
                stock_info = json.loads(stock_info_json)
                stock_name = stock_info.get("法人名")
                ticker_code = stock_info.get("証券コード")
                if not stock_name or not ticker_code:
                    self.logger.error(f"銘柄名または証券コードがJSONから抽出できませんでした: {stock_info_json}")
                    return False
            except json.JSONDecodeError as e:
                self.logger.error(f"JSONデコードエラー: {e}. レスポンス: {stock_info_json}")
                # Try alternative method if JSON decoding fails
                self.logger.info("JSONデコードエラーが発生したため、代替方法を試します。")
                import re
                match = re.search(r'"法人名":\s*"([^"]+)",\s*"証券コード":\s*"(\d+)"', stock_info_json)
                if match:
                    stock_name = match.group(1)
                    ticker_code = match.group(2)
                    self.logger.info(f"代替方法で銘柄名と証券コードを抽出: {stock_name}, {ticker_code}")
                else:
                    self.logger.error(f"代替方法でも銘柄名または証券コードを抽出できませんでした: {stock_info_json}")
                    return False

            # 2. Search detailed stock information
            search_info_prompt_path = 'batch/scripts/prompt/search_stock_information_then_fill_in json_format.md'
            with open(search_info_prompt_path, 'r', encoding='utf-8') as f:
                search_info_prompt_template = f.read()

            search_info_prompt = search_info_prompt_template + f"\n**企業:** {stock_name} ({ticker_code})"
            detailed_stock_info_json = self.call_perplexity_api(search_info_prompt, self.domain_filter, recency_days=self.recency_days)
            if not detailed_stock_info_json:
                self.logger.error(f"{stock_name}({ticker_code})の詳細情報検索に失敗しました。")
                return False

            # 2. Save detailed stock information to JSON file
            current_date = datetime.now().strftime("%Y-%m-%d")
            output_dir = 'test/output'
            os.makedirs(output_dir, exist_ok=True)
            filename = os.path.join(output_dir, f"{current_date}_{stock_name}_{ticker_code}.json")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json.loads(detailed_stock_info_json), f, indent=2, ensure_ascii=False)
            self.logger.info(f"詳細情報をJSONファイルに保存: {filename}")

            # 3. Create Hatena Blog post
            title = f"本日の銘柄{{{stock_name},{ticker_code}}} {current_date}"
            content = f"""# {stock_name}({ticker_code}) {current_date} 株式情報レポート\n\n{detailed_stock_info_json}"""
            entry_xml = self.create_entry_xml(
                title=title,
                content=content,
                tags=[stock_name, "株式投資", "個別株"],
                categories=self.categories
            )
            success, url = self.post_to_hatena(entry_xml)
            if success:
                self.logger.info(f"投稿URL: {url}")
            return success

        except Exception as e:
            self.logger.error(f"処理中にエラーが発生しました: {e}")
            return False

def main():
    searcher_poster = StockSearcherPoster()
    searcher_poster.execute_search_and_post()

if __name__ == "__main__":
    main()