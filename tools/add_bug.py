#!/usr/bin/env python3
"""
添加 Bug 记录工具 — 创建 failure_database/ 下的单个 Bug Markdown 条目。

用法：
    python tools/add_bug.py                          # 交互式创建
    python tools/add_bug.py --quick "标题" "解决方案"  # 快速添加
    python tools/add_bug.py --help
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


BUG_TEMPLATE = """# {title}

## 问题现象
{phenomenon}

## 根因
{causes}

## 解决方案
{solution}

## 验证
{verification}

## 相关项目
{related_projects}
"""


def find_experience_lib() -> Path:
    """自动定位经验库根目录（本文件在 tools/ 下）"""
    return Path(__file__).resolve().parent.parent


def failure_db_dir() -> Path:
    """failure_database 目录（当前 Bug 记录位置，替代已废弃的 bugs/）"""
    return find_experience_lib() / "failure_database"


def slugify(title: str) -> str:
    """把标题转成文件名 slug：保留 ASCII 字母数字，其余转 '-'"""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")
    return slug


def make_filename(title: str) -> str:
    """生成文件名；英文标题用 slug，中文标题回退为 bug_<时间戳>"""
    slug = slugify(title)
    if slug:
        return f"{slug}.md"
    return f"bug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"


def make_output_path(title: str) -> Path:
    """返回目标路径；若文件名已存在，自动追加序号避免覆盖"""
    out_dir = failure_db_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    base = make_filename(title)
    candidate = out_dir / base
    i = 1
    while candidate.exists():
        stem = Path(base).stem
        suffix = Path(base).suffix
        candidate = out_dir / f"{stem}_{i}{suffix}"
        i += 1
    return candidate


def create_bug(title: str, phenomenon: str, causes: str,
               solution: str, verification: str, related_projects: str) -> Path:
    """写入单个 failure_database 条目，返回写入路径"""
    out_path = make_output_path(title)
    content = BUG_TEMPLATE.format(
        title=title,
        phenomenon=phenomenon or "（待补充）",
        causes=causes or "（待补充）",
        solution=solution or "（待补充）",
        verification=verification or "（待补充）",
        related_projects=related_projects or "（未指定）",
    )
    out_path.write_text(content, encoding="utf-8")
    print(f"[OK] Bug 记录已写入：{out_path}")
    return out_path


def interactive_mode():
    print("=== 添加 Bug 记录（写入 failure_database/） ===")
    print()

    title = input("Bug 标题：").strip()
    if not title:
        print("标题不能为空，已退出。")
        sys.exit(1)

    print("问题现象（多行，空行结束）：")
    phenomenon = _multiline_input()
    print("根因（多行，空行结束）：")
    causes = _multiline_input()
    print("解决方案（多行，空行结束）：")
    solution = _multiline_input()
    print("验证方式（多行，空行结束）：")
    verification = _multiline_input()
    related_projects = input("相关项目（逗号分隔）：").strip()

    target = make_output_path(title)
    print("\n" + "=" * 50)
    print("请确认以下内容：")
    print(f"  标题：{title}")
    print(f"  文件：{target}")
    print(f"  现象：{phenomenon[:40]}{'...' if len(phenomenon) > 40 else ''}")
    confirm = input("\n确认创建？(Y/n)：").strip().lower()
    if confirm in ("", "y", "yes"):
        create_bug(title, phenomenon, causes, solution, verification, related_projects)
    else:
        print("已取消。")


def quick_mode(title: str, solution: str):
    create_bug(
        title=title,
        phenomenon="（快速添加，待补充细节）",
        causes="（待补充）",
        solution=solution,
        verification="（待补充）",
        related_projects="（未指定）",
    )


def _multiline_input() -> str:
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines) if lines else "（待补充）"


def main():
    parser = argparse.ArgumentParser(
        description="经验库工具 — 添加 Bug 记录（写入 failure_database/）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--quick", nargs=2, metavar=("TITLE", "SOLUTION"),
                        help="快速添加（仅标题和解决方案）")
    args = parser.parse_args()

    if args.quick:
        quick_mode(args.quick[0], args.quick[1])
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
