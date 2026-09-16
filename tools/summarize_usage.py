#!/usr/bin/env python3
"""
汇总 Knowledge Agent 使用结果 — 读取 reports/usage/knowledge_usage.jsonl。

用法：
    python tools/summarize_usage.py
    python tools/summarize_usage.py --top 10
"""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Iterable


def find_experience_lib() -> Path:
    """自动定位经验库根目录（本文件在 tools/ 下）"""
    return Path(__file__).resolve().parent.parent


def default_log_path() -> Path:
    return find_experience_lib() / "reports" / "usage" / "knowledge_usage.jsonl"


def read_records(log_path: Path) -> list[dict]:
    if not log_path.exists():
        return []
    records: list[dict] = []
    for line_no, line in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{log_path}:{line_no} JSON 解析失败：{exc}") from exc
    return records


def percent(numerator: int | float, denominator: int | float) -> str:
    if not denominator:
        return "N/A"
    return f"{numerator / denominator * 100:.1f}%"


def average(values: Iterable[int | float]) -> str:
    values = list(values)
    if not values:
        return "N/A"
    return f"{sum(values) / len(values):.2f}"


def as_list(record: dict, key: str) -> list[str]:
    value = record.get(key) or []
    return value if isinstance(value, list) else []


def print_counter(title: str, counter: Counter[str], limit: int) -> None:
    print()
    print(title)
    if not counter:
        print("- 无")
        return
    for i, (item, count) in enumerate(counter.most_common(limit), 1):
        print(f"{i}. {item} — {count} 次")


def summarize(records: list[dict], top: int) -> None:
    total = len(records)
    knowledge_called = [r for r in records if r.get("knowledge_called")]
    hit_tasks = [r for r in knowledge_called if as_list(r, "retrieved_ids")]
    adopted_tasks = [r for r in knowledge_called if as_list(r, "used_ids")]
    not_adopted_tasks = [r for r in knowledge_called if not as_list(r, "used_ids")]

    total_retrieved = sum(len(as_list(r, "retrieved_ids")) for r in records)
    total_used = sum(len(as_list(r, "used_ids")) for r in records)
    repeated_bug_tasks = [r for r in records if as_list(r, "repeated_bug_ids")]
    repeated_bug_count = sum(len(as_list(r, "repeated_bug_ids")) for r in records)

    first_pass_tasks = [
        r for r in records
        if r.get("test_passed") is True and int(r.get("revision_count") or 0) <= 1
    ]
    adopted_first_pass = [
        r for r in adopted_tasks
        if r.get("test_passed") is True and int(r.get("revision_count") or 0) <= 1
    ]
    not_adopted_first_pass = [
        r for r in not_adopted_tasks
        if r.get("test_passed") is True and int(r.get("revision_count") or 0) <= 1
    ]

    used_counter: Counter[str] = Counter()
    retrieved_not_used_counter: Counter[str] = Counter()
    repeated_bug_counter: Counter[str] = Counter()
    for record in records:
        retrieved = set(as_list(record, "retrieved_ids"))
        used = set(as_list(record, "used_ids"))
        used_counter.update(used)
        retrieved_not_used_counter.update(retrieved - used)
        repeated_bug_counter.update(as_list(record, "repeated_bug_ids"))

    print("Knowledge Usage Summary")
    print()
    print(f"任务总数：{total}")
    print(f"Knowledge 调用任务：{len(knowledge_called)}")
    print(f"经验命中率：{percent(len(hit_tasks), len(knowledge_called))}")
    print(f"经验采用率：{percent(total_used, total_retrieved)}")
    print(f"有效任务率：{percent(len(adopted_tasks), len(knowledge_called))}")
    print()
    print("一次通过率：")
    print(f"- 全部任务：{percent(len(first_pass_tasks), total)}")
    print(f"- 采用经验：{percent(len(adopted_first_pass), len(adopted_tasks))}")
    print(f"- 未采用经验：{percent(len(not_adopted_first_pass), len(not_adopted_tasks))}")
    print()
    print("平均修改轮数：")
    print(f"- 全部任务：{average(int(r.get('revision_count') or 0) for r in records)}")
    print(f"- 采用经验：{average(int(r.get('revision_count') or 0) for r in adopted_tasks)}")
    print(f"- 未采用经验：{average(int(r.get('revision_count') or 0) for r in not_adopted_tasks)}")
    print()
    print(f"旧 Bug 复发任务：{len(repeated_bug_tasks)}")
    print(f"旧 Bug 复发次数：{repeated_bug_count}")

    print_counter("TOP 被采用经验：", used_counter, top)
    print_counter("TOP 命中但未采用经验：", retrieved_not_used_counter, top)
    print_counter("TOP 复发旧 Bug：", repeated_bug_counter, top)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="经验库工具 — 汇总 Knowledge Agent 使用记录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--log", type=Path, default=default_log_path(),
                        help="日志路径，默认 reports/usage/knowledge_usage.jsonl")
    parser.add_argument("--top", type=int, default=5, help="TOP 列表数量，默认 5")
    args = parser.parse_args()

    records = read_records(args.log)
    if not records:
        print(f"暂无使用记录：{args.log}")
        return
    summarize(records, args.top)


if __name__ == "__main__":
    main()
