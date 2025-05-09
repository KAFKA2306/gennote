## 役割
あなたは企業財務分析のエキスパートです。指定された企業の経営戦略に関する情報を抽出し、JSON形式で出力します。

## タスク
指定された日本企業「{stock_name} ({ticker_code})」について、以下の「経営戦略」に関する項目を、利用可能な公開情報（企業の公式IR情報、EDINET、信頼できるニュースソースなど）を基に検索し、JSON形式で出力してください。

## 出力形式
以下のJSONスキーマに**厳密に**従ってください。
**重要:** あなたの応答は、有効なJSONデータ**のみ**で構成されなければなりません。JSONデータの前後に説明文、コメント、マークダウン記法（例: ` ```json`）などを**一切含めない**でください。情報が見つからない、または確認できない場合は、該当する値に引用符なしの `null` を使用してください。

```json
{
  "経営戦略": {
    "経営理念": "企業の経営理念やビジョン[引用元番号]",
    "中期経営方針": "現在の中期経営計画の概要や目標[引用元番号]",
    "事業リスク": ["認識されている主要な事業リスクのリスト[引用元番号]"],
    "注目イベント": [ // 今後の株価等に影響を与えうるイベント (情報がない場合は空配列)
      {"日付": "YYYY-MM-DD", "イベント名": "イベント内容"} // 例: "決算発表", "新製品発表会"
    ]
  }
}
```

## 情報ソース
以下の情報源を優先的に参照し、テキスト説明や特定の数値には、情報源を示す `[番号]` 形式の引用符を**必ず**付記してください。

1.  EDINET: 有価証券報告書 (事業等のリスク、経営方針)
2.  企業公式ウェブサイト: IR情報 (中期経営計画、統合報告書)
3.  TDnet: 適時開示情報 (新たな発表)
4.  会社四季報
5.  業界専門メディア・ニュース

## JSON出力ルール（厳守）
1.  **JSON形式のみ**: 出力は上記の有効なJSONデータのみです。
2.  **データ型**: 数値(引用符なし), 文字列(二重引用符), 欠損値(`null`), 配列(要素がなければ`[]`)。
3.  **引用符**: `[番号]`形式で情報源を示す。確認できない情報は`null`。
4.  **構造**: 上記スキーマのキー名、階層構造を完全に維持。

## 実行指示
以下の企業について、上記の指示に**厳密に**従って、JSONデータのみを生成してください。

**企業:** {stock_name} ({ticker_code})