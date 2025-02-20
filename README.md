# Project Description

It searches for the latest financial data, formats it, and posts it to a blog.
Result : https://kafkafinancialgroup.hatenablog.com/

## Directory Structure

```
.
└── test/
    ├── src/
    │   ├── post.py
    │   └── search.py
```

## src/* Explanation
- `search_latest.py`: Searches for the latest financial data.
- `search_china.py`: Searches for the lastest china financial data.
- `search_globalmacro.py`: Searches for the lastest globalmacro financial data.
- `post.py`: Posts to a blog.

---

検索機能付きLLMとブログを組み合わせて最新情報を取得して整理する

基本コンセプト検証OK

強いところ：中国語ドメインなどからも簡単に情報収集できる
https://kafkafinancialgroup.hatenablog.com/entry/2025/02/21/011723
弱いところ：情報の精査が不足している
将来性：model,prompt,domainのアップデートで価値が出るターゲット設定ができる

"model": "sonar-reasoning-pro"の制御が難しい
