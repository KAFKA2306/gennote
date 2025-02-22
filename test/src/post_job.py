# post_job.py
from datetime import datetime
import os
from post_base import PostBase

class JobPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = [
            "転職市場",
            "求人動向",
            "業界分析",
            "キャリア",
            "採用動向",
            "人材市場"
        ]
        self.categories = [
            "転職・採用",
            "市場分析",
            "キャリア戦略"
        ]

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}_job.md'
            
            if not os.path.exists(filename):
                self.logger.error(f"ファイルが存在しません: {filename}")
                return False
                
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title = f"転職市場レポート {current_date}"
            
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
    poster = JobPostProcessor()
    result = poster.post_content()
    print(f"投稿結果: {'成功' if result else '失敗'}")
