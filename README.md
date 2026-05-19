# e-learning-AI

`e-learning-AI` は、対象サイト `e-learning` 上で実施する英語課題を、ブラウザの読み取りから操作まで自動化するための最小構成ツールです。  
Playwright を使い、JSON で定義した手順に従ってログイン・課題選択・回答入力・提出確認までを自動実行できます。

## セットアップ

```bash
python -m pip install -e .
python -m playwright install chromium
```

## 使い方

1. `config.example.json` をコピーして、自分の学校の `e-learning` サイトに合わせてセレクタやURLを調整します。
2. ログイン情報は環境変数で渡します。

```bash
export E_LEARNING_USERNAME="your-id"
export E_LEARNING_PASSWORD="your-password"
e-learning-ai config.json --output-dir outputs
```

画面を見ながら動作確認したい場合:

```bash
e-learning-ai config.json --headed --output-dir outputs
```

## 設定ファイル

設定ファイルは JSON 形式で、`actions` に順番に実行する操作を並べます。

### サポートしている action

- `goto`: URLを開く
- `wait_for`: 要素の表示待ち、または一定時間待機
- `click`: 要素をクリック
- `fill`: 入力欄に文字を入れる
- `press`: キー入力を送る
- `select_option`: セレクトボックスを選択する
- `check` / `uncheck`: チェックボックスを操作する
- `extract_text`: 要素の文字列を読み取って変数として保存する
- `assert_text`: 期待する文言が表示されていることを確認する
- `screenshot`: 実行結果のスクリーンショットを保存する

### ロケータ指定

`click` / `fill` / `extract_text` などの要素操作は、以下のいずれかで対象を指定できます。

- `selector`: CSS セレクタで指定
- `text`: 画面に表示される文字列で指定

同じ文言が複数ある場合は `nth` (0 始まり) で対象を選べます。  
`text` を厳密一致にしたい場合は `exact: true` を指定します。

```json
{
  "type": "click",
  "text": "学習する",
  "nth": 0
}
```

## 変数展開

`value` や `url` などの文字列では `${...}` 形式の変数展開を使えます。

- 先に `extract_text` で読み取った値
- 環境変数

例:

```json
{
  "type": "fill",
  "selector": "textarea.answer",
  "value": "Answer for ${assignment_title}"
}
```

## 目的

サイト構造が学校ごとに少し異なっても、コードを書き換えず設定ファイルだけで調整できるようにしてあります。  
そのため、まずは `config.example.json` をベースに、実際の `e-learning` 画面のセレクタへ置き換えて利用してください。
