# -*- coding: utf-8 -*-
"""
ロガー設定

Python logging ライブラリを使用
コンソール、ファイル、メール用バッファの3出力先に対応
"""

import sys
import os
from datetime import datetime

try:
    # IronPython環境では一部のモジュールが制限される可能性があるため try-except で対応
    import logging
    from logging.handlers import MemoryHandler
except ImportError as e:
    print("Error importing logging modules: {}".format(str(e)))
    raise

from config import LOG_CONFIG


class EmailLogHandler(logging.Handler):
    """
    メール送信用のログバッファ

    ログメッセージを内部バッファに蓄積し、
    後でメール本文として取得できるようにする
    """
    def __init__(self):
        # type: () -> None
        super(EmailLogHandler, self).__init__()
        self.log_buffer = []  # type: list

    def emit(self, record):
        # type: (logging.LogRecord) -> None
        """ログレコードをバッファに追加"""
        try:
            msg = self.format(record)
            self.log_buffer.append(msg)
        except Exception:
            self.handleError(record)

    def get_logs(self):
        # type: () -> str
        """蓄積されたログを取得"""
        return "\n".join(self.log_buffer)

    def clear(self):
        # type: () -> None
        """バッファをクリア"""
        self.log_buffer = []


def setup_logger():
    # type: () -> tuple
    """
    ロガーのセットアップ

    Returns:
        tuple: (logger, email_handler)
            logger (logging.Logger): 設定済みのロガーインスタンス
            email_handler (EmailLogHandler): メール用ログハンドラ（ログ取得用）
    """
    # ロガーの作成
    logger = logging.getLogger("AnsysBatchRunner")

    # ログレベルの設定
    level_name = LOG_CONFIG.get("level", "INFO")
    level = getattr(logging, level_name, logging.INFO)
    logger.setLevel(level)

    # 既存のハンドラをクリア（重複防止）
    logger.handlers = []

    # フォーマッタの作成
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. コンソールハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. ファイルハンドラ
    if LOG_CONFIG.get("log_to_file", False):
        try:
            log_dir = LOG_CONFIG.get("log_dir", ".")
            # ログディレクトリが存在しない場合は作成
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # タイムスタンプ付きログファイル名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = LOG_CONFIG.get("log_file_prefix", "ansys_batch")
            log_filename = "{}_{}.log".format(prefix, timestamp)
            log_filepath = os.path.join(log_dir, log_filename)

            file_handler = logging.FileHandler(log_filepath, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            logger.info("Log file created: {}".format(log_filepath))
        except Exception as e:
            logger.warning("Failed to create file handler: {}".format(str(e)))

    # 3. メール用バッファハンドラ
    email_handler = EmailLogHandler()
    email_handler.setLevel(logging.INFO)  # メールには INFO 以上を含める
    email_handler.setFormatter(formatter)
    logger.addHandler(email_handler)

    return logger, email_handler
