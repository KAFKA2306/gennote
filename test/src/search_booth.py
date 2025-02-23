from datetime import datetime
from search_base import SearchBase
from post_booth import BOOTHPostProcessor

class BOOTHSearcher(SearchBase):
    def __init__(self):
        super().__init__()
        self.domain_filter = ["booth.pm"]

    def create_booth_prompt(self):
        base_prompt = self.create_base_prompt()
        booth_prompt = f"""
        {base_prompt}

        ## BOOTH新着3D衣装レポート

        【検索条件】
        - サイト: BOOTH限定
        - カテゴリ: VRChat用3D衣装
        - 期間: 直近7日間
        - 価格帯: 500円～10,000円

        【出力形式】
        ## [商品名](https://booth.pm/ja/items/商品ID)
        - 💰 価格: xxx円
        - 🎨 クリエイター: [ショップ名](ショップURL)
        - ⭐ 更新日: YYYY-MM-DD

        【商品特徴】
        3-4行で商品の特徴を説明
        """
        return booth_prompt

    def execute_search(self):
        prompt = self.create_booth_prompt()
        content = self.call_perplexity_api(prompt, self.domain_filter)
        
        if content:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md'
            if self.save_content(content, filename):
                # 投稿処理
                poster = BOOTHPostProcessor()
                success = poster.post_content()
                return success
        return False

def main():
    searcher = BOOTHSearcher()
    searcher.execute_search()

if __name__ == "__main__":
    main()
