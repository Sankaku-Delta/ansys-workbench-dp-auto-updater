# -*- coding: utf-8 -*-
"""
メール送信機能

SMTP によるメール送信
処理結果サマリーとログ全文を送信
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

from config import EMAIL_CONFIG


def send_email(subject, summary, full_log, logger=None):
    # type: (str, str, str, logging.Logger) -> bool
    """
    処理結果をメールで送信

    Args:
        subject (str): メール件名
        summary (str): 処理結果のサマリー
        full_log (str): ログ全文
        logger (logging.Logger): ロガーインスタンス（オプション）

    Returns:
        bool: 送信成功時 True、失敗時 False
    """
    if not EMAIL_CONFIG.get("enabled", False):
        if logger:
            logger.info("Email notification is disabled in config")
        return False

    try:
        # メール本文の作成
        body = _create_email_body(summary, full_log)

        # MIMEメッセージの作成
        msg = MIMEMultipart()
        msg["From"] = EMAIL_CONFIG["from_addr"]
        msg["To"] = EMAIL_CONFIG["to_addr"]
        msg["Subject"] = subject

        # 本文を添付
        msg.attach(MIMEText(body, "plain", "utf-8"))

        # SMTPサーバーに接続して送信
        smtp_server = EMAIL_CONFIG["smtp_server"]
        smtp_port = EMAIL_CONFIG["smtp_port"]
        use_tls = EMAIL_CONFIG.get("use_tls", True)

        if logger:
            logger.info("Connecting to SMTP server: {}:{}".format(smtp_server, smtp_port))

        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)

        # 認証
        username = EMAIL_CONFIG.get("username")
        password = EMAIL_CONFIG.get("password")
        if username and password:
            server.login(username, password)

        # メール送信
        server.send_message(msg)
        server.quit()

        if logger:
            logger.info("Email sent successfully to {}".format(EMAIL_CONFIG["to_addr"]))

        return True

    except Exception as e:
        error_msg = "Failed to send email: {}".format(str(e))
        if logger:
            logger.error(error_msg)
        else:
            print(error_msg)
        return False


def _create_email_body(summary, full_log):
    # type: (str, str) -> str
    """
    メール本文を作成

    Args:
        summary (str): 処理結果のサマリー
        full_log (str): ログ全文

    Returns:
        str: メール本文
    """
    body_parts = []

    # ヘッダー
    body_parts.append("=" * 60)
    body_parts.append("Ansys Workbench Batch Runner - 処理完了通知")
    body_parts.append("=" * 60)
    body_parts.append("")

    # サマリーセクション
    body_parts.append(summary)
    body_parts.append("")

    # ログセクション
    body_parts.append("-" * 60)
    body_parts.append("詳細ログ")
    body_parts.append("-" * 60)
    body_parts.append(full_log)

    return "\n".join(body_parts)


def format_summary(total_projects, successful_projects, failed_projects,
                   project_results, elapsed_time):
    # type: (int, int, int, list, timedelta) -> str
    """
    処理結果のサマリーを整形

    Args:
        total_projects (int): 総プロジェクト数
        successful_projects (int): 成功したプロジェクト数
        failed_projects (int): 失敗したプロジェクト数
        project_results (list): プロジェクトごとの結果リスト
        elapsed_time (timedelta): 処理時間

    Returns:
        str: 整形されたサマリー
    """
    lines = []

    # 全体サマリー
    lines.append("処理結果サマリー")
    lines.append("")
    lines.append("総プロジェクト数: {}".format(total_projects))
    lines.append("成功: {}".format(successful_projects))
    lines.append("失敗: {}".format(failed_projects))
    lines.append("処理時間: {}".format(_format_timedelta(elapsed_time)))
    lines.append("")

    # 各プロジェクトの結果
    lines.append("各プロジェクトの結果:")
    lines.append("")
    for result in project_results:
        status_icon = "[OK]" if result["success"] else "[FAILED]"
        lines.append("{} {}".format(status_icon, result["project"]))
        if not result["success"] and result.get("error"):
            lines.append("  エラー: {}".format(result["error"]))
        if result.get("dp_success") is not None:
            lines.append("  設計ポイント成功: {} / {}".format(
                result["dp_success"], result["dp_total"]
            ))
        lines.append("")

    return "\n".join(lines)


def _format_timedelta(td):
    # type: (timedelta) -> str
    """
    timedelta を読みやすい形式に整形

    Args:
        td (timedelta): 時間差

    Returns:
        str: 整形された文字列 (例: "1時間23分45秒")
    """
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if hours > 0:
        parts.append("{}時間".format(hours))
    if minutes > 0:
        parts.append("{}分".format(minutes))
    parts.append("{}秒".format(seconds))

    return "".join(parts)


def create_subject(successful, total):
    # type: (int, int) -> str
    """
    メール件名を作成

    Args:
        successful (int): 成功したプロジェクト数
        total (int): 総プロジェクト数

    Returns:
        str: メール件名
    """
    if successful == total:
        status = "SUCCESS"
    else:
        status = "FAILED"

    return "[Ansys Batch] {} - {}/{} projects completed".format(
        status, successful, total
    )
