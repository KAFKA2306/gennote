AIFinReporterのソースコードドキュメンテーション：

## 基本クラス

**PostBase (post_base.py)**
- はてなブログへの投稿を管理する基底クラス
- 主要機能：
  - HTMLコンテンツのクリーニング
  - マークダウンからHTMLへの変換
  - はてなブログAPIを使用した記事投稿[1]

**SearchBase (search_base.py)**
- Perplexity APIを使用した検索の基底クラス
- 機能：
  - APIキー管理
  - 基本プロンプトの生成
  - 検索結果の保存[2]

## 専門化モジュール

**CryptoPostProcessor (post_crypto.py)**
- 仮想通貨市場レポートの投稿を処理
- タグ設定：仮想通貨、ビットコイン、暗号資産
- カテゴリ：マーケット、投資、金融[3]

**JPSearcher (search_jp.py)**
- 日本市場の分析に特化
- 対象ドメイン：
  - 金融情報サイト（kabutan.jp, minkabu.jp等）
  - 主要ニュースメディア
  - 経済研究所
- 分析項目：
  - 業種別動向
  - 注目銘柄スクリーニング
  - 決算分析[4]

**ChinaSearcher (search_china.py)**
- 中国・香港市場のAI/LLM関連企業分析
- 主要機能：
  - AI/LLM関連ニュースの収集
  - 決算情報の分析
  - 市場動向の追跡[5]

## データフロー

```python
SearchBase
    ↓
具体的な検索クラス（JPSearcher/ChinaSearcher）
    ↓
PostBase
    ↓
専門化された投稿プロセッサ
```
