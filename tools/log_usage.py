#!/usr/bin/env python3
"""
记录 Knowledge Agent 使用结果 — 追加一条 JSONL 到 reports/usage/knowledge_usage.jsonl。

用法：
    python tools/log_usage.py --task-id T20260822-001 --project HikCameraManager \
        --task-type bugfix --retrieved-id failure_database/example.md \
        --used-id failure_database/example.md --test-passed true --revision-count 1 \
        --duration-minutes 18
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def find_experience_lib() -> Path:
    """自动定位经验库根目录（本文件在 tools/ 下）"""
    return Path(__file__).resolve().parent.parent


def default_log_path() -> Path:
    return find_experience_lib() / "reports" / "usage" / "knowledge_usage.jsonl"


def parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "y", "passed", "pass"}:
        return True
    if normalized in {"false", "0", "no", "n", "failed", "fail"}:
        return False
    if normalized in {"unknown", "none", "null", "not-run", "not_run", "skip", "skipped"}:
        return None
    raise argparse.ArgumentTypeError(f"无法解析布尔值：{value}")


def split_values(values: list[str] | None) -> list[str]:
    """支持重复参数，也支持单个参数内用逗号分隔"""
    result: list[str] = []
    for value in values or []:
        for item in value.split(","):
            item = item.strip()
            if item:
                result.append(item)
    return result


def make_task_id() -> str:
    return "T" + datetime.now().strftime("%Y%m%d-%H%M%S")


def append_record(record: dict, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")


def build_record(args: argparse.Namespace) -> dict:
    retrieved_ids = split_values(args.retrieved_id)
    used_ids = split_values(args.used_id)
    repeated_bug_ids = split_values(args.repeated_bug_id)
    return {
        "schema_version": 1,
        "task_id": args.task_id or make_task_id(),
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "project": args.project or "",
        "task_type": args.task_type or "",
        "knowledge_called": args.knowledge_called,
        "retrieved_ids": retrieved_ids,
        "used_ids": used_ids,
        "test_passed": args.test_passed,
        "revision_count": args.revision_count,
        "duration_minutes": args.duration_minutes,
        "repeated_bug_ids": repeated_bug_ids,
        "notes": args.notes or "",
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="经验库工具 — 记录 Knowledge Agent 使用结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--task-id", help="任务 ID；未提供时自动生成")
    parser.add_argument("--project", default="", help="项目名")
    parser.add_argument("--task-type", default="", help="任务类型，如 bugfix/feature/refactor/tooling")
    parser.add_argument("--knowledge-called", type=parse_bool, default=True,
                        help="是否调用经验库，默认 true")
    parser.add_argument("--retrieved-id", action="append",
                        help="检索命中的经验 ID/路径；可重复，也可逗号分隔")
    parser.add_argument("--used-id", action="append",
                        help="实际采用的经验 ID/路径；可重复，也可逗号分隔")
    parser.add_argument("--test-passed", type=parse_bool, default=None,
                        help="测试结果：true/false/unknown")
    parser.add_argument("--revision-count", type=int, default=0,
                        help="修改轮数，默认 0")
    parser.add_argument("--duration-minutes", type=float, default=None,
                        help="任务耗时（分钟）")
    parser.add_argument("--repeated-bug-id", action="append",
                        help="复发的旧 Bug ID/路径；可重复，也可逗号分隔")
    parser.add_argument("--notes", default="", help="补充说明")
    parser.add_argument("--log", type=Path, default=default_log_path(),
                        help="日志路径，默认 reports/usage/knowledge_usage.jsonl")
    args = parser.parse_args()

    record = build_record(args)
    append_record(record, args.log)
    print(f"[OK] 使用记录已追加：{args.log}")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
