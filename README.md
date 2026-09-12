# gennote

金融情報を検索・整形し、はてなブログ AtomPub へ送信する Python プロトタイプです。

公開先としてコード中に設定されているブログ: https://kafkafinancialgroup.hatenablog.com/

## 現在の実装

README が対象とする実装は `test/src/` です。

- `search_*.py`: Perplexity API を利用した検索処理
- `post.py` / `post_*.py`: はてなブログ AtomPub への送信処理
- `publication_state.py`: 記事入力の決定的 identity と公開完了 evidence の永続化
- `config.py`: API endpoint、検索domain、model等の設定
- `test/output/`: 過去に生成された出力

`batch/` には別のローカル実行経路も残っています。Windows上の固定pathを含むため、現在のportableな実行interfaceとは扱いません。

## 公開時の挙動

現在の `test/src/post.py` は `HATENA_ID` と `HATENA_API_KEY` を環境変数から読み、AtomPub collection URIへPOSTします。生成XMLは `<app:draft>no</app:draft>` を指定しているため、公開前reviewを強制する実装にはなっていません。

同じタイトルとMarkdown本文から SHA-256 の publication identity を生成し、既定では `test/output/.publication-state/` に状態を保存します。外部POSTの前に `uncertain` を記録し、`201` と有効な `Location` の両方を確認した場合だけ `confirmed` に昇格します。`confirmed` または `uncertain` の同一入力は再POSTしません。状態保存先は `GENNOTE_PUBLICATION_STATE_DIR` で変更できます。

はてなブログ公式AtomPub仕様: https://developer.hatena.ne.jp/ja/documents/blog/apis/atom/

## 現在確認できていないこと

- 検索結果の各主張が一次情報へ照合済みであること
- 生成文章と根拠URLを対応付ける保存形式
- draft → review → publish の承認手順
- fresh cloneからのportableな依存関係installと実行
- repositoryのcommitと公開記事を対応付けるdeployment evidence
- 定期実行scheduler

したがって、このrepositoryだけを根拠に「最新」「正確」「自動定期更新」を保証しません。

## 検証

GitHub ActionsではPython標準ライブラリだけを使い、tracked Python sourceの構文、`post.py` のmain entrypoint、publication identity、confirmed/uncertain 状態、再実行時の二重POST防止を検証します。
