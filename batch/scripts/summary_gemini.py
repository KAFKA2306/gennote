# summary_gemini.py

import os
import glob
from datetime import datetime
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from post_base import PostBase
import heapq

class GeminiSummarizer:
    def __init__(self, max_files=10):
        # 環境変数の読み込み
        load_dotenv('M:/ML/ChatGPT/gennote/.env')
        
        # Gemini API キーの設定
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=self.gemini_api_key)
        
        # 入出力パスの設定
        self.input_folder = 'M:/ML/ChatGPT/gennote/test/output/'
        self.output_folder = 'M:/ML/ChatGPT/gennote/test/gemini_output/'
        
        # 最大ファイル数の設定
        self.max_files = max_files
        
        # 出力フォルダが存在しない場合は作成
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        
        # ロギングの設定
        self._setup_logging()
        
        # Geminiモデルの設定
        self.model = genai.GenerativeModel('gemini-1.5-pro')

    def _setup_logging(self):
        """ロギングの設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def read_markdown_files(self):
        """最新のマークダウンファイルを読み込む"""
        try:
            # 入力フォルダが存在するか確認
            if not os.path.exists(self.input_folder):
                self.logger.error(f"入力フォルダが存在しません: {self.input_folder}")
                return None
            
            # マークダウンファイルのパスを取得
            markdown_files = glob.glob(os.path.join(self.input_folder, '*.md'))
            
            if not markdown_files:
                self.logger.warning("マークダウンファイルが見つかりませんでした")
                return None
            
            # ファイルの最終更新日時を取得し、最新のファイルを選択
            latest_files = heapq.nlargest(self.max_files, markdown_files, key=os.path.getmtime)
            
            # ファイルの内容を読み込む
            markdown_contents = {}
            for file_path in latest_files:
                file_name = os.path.basename(file_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        markdown_contents[file_name] = content
                        self.logger.info(f"ファイルを読み込みました: {file_name}")
                except Exception as e:
                    self.logger.error(f"ファイル読み込みエラー ({file_name}): {str(e)}")
            
            return markdown_contents
        
        except Exception as e:
            self.logger.error(f"マークダウンファイル読み込みエラー: {str(e)}")
            return None

    def create_summary_prompt(self, contents, file_list):
        """要約用のプロンプトを作成"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        # 読み込んだファイル一覧を作成
        files_info = "\n".join([f"- {file_name}" for file_name in file_list])
        
        prompt = f"""
# 本日({current_date})のアナリストレポート総括

以下の複数の市場・業界レポートから、総合的なアナリストレポートとしてまとめてください。

【分析対象ファイル一覧】
{files_info}

【レポート内容】
{contents}

【出力形式】
## 市場概況
- 世界経済の全体的な状況（成長率予測、インフレ動向、金融政策など）
- 主要地域・国別の市場動向（米国、欧州、日本、中国など）
- 資産クラス別の市場状況（株式、債券、為替、商品市場など）
- 重要な経済指標

## 業界別分析
- 各業界の重要トレンドと構造変化
- 業績動向
- 注目すべきセクターと具体的な銘柄例（コードと企業名）
- 業界固有のリスク要因と機会


## 今後の注目ポイント
- 今週・来週の重要経済イベントとその潜在的影響
- 監視すべき経済指標や企業動向
- 政策変更の可能性とその影響
- 長期的な構造変化と投資への示唆

【重要指示】
- 必ず上記の【分析対象ファイル一覧】に記載されたすべてのファイルの内容に言及してください
- 各セクションでは、情報の出所となるファイル名を明示しないでください。
- 具体的な数値、銘柄名、企業名、経済指標などを含め、具体性のある分析を提供してください
- 銘柄に言及する場合は、企業名とともに証券コードも記載してください
- 引用符や引用表記は使用せず、情報を自然な文章に統合してください
- 株式や企業に言及する際は、公式サイトやYahoo Financeなどへのリンクを付けてください
- 具体的かつ実用的な情報を日本語で提供してください
- 各セクションで最も重要な情報に焦点を当て、明瞭かつ詳細に記述してください


複数の市場・業界レポートから、総合的なアナリストレポートとしてまとめてください。
"""
        return prompt

    def generate_summary(self, markdown_contents):
        """Gemini AIを使用して要約を生成"""
        try:
            if not markdown_contents:
                self.logger.error("要約するコンテンツがありません")
                return None
            
            # ファイル名のリスト
            file_list = list(markdown_contents.keys())
            
            # すべてのコンテンツを結合
            combined_content = "\n\n===== 次のレポート =====\n\n".join(
                [f"【{file_name}】\n{content}" for file_name, content in markdown_contents.items()]
            )
            
            # プロンプトの作成
            prompt = self.create_summary_prompt(combined_content, file_list)
            
            # Gemini AIによる要約生成
            response = self.model.generate_content(prompt)
            
            if response:
                summary = response.text
                self.logger.info("要約の生成に成功しました")
                return summary
            else:
                self.logger.error("Gemini AIからの応答がありませんでした")
                return None
        
        except Exception as e:
            self.logger.error(f"要約生成エラー: {str(e)}")
            return None

    def save_summary(self, summary):
        """生成された要約を保存"""
        try:
            if not summary:
                self.logger.error("保存する要約がありません")
                return None
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            output_file = os.path.join(self.output_folder, f"{current_date}_gemini_summary.md")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            self.logger.info(f"要約を保存しました: {output_file}")
            return output_file
        
        except Exception as e:
            self.logger.error(f"要約保存エラー: {str(e)}")
            return None

    def execute(self):
        """要約処理の実行"""
        # マークダウンファイルの読み込み
        markdown_contents = self.read_markdown_files()
        
        if not markdown_contents:
            self.logger.error("処理を中止します: マークダウンファイルが読み込めませんでした")
            return False
        
        # 要約の生成
        summary = self.generate_summary(markdown_contents)
        
        if not summary:
            self.logger.error("処理を中止します: 要約の生成に失敗しました")
            return False
        
        # 要約の保存
        output_file = self.save_summary(summary)
        
        if not output_file:
            self.logger.error("処理を中止します: 要約の保存に失敗しました")
            return False
        
        # はてなブログへの投稿
        poster = GeminiSummaryPoster()
        success = poster.post_content(output_file)
        
        return success


