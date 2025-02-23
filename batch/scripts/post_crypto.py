# post_crypto.py
from datetime import datetime
import os
from post_base import PostBase

class CryptoPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["仮想通貨", "ビットコイン", "暗号資産"]
        self.categories = ["マーケット", "投資", "金融"]

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_crypto.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = f"仮想通貨市場レポート {current_date}"
            
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
    poster = CryptoPostProcessor()
    result = poster.post_content()
    print(f"投稿結果: {'成功' if result else '失敗'}")
