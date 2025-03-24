# post_jp.py
from datetime import datetime
import os
from post_base import PostBase

class JPPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = [
            "日本株",
            "投資戦略",
            "業種別分析",
            "高BOE",
            "高ROE"
        ]
        self.categories = [
            "投資",
            "株式",
            
            "マーケット分析"
        ]

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_jp.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = f"日本株式市場 投資戦略レポート {current_date}"
            
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

if __name__ == "__main__":
    poster = JPPostProcessor()
    result = poster.post_content()
    print(f"投稿結果: {'成功' if result else '失敗'}")