class GeminiSummaryPoster(PostBase):
    def __init__(self):
        super().__init__()
        self.tags = ["マーケット分析", "投資戦略", "アナリストレポート", "市場動向"]
        self.categories = ["マーケット", "投資", "分析"]
        self._setup_logging()

    def _setup_logging(self):
        """ロギングの設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def post_content(self, file_path):
        """要約をはてなブログに投稿"""
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"ファイルが存在しません: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_date = datetime.now().strftime("%Y-%m-%d")
            title = f"AIアナリストレポート総括 {current_date}"
            
            # ファイル情報を追加
            header = f"# AIアナリストレポート総括 {current_date}\n\n"
            header += "本レポートは、最新の市場・業界レポートを分析し、重要なポイントを抽出して総合的にまとめたものです。\n\n"
            
            # 整形されたコンテンツ
            formatted_content = header + content
            
            entry_xml = self.create_entry_xml(
                title=title,
                content=formatted_content,
                tags=self.tags,
                categories=self.categories
            )
            
            success, url = self.post_to_hatena(entry_xml)
            
            if success:
                self.logger.info(f"投稿URL: {url}")
                return True
            else:
                self.logger.error("はてなブログへの投稿に失敗しました")
                return False
        
        except Exception as e:
            self.logger.error(f"投稿処理エラー: {str(e)}")
            return False


def main():
    # 最新の10ファイルを処理
    summarizer = GeminiSummarizer(max_files=10)
    result = summarizer.execute()
    print(f"処理結果: {'成功' if result else '失敗'}")


if __name__ == "__main__":
    main()
