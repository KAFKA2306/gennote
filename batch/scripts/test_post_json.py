import os
import json
import re
from datetime import datetime, timezone, timedelta
from post_base import PostBase  # はてなブログ投稿用の基底クラス

def post_json_to_hatena(json_filepath):
    """
    JSONファイルの内容をはてなブログに投稿する関数
    
    Args:
        json_filepath (str): 投稿するJSONファイルのパス
        
    Returns:
        tuple: (成功したかどうか, 投稿URL)
    """
    try:
        # 1. ファイル名から会社情報を抽出
        company_info = extract_company_info(json_filepath)
        
        # 2. JSONファイルの内容を読み込み
        json_content = read_json_file(json_filepath)
        
        # 3. ブログ投稿用のコンテンツを作成
        blog_content = create_blog_content(json_content)
        
        # 4. ブログ投稿用のメタデータを設定
        blog_title, post_tags = create_blog_metadata(company_info)
        
        # 5. はてなブログに投稿
        success, url = post_to_hatena_blog(blog_title, blog_content, post_tags)
        
        return success, url
        
    except Exception as e:
        print(f"エラー発生: {e}")
        return False, None


def extract_company_info(json_filepath):
    """
    ファイル名から会社名と証券コードを抽出する関数
    
    Args:
        json_filepath (str): JSONファイルのパス
        
    Returns:
        dict: 会社情報を含む辞書
    """
    filename = os.path.basename(json_filepath)
    match = re.search(r'(\d{8})_(.+?)_(\d{4})\.json', filename)
    
    if match:
        date_str, company_name, ticker_code = match.groups()
        # 会社名のアンダースコアをスペースに置換
        company_name = company_name.replace('_', ' ')
    else:
        # ファイル名からの抽出に失敗した場合はJSONから情報を取得
        with open(json_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        company_data = data["企業データ"][0]
        company_name = company_data["基本情報"]["法人名"]
        ticker_code = company_data["基本情報"]["証券コード"]
    
    return {
        "company_name": company_name,
        "ticker_code": ticker_code,
        "date_str": date_str if 'date_str' in locals() else datetime.now().strftime("%Y%m%d")
    }


def read_json_file(json_filepath):
    """
    JSONファイルの内容を読み込む関数
    
    Args:
        json_filepath (str): JSONファイルのパス
        
    Returns:
        str: JSONファイルの内容
    """
    with open(json_filepath, 'r', encoding='utf-8') as f:
        return f.read()


def create_blog_content(json_content):
    """
    ブログ投稿用のコンテンツを作成する関数
    
    Args:
        json_content (str): JSONファイルの内容
        
    Returns:
        str: ブログ投稿用のコンテンツ
    """
    return f"""
```
{json_content}
```
"""


def create_blog_metadata(company_info):
    """
    ブログ投稿用のメタデータを作成する関数
    
    Args:
        company_info (dict): 会社情報を含む辞書
        
    Returns:
        tuple: (ブログタイトル, 投稿タグのリスト)
    """
    # ブログ共通タグ
    BLOG_TAGS_COMMON = ["株式投資", "個別株", "銘柄分析", "日本株", "JSONデータ"]
    
    # 日本時間の現在日時を取得
    JST = timezone(timedelta(hours=+9), 'JST')
    now_jst = datetime.now(JST)
    current_date_title = now_jst.strftime("%Y-%m-%d")
    
    # ブログタイトルを設定
    blog_title = f"【注目銘柄】{company_info['company_name']}({company_info['ticker_code']}) - {current_date_title}"
    
    # タグを設定（会社名とコードを追加）
    post_tags = list(set([company_info['company_name'], company_info['ticker_code']] + BLOG_TAGS_COMMON))
    
    return blog_title, post_tags


def post_to_hatena_blog(blog_title, blog_content, post_tags):
    """
    はてなブログに投稿する関数
    
    Args:
        blog_title (str): ブログタイトル
        blog_content (str): ブログコンテンツ
        post_tags (list): 投稿タグのリスト
        
    Returns:
        tuple: (成功したかどうか, 投稿URL)
    """
    # ブログカテゴリ
    BLOG_CATEGORIES = ["マーケット", "投資", "金融"]
    
    # はてなブログに投稿
    poster = PostBase()
    entry_xml = poster.create_entry_xml(
        title=blog_title,
        content=blog_content,
        tags=post_tags,
        categories=BLOG_CATEGORIES
    )
    
    success, url = poster.post_to_hatena(entry_xml)
    if success:
        print(f"投稿成功: {url}")
    else:
        print("投稿失敗")
    
    return success, url


if __name__ == "__main__":
    # JSONファイルのパス
    json_filepath = r"M:\ML\ChatGPT\gennote\test\output\20250421_株式会社ネクスウェア_4814.json"
    post_json_to_hatena(json_filepath)