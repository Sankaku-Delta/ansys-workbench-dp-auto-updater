# -*- coding: utf-8 -*-
"""
設定ファイル

プロジェクトリスト、ログ設定、メール設定を一元管理
"""

# プロジェクトリスト
# 処理したい .wbpj ファイルのフルパスを指定
PROJECTS = [
    r"C:\Work\Project1.wbpj",
    r"C:\Work\Project2.wbpj",
    # 必要に応じて追加
]

# ログ設定
LOG_CONFIG = {
    # ログレベル: DEBUG, INFO, WARNING, ERROR, CRITICAL
    "level": "INFO",

    # ファイルにログを出力するか
    "log_to_file": True,

    # ログファイルの保存先ディレクトリ
    "log_dir": r"C:\Scripts\logs",

    # ログファイル名のプレフィックス
    # 実際のファイル名は: {prefix}_YYYYMMDD_HHMMSS.log
    "log_file_prefix": "ansys_batch",
}

# メール設定
EMAIL_CONFIG = {
    # メール通知を有効にするか
    "enabled": True,

    # SMTPサーバー設定
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": True,

    # 認証情報
    # Gmail の場合はアプリパスワードを使用すること
    # https://support.google.com/accounts/answer/185833
    "username": "your_email@gmail.com",
    "password": "your_app_password",

    # 送信元・送信先アドレス
    "from_addr": "your_email@gmail.com",
    "to_addr": "recipient@example.com",
}
