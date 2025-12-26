# Ansys Workbench Batch Runner

Ansys Workbench の複数プロジェクト（.wbpj）の設計ポイント（Design Points）を連続実行し、完了時にメール通知を行うバッチ処理スクリプト。

## 特徴

- **複数プロジェクトの自動処理**: 複数の .wbpj ファイルを順次処理
- **堅牢なエラーハンドリング**: 1つのプロジェクトが失敗しても全体の処理を継続
- **詳細なログ出力**: コンソール、ファイル、メール本文の3箇所に出力
- **メール通知**: 処理完了時に結果サマリーとログをメールで送信
- **自動バックアップ**: 保存失敗時は自動的にバックアップファイルを作成

## 必要要件

- ANSYS Workbench（v241 など）
- Python 2.7（Workbench の IronPython 環境で実行）
- メール通知を使用する場合: SMTPサーバーへのアクセス

## インストール

1. このリポジトリをクローンまたはダウンロード:

```bash
git clone https://github.com/yourusername/ansys-workbench-dp-auto-updater.git
```

1. スクリプトを任意のディレクトリに配置（例: `C:\Scripts\`）:

```
C:\Scripts\
├── config.py
├── logger.py
├── email_utils.py
└── run_projects.py
```

## 設定

### 1. プロジェクトリストの設定

`config.py` を編集して、処理したいプロジェクトファイルを指定:

```python
PROJECTS = [
    r"C:\Work\Project1.wbpj",
    r"C:\Work\Project2.wbpj",
    # 必要に応じて追加
]
```

### 2. ログ設定

ログファイルの保存先とログレベルを設定:

```python
LOG_CONFIG = {
    "level": "INFO",              # DEBUG, INFO, WARNING, ERROR, CRITICAL
    "log_to_file": True,
    "log_dir": r"C:\Scripts\logs",
    "log_file_prefix": "ansys_batch",
}
```

### 3. メール設定

SMTP サーバーの情報と認証情報を設定:

```python
EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_email@gmail.com",
    "password": "your_app_password",  # Gmail の場合はアプリパスワードを使用
    "from_addr": "your_email@gmail.com",
    "to_addr": "recipient@example.com",
}
```

**Gmail を使用する場合の注意:**

- 2段階認証を有効にする
- アプリパスワードを生成して使用する（[詳細](https://support.google.com/accounts/answer/185833)）

## 実行方法

コマンドプロンプトまたはバッチファイルから以下のコマンドを実行:

```bat
"C:\Program Files\ANSYS Inc\v241\Framework\bin\Win64\RunWB2.exe" -B -R "C:\Scripts\run_projects.py"
```

### オプション

- `-B`: バッチモード（GUIなし）
- `-R`: スクリプトファイルを実行

**注意:** `v241` の部分は、インストールされている Ansys のバージョンに合わせて変更してください。

## 出力例

### コンソール出力

```
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - ************************************************************
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - Ansys Workbench Batch Runner - START
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - ************************************************************
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - Start time: 2025-12-26 10:00:00
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - Total projects to process: 2
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - ============================================================
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - Processing project: C:\Work\Project1.wbpj
2025-12-26 10:00:00 - AnsysBatchRunner - INFO - ============================================================
...
```

### メール通知

**件名:**

```
[Ansys Batch] SUCCESS - 2/2 projects completed
```

**本文:**

```
============================================================
Ansys Workbench Batch Runner - 処理完了通知
============================================================

処理結果サマリー

総プロジェクト数: 2
成功: 2
失敗: 0
処理時間: 1時間23分45秒

各プロジェクトの結果:

[OK] Project1.wbpj
  設計ポイント成功: 5 / 5

[OK] Project2.wbpj
  設計ポイント成功: 3 / 3

------------------------------------------------------------
詳細ログ
------------------------------------------------------------
[ログ全文が続く...]
```

## ファイル構成

| ファイル | 役割 |
|----------|------|
| `config.py` | プロジェクトリスト、ログ設定、メール設定を一元管理 |
| `logger.py` | Python logging ライブラリを使用。コンソール、ファイル、メール用バッファの3出力先に対応 |
| `email_utils.py` | SMTP によるメール送信。処理結果サマリーとログ全文を送信 |
| `run_projects.py` | メインスクリプト。Workbench API を呼び出して設計ポイントを更新 |

## トラブルシューティング

### プロジェクトが開けない

- ファイルパスが正しいか確認
- ファイルが別のプロセスで開かれていないか確認
- Ansys のバージョンとプロジェクトの互換性を確認

### メールが送信されない

- SMTP サーバーの設定を確認
- ファイアウォールやセキュリティソフトが SMTP 通信をブロックしていないか確認
- Gmail の場合、アプリパスワードを使用しているか確認

### ログファイルが作成されない

- ログディレクトリが存在するか確認
- ディレクトリへの書き込み権限があるか確認

## 今後の拡張候補

- 設計ポイントの並列実行設定
- Slack / Teams 通知対応
- 実行スケジュール機能（タスクスケジューラ連携）
- 結果の CSV / Excel 出力
- Web UI によるジョブ管理

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 注意事項

- このスクリプトは Workbench の IronPython 2.7 環境で実行されます
- Ansys のバージョンによって API が若干異なる場合があります
- 大規模なプロジェクトや多数の設計ポイントを処理する場合、実行時間が長くなる可能性があります
