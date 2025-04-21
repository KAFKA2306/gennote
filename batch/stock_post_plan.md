# 株式情報検索とHatenaブログ投稿スクリプト作成計画

**計画:**

1.  **`stock_search_and_post.py` の作成:**
    *   `search_china.py` をコピーして `stock_search_and_post.py` を作成します。このファイル名は、より説明的で、結合された機能が反映されています。
    *   プロンプトを `find_most_rising_stock_name_and_code.md` と `search_stock_information_then_fill_in json_format.md` を使用するように更新します。
    *   プロンプトで指定されたように、日本の株式と金融情報源に焦点を当てるように検索ロジックを変更します。
    *   **Hatena Blog への投稿機能をこのスクリプトに直接組み込みます。** これは、`post_crypto.py` (または `PostBase`) からの投稿ロジックを `stock_search_and_post.py` に組み込むことを意味します。
    *   スクリプトは最初に株式情報を検索し、次にそれをフォーマットし、最後にはてなブログに投稿します。
    *   タイトルは "本日の銘柄{銘柄名,ticker\_code} YYYY-MM-DD" の形式にする必要があります。
    *   タグには、銘柄名、"株式投資"、"個別株" を含める必要があります。

2.  **共通コードのリファクタリング:**
    *   `search_china.py`、`post_crypto.py`、および `stock_search_and_post.py` (API 呼び出し、ファイル保存、Hatena 投稿など) の間で共通の機能を特定します。
    *   コードの重複を避け、保守性を向上させるために、これらの共通部分を `SearchBase` および `PostBase` クラスにリファクタリングします。

**計画の Mermaid 図:**

\`\`\`mermaid
graph LR
    A[開始] --> B{stock_search_and_post.py を作成};
    B --> C{search_china.py を修正};
    C --> D{プロンプトを更新};
    D --> E{JP 株の検索ロジックを修正};
    E --> F{Hatena 投稿を組み込む};
    F --> G{タイトルとタグを更新};
    G --> H{Hatena に PostBase を使用};
    H --> I{共通コードをリファクタリング};
    I --> J[終了];
\`\`\`