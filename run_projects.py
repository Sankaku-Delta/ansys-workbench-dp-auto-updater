# -*- coding: utf-8 -*-
r"""
メインスクリプト

Workbench API を呼び出して設計ポイントを更新
複数プロジェクトの設計ポイントを連続実行し、完了時にメール通知を行う

使用方法:
    "C:\Program Files\ANSYS Inc\v241\Framework\bin\Win64\RunWB2.exe" -B -R "C:\Scripts\run_projects.py"
"""

import sys
import os
import logging
from datetime import datetime, timedelta

# カスタムモジュールのインポート
try:
    from config import PROJECTS
    from logger import setup_logger
    from email_utils import send_email, format_summary, create_subject, send_project_start_email
except ImportError as e:
    print("Error importing modules: {}".format(str(e)))
    print("Make sure config.py, logger.py, and email_utils.py are in the same directory")
    sys.exit(1)


def process_project(project_path, logger):
    # type: (str, logging.Logger) -> dict
    """
    1つのプロジェクトを処理

    Args:
        project_path (str): プロジェクトファイル (.wbpj) のパス
        logger (logging.Logger): ロガーインスタンス

    Returns:
        dict: 処理結果
            {
                "project": str,
                "success": bool,
                "error": str or None,
                "dp_total": int,
                "dp_success": int,
            }
    """
    result = {
        "project": os.path.basename(project_path),
        "success": False,
        "error": None,
        "dp_total": 0,
        "dp_success": 0,
    }

    try:
        logger.info("=" * 60)
        logger.info("Processing project: {}".format(project_path))
        logger.info("=" * 60)

        # ファイル存在チェック
        if not os.path.exists(project_path):
            error_msg = "Project file not found: {}".format(project_path)
            logger.error(error_msg)
            result["error"] = error_msg
            return result

        # プロジェクトを開く
        logger.info("Opening project...")
        try:
            Open(FilePath=project_path)
            logger.info("Project opened successfully")
        except Exception as e:
            error_msg = "Failed to open project: {}".format(str(e))
            logger.error(error_msg)
            result["error"] = error_msg
            return result

        # 設計ポイントを取得
        logger.info("Retrieving design points...")
        try:
            design_points = Parameters.GetAllDesignPoints()
            dp_count = len(design_points)
            result["dp_total"] = dp_count
            logger.info("Found {} design point(s)".format(dp_count))
        except Exception as e:
            error_msg = "Failed to get design points: {}".format(str(e))
            logger.error(error_msg)
            result["error"] = error_msg
            # プロジェクトを閉じる前に保存を試みる
            _safe_save(project_path, logger)
            return result

        # 各設計ポイントを更新
        dp_success_count = 0
        for i, dp in enumerate(design_points, 1):
            try:
                logger.info("Processing design point {}/{}...".format(i, dp_count))

                # 既に更新済みかチェック
                if dp.Retained:
                    logger.info("Design point {} is already retained (updated)".format(i))
                    dp_success_count += 1
                    continue

                # 設計ポイントを更新
                logger.info("Updating design point {}...".format(i))
                dp.Update()

                # 更新完了確認
                if dp.Retained:
                    logger.info("Design point {} updated successfully".format(i))
                    dp_success_count += 1
                else:
                    logger.warning("Design point {} update completed but not retained".format(i))

            except Exception as e:
                logger.error("Failed to update design point {}: {}".format(i, str(e)))
                # 1つの設計ポイントが失敗しても続行

        result["dp_success"] = dp_success_count
        logger.info("Design points summary: {}/{} successful".format(
            dp_success_count, dp_count
        ))

        # プロジェクトを保存
        _safe_save(project_path, logger)

        # 全ての設計ポイントが成功した場合のみ success = True
        if dp_success_count == dp_count:
            result["success"] = True
            logger.info("Project processing completed successfully")
        else:
            result["error"] = "Some design points failed to update"
            logger.warning("Project processing completed with errors")

    except Exception as e:
        error_msg = "Unexpected error during project processing: {}".format(str(e))
        logger.error(error_msg)
        result["error"] = error_msg

    return result


def _safe_save(project_path, logger):
    # type: (str, logging.Logger) -> None
    """
    プロジェクトを安全に保存

    Args:
        project_path (str): プロジェクトファイルのパス
        logger (logging.Logger): ロガーインスタンス
    """
    try:
        logger.info("Saving project...")
        Save()
        logger.info("Project saved successfully")
    except Exception as e:
        logger.error("Failed to save project: {}".format(str(e)))

        # 別名保存を試みる
        try:
            backup_path = _get_backup_path(project_path)
            logger.info("Attempting to save as backup: {}".format(backup_path))
            Save(FilePath=backup_path)
            logger.info("Project saved as backup successfully")
        except Exception as e2:
            logger.error("Failed to save backup: {}".format(str(e2)))


def _get_backup_path(original_path):
    # type: (str) -> str
    """
    バックアップファイルのパスを生成

    Args:
        original_path (str): 元のファイルパス

    Returns:
        str: バックアップファイルパス
    """
    dir_name = os.path.dirname(original_path)
    base_name = os.path.basename(original_path)
    name, ext = os.path.splitext(base_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = "{}_backup_{}{}".format(name, timestamp, ext)
    return os.path.join(dir_name, backup_name)


def _format_single_project_summary(project_number, total_projects, result,
                                   elapsed_time, overall_successful, overall_processed):
    # type: (int, int, dict, timedelta, int, int) -> str
    """
    個別プロジェクトの処理結果サマリーを整形

    Args:
        project_number (int): 現在のプロジェクト番号
        total_projects (int): 総プロジェクト数
        result (dict): プロジェクトの処理結果
        elapsed_time (timedelta): このプロジェクトの処理時間
        overall_successful (int): これまでに成功したプロジェクト数
        overall_processed (int): これまでに処理したプロジェクト数

    Returns:
        str: 整形されたサマリー
    """
    from email_utils import _format_timedelta

    lines = []

    # プロジェクト情報
    lines.append("プロジェクト処理完了 ({}/{})".format(project_number, total_projects))
    lines.append("")
    lines.append("プロジェクト名: {}".format(result["project"]))
    lines.append("処理結果: {}".format("成功" if result["success"] else "失敗"))
    lines.append("処理時間: {}".format(_format_timedelta(elapsed_time)))
    lines.append("")

    # 設計ポイントの結果
    if result["dp_total"] > 0:
        lines.append("設計ポイント:")
        lines.append("  総数: {}".format(result["dp_total"]))
        lines.append("  成功: {}".format(result["dp_success"]))
        lines.append("  失敗: {}".format(result["dp_total"] - result["dp_success"]))
        lines.append("")

    # エラー情報
    if not result["success"] and result.get("error"):
        lines.append("エラー: {}".format(result["error"]))
        lines.append("")

    # 全体の進捗
    lines.append("全体の進捗:")
    lines.append("  処理済み: {}/{}".format(overall_processed, total_projects))
    lines.append("  成功: {}".format(overall_successful))
    lines.append("  失敗: {}".format(overall_processed - overall_successful))
    remaining = total_projects - overall_processed
    if remaining > 0:
        lines.append("  残り: {}".format(remaining))

    return "\n".join(lines)


def _create_single_project_subject(project_number, total_projects, result):
    # type: (int, int, dict) -> str
    """
    個別プロジェクトのメール件名を作成

    Args:
        project_number (int): 現在のプロジェクト番号
        total_projects (int): 総プロジェクト数
        result (dict): プロジェクトの処理結果

    Returns:
        str: メール件名
    """
    status = "SUCCESS" if result["success"] else "FAILED"
    project_name = result["project"]

    return "[Ansys Batch] {} - {}/{} - {}".format(
        status, project_number, total_projects, project_name
    )


def main():
    # type: () -> None
    """
    メイン処理

    複数のプロジェクトを順次処理し、結果をメールで通知
    """
    # ロガーのセットアップ
    logger, email_handler = setup_logger()

    logger.info("*" * 60)
    logger.info("Ansys Workbench Batch Runner - START")
    logger.info("*" * 60)

    start_time = datetime.now()
    logger.info("Start time: {}".format(start_time.strftime("%Y-%m-%d %H:%M:%S")))
    logger.info("Total projects to process: {}".format(len(PROJECTS)))

    # 各プロジェクトを処理
    project_results = []
    successful_count = 0

    for i, project_path in enumerate(PROJECTS, 1):
        # プロジェクト開始時のメール通知を送信
        project_start_time = datetime.now()
        project_name = os.path.basename(project_path)

        start_log = email_handler.get_logs()
        send_project_start_email(
            project_number=i,
            total_projects=len(PROJECTS),
            project_name=project_name,
            start_time=project_start_time,
            overall_successful=successful_count,
            overall_processed=i - 1,
            full_log=start_log,
            logger=logger
        )

        # プロジェクトを処理
        result = process_project(project_path, logger)
        project_results.append(result)

        if result["success"]:
            successful_count += 1

        # プロジェクト完了ごとにメール送信
        project_end_time = datetime.now()
        project_elapsed_time = project_end_time - project_start_time

        # 個別プロジェクトのサマリーを作成
        project_summary = _format_single_project_summary(
            project_number=i,
            total_projects=len(PROJECTS),
            result=result,
            elapsed_time=project_elapsed_time,
            overall_successful=successful_count,
            overall_processed=i
        )

        # 個別プロジェクトのメール件名を作成
        project_subject = _create_single_project_subject(i, len(PROJECTS), result)

        # 現在までのログを取得
        full_log = email_handler.get_logs()

        # メール送信
        send_email(project_subject, project_summary, full_log, logger)

    # 処理完了
    end_time = datetime.now()
    elapsed_time = end_time - start_time

    logger.info("*" * 60)
    logger.info("Ansys Workbench Batch Runner - COMPLETED")
    logger.info("*" * 60)
    logger.info("End time: {}".format(end_time.strftime("%Y-%m-%d %H:%M:%S")))
    logger.info("Total time: {}".format(elapsed_time))
    logger.info("Successful projects: {}/{}".format(successful_count, len(PROJECTS)))

    # サマリーとメール送信
    summary = format_summary(
        total_projects=len(PROJECTS),
        successful_projects=successful_count,
        failed_projects=len(PROJECTS) - successful_count,
        project_results=project_results,
        elapsed_time=elapsed_time
    )

    subject = create_subject(successful_count, len(PROJECTS))
    full_log = email_handler.get_logs()

    # メール送信
    send_email(subject, summary, full_log, logger)

    logger.info("Script finished")

    # 終了コード
    if successful_count == len(PROJECTS):
        sys.exit(0)  # 全て成功
    else:
        sys.exit(1)  # 一部または全て失敗


if __name__ == "__main__":
    # IronPython環境では __name__ が "__main__" にならない場合があるため
    # スクリプトとして実行された場合は必ず main() を呼ぶ
    main()
