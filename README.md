# saleslist

Instagram・Xの指定アカウントのフォロワーを、営業確認用CSVへ出力するPython CLIです。DMの送信は一切行いません。

取得できる範囲でDM不可と明示されたアカウントは除外します。公開プロフィールの情報だけでは判定できないケースは `dm_status=unknown` として残します。

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

`.env` に認証情報を設定してください。`.env`、`sessions/`、`output/` はGit管理されません。

## 認証設定

### Instagram

通常は以下を設定します。

```env
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

Instagramのパスワードログインで本人確認が解除できない場合は、通常のChromeでInstagramへログインした状態で `sessionid` Cookieを確認し、`INSTAGRAM_SESSION_ID` として `.env` に設定できます。この値はパスワード相当の機密情報なので共有・Git管理しないでください。設定時はInstagramのユーザー名・パスワードより優先されます。

### X

Xは`tweetkit-x`を使用します。Xにログイン済みのブラウザから、`auth_token`と`ct0`を含むCookieヘッダーを取得して設定してください。

```env
TWEETKIT_COOKIE="auth_token=...; ct0=...;"
```

Cookieはパスワードと同等の機密情報です。チャット・Git・CSVへ貼り付けないでください。Cookieが失効した場合は、ブラウザで再ログインして新しい値に置き換えます。

## 使い方

```bash
python -m saleslist instagram target_account
python -m saleslist x target_account --limit 500
python -m saleslist instagram target_account --resume
python -m saleslist x target_account --resume output/x_target_account_20260101T000000+0900.csv
```

省略時は全件を取得します。件数を制限する場合は `--limit` を使います。

```bash
python -m saleslist x ebisol_official --limit 100
```

途中で停止した場合は、すでに出力済みのCSVを指定して再開できます。再開時はCSV内のユーザー名を読み込み、重複行を出力しません。

```bash
python -m saleslist x ebisol_official --resume output/x_ebisol_official_YYYYMMDDTHHMMSS+0900.csv
```

## 出力

CSVは毎回、新規ファイルとして次の形式で作成されます。

```text
output/<platform>_<target>_<timestamp>.csv
```

列は、プラットフォーム、ユーザー名、表示名、プロフィールURL、自己紹介、フォロワー数、フォロー数、公開／非公開状態、DM判定、取得日時です。取得できない項目は空欄になります。

## 注意事項

各サービスの利用規約、取得対象への権限、および個人情報保護上の義務を確認して使用してください。レート制限・認証チェックが発生した場合は停止し、時間を置いて `--resume` で再開してください。

Xは非公開の内部APIに依存するため、Xの変更により取得不能になる可能性があります。その場合はログインを繰り返さず、表示されたエラーを確認してください。
