from datetime import datetime
from post_base import PostBase

class BOOTHPostProcessor(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["BOOTH", "VRChat", "3Dモデル"]

    def clean_booth_content(self, content):
        """BOOTH特有のコンテンツクリーニング"""
        content = super().clean_html(content)
        # BOOTH特有の整形ルールを追加
        content = content.replace('商品ID', 'item_id')
        return content

    def post_content(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            filename = f'M:/ML/ChatGPT/gennote/test/output/{current_date}.md'

            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            cleaned_content = self.clean_booth_content(content)
            title = f"BOOTH 3D衣装レポート {current_date}"
            
            entry_xml = self.create_entry_xml(
                title=title,
                content=cleaned_content,
                tags=self.tags
            )

            success, url = self.post_to_hatena(entry_xml)
            if success:
                self.logger.info(f"Posted successfully: {url}")
            return success

        except Exception as e:
            self.logger.error(f"Post Process Error: {str(e)}")
            return False

def main():
    processor = BOOTHPostProcessor()
    processor.post_content()

if __name__ == "__main__":
    main()
