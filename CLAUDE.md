# Ansys Workbench Batch Runner

## 概要

Ansys Workbench の複数プロジェクト（.wbpj）の設計ポイント（Design Points）を連続実行し，完了時にメール通知を行うバッチ処理スクリプト．

修士論文でデータを集めるために使用．

## ファイル構成

```
C:\Scripts\
├── CLAUDE.md          # このファイル
├── config.py          # 設定ファイル
├── logger.py          # ロガー設定
├── email_utils.py     # メール送信機能
└── run_projects.py    # メインスクリプト
```

### 各ファイルの役割

| ファイル | 役割 |
|----------|------|
| config.py | プロジェクトリスト，ログ設定，メール設定を一元管理 |
| logger.py | Python logging ライブラリを使用．コンソール，ファイル，メール用バッファの3出力先に対応 |
| email_utils.py | SMTP によるメール送信．処理結果サマリーとログ全文を送信 |
| run_projects.py | メインスクリプト．Workbench API を呼び出して設計ポイントを更新 |

## 実行方法

```bat
"C:\Program Files\ANSYS Inc\v241\Framework\bin\Win64\RunWB2.exe" -B -R "C:\Scripts\run_projects.py"
```

- `-B`: バッチモード（GUIなし）
- `-R`: スクリプト実行
- `v241` 部分はインストールされている Ansys バージョンに合わせて変更

## 設計方針

### 堅牢性

- 例外処理を徹底し，1つのプロジェクトや設計ポイントが失敗しても全体が止まらない
- ファイル存在チェック，保存失敗時のバックアップ保存を実装
- 各処理段階で try-except を使用

### ログ出力

- Python 標準の logging ライブラリを使用
- 3つの出力先: コンソール，ファイル，メール本文用バッファ
- タイムスタンプ付きログファイル（実行ごとに別ファイル）
- ログレベル対応（DEBUG, INFO, WARNING, ERROR, CRITICAL）

### メール通知

- 処理完了時に結果サマリーをメール送信
- 件名で成功/失敗が一目でわかる
- 本文に経過時間，各プロジェクトの結果，ログ全文を含む
- Gmail，社内SMTPサーバー両対応

## Workbench API

### 使用している主な API

```python
Open(FilePath=path)                    # プロジェクトを開く
Save()                                 # プロジェクトを保存
Save(FilePath=path)                    # 別名で保存
Parameters.GetAllDesignPoints()        # 全設計ポイントを取得
designPoint.Update()                   # 設計ポイントを更新
designPoint.Retained                   # 更新済みかどうか
```

### 注意事項

- スクリプトは Workbench の IronPython 環境で実行される
- `Open`, `Save`, `Parameters` などはグローバルに利用可能な Workbench API
- Ansys バージョンによって API が若干異なる場合がある

## 設定項目

### config.py

```python
# プロジェクトリスト
PROJECTS = [
    r"C:\Work\Project1.wbpj",
    r"C:\Work\Project2.wbpj",
]

# ログ設定
LOG_CONFIG = {
    "level": "INFO",
    "log_to_file": True,
    "log_dir": r"C:\Scripts\logs",
    "log_file_prefix": "ansys_batch",
}

# メール設定
EMAIL_CONFIG = {
    "enabled": True,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,
    "username": "your_email@gmail.com",
    "password": "your_app_password",
    "from_addr": "your_email@gmail.com",
    "to_addr": "recipient@example.com",
}
```

## 今後の拡張候補

- 設計ポイントの並列実行設定
- Slack / Teams 通知対応
- 実行スケジュール機能（タスクスケジューラ連携）
- 結果の CSV / Excel 出力
- Web UI によるジョブ管理
