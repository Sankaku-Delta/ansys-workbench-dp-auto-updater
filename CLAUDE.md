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

- **3段階のメール通知**:
  1. **プロジェクト開始通知**: 各プロジェクトの処理開始時に送信
  2. **プロジェクト完了通知**: 各プロジェクトの処理完了時に送信
  3. **全体完了通知**: 全プロジェクトの処理完了時に送信
- 件名で状態（STARTING/SUCCESS/FAILED）が一目でわかる
- 本文に経過時間，進捗状況，各プロジェクトの結果，ログ全文を含む
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

## メール通知の詳細

### 送信されるメールの種類

#### 1. プロジェクト開始通知

各プロジェクトの処理開始時に送信されます。

**件名例:**
```
[Ansys Batch] STARTING - 2/5 - Project2.wbpj
```

**本文内容:**
- プロジェクト名
- 開始時刻
- 全体の進捗（処理済み/成功/失敗/残り）
- 詳細ログ

#### 2. プロジェクト完了通知

各プロジェクトの処理完了時に送信されます。

**件名例:**
```
[Ansys Batch] SUCCESS - 2/5 - Project2.wbpj
[Ansys Batch] FAILED - 3/5 - Project3.wbpj
```

**本文内容:**
- プロジェクト名
- 処理結果（成功/失敗）
- 処理時間
- 設計ポイントの結果（総数/成功/失敗）
- エラー情報（失敗時）
- 全体の進捗
- 詳細ログ

#### 3. 全体完了通知

全プロジェクトの処理完了後に送信されます。

**件名例:**
```
[Ansys Batch] SUCCESS - 5/5 projects completed
[Ansys Batch] FAILED - 3/5 projects completed
```

**本文内容:**
- 総プロジェクト数
- 成功/失敗数
- 総処理時間
- 各プロジェクトの結果一覧
- 詳細ログ

### メール送信のタイミング

5つのプロジェクトを処理する場合、最大11通のメールが送信されます：

1. プロジェクト1 開始通知
2. プロジェクト1 完了通知
3. プロジェクト2 開始通知
4. プロジェクト2 完了通知
5. プロジェクト3 開始通知
6. プロジェクト3 完了通知
7. プロジェクト4 開始通知
8. プロジェクト4 完了通知
9. プロジェクト5 開始通知
10. プロジェクト5 完了通知
11. 全体完了通知

これにより、処理の進捗をリアルタイムで把握できます。

## 今後の拡張候補

- 設計ポイントの並列実行設定
- Slack / Teams 通知対応
- 実行スケジュール機能（タスクスケジューラ連携）
- 結果の CSV / Excel 出力
- Web UI によるジョブ管理
- メール通知の頻度設定（開始/完了の通知を個別に有効/無効化）
