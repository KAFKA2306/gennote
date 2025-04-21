M:\ML\ChatGPT\gennote\batch\scripts\search_china.py
M:\ML\ChatGPT\gennote\batch\scripts\post_crypto.py

上記のファイルのように、検索してはてなブログにポストするプログラムを作成したいです。

まず最初に、
M:\ML\ChatGPT\gennote\batch\scripts\prompt\find_most_rising_stock_name_and_code.md
で軽く検索して、対象の銘柄を決めます。
次に、以下の内容で良く検索して、最終的な出力を得ます。
M:\ML\ChatGPT\gennote\batch\scripts\prompt\search_stock_information_then_fill_in json_format.md


これをはてなブログに、本日の銘柄{銘柄名,ticker_code} YYYY-MM-DDのようなタイトルで形式でポストする
タグには、個別株の名前や、株式投資や個別株といったものをつけること。


それでは、2つのpyファイルを作成してスタート