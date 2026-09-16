#!/usr/bin/env python3
"""
经验库索引构建工具 — 扫描 bugs、patterns、projects 目录，
自动生成 index/ 下的索引文件。

用法：
    python tools/build_index.py          # 重建所有索引
    python tools/build_index.py --check  # 仅检查不一致
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class BugEntry:
    num: int
    title: str
    file: str


@dataclass
class PatternEntry:
    name: str
    file: str
    domain: str = ""


@dataclass
class ProjectEntry:
    name: str
    dir: str
    tech_stack: str = ""
    status: str = ""


def find_experience_lib() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_bugs(bugs_dir: Path) -> list[BugEntry]:
    """解析 bugs 目录和 failure_database 目录下的所有 Bug 记录"""
    entries = []
    for md_file in sorted(bugs_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        for match in re.finditer(r"## Bug\s*(\d+)[：:]\s*(.+)", content):
            num = int(match.group(1))
            title = match.group(2).strip()
            entries.append(BugEntry(
                num=num,
                title=title,
                file=md_file.name,
            ))
    return entries


def parse_failure_db(fail_dir: Path) -> list[BugEntry]:
    """解析 failure_database 目录下的所有失败记录"""
    entries = []
    for i, md_file in enumerate(sorted(fail_dir.glob("*.md")), 1):
        content = md_file.read_text(encoding="utf-8")
        title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else md_file.stem
        entries.append(BugEntry(
            num=i,
            title=title,
            file=md_file.name,
        ))
    return entries


def parse_patterns(patterns_dir: Path) -> list[PatternEntry]:
    """解析 patterns 目录下的所有模式文档"""
    entries = []
    for md_file in sorted(patterns_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        # 从标题中提取模式名称
        title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else md_file.stem

        # 从 # 适用场景 段落推断领域
        domain = ""
        scene_match = re.search(r"适用场景\s*\n(.+)", content)
        if scene_match:
            scene_text = scene_match.group(1).lower()
            if "halcon" in scene_text:
                domain = "HALCON"
            elif "yolo" in scene_text:
                domain = "YOLO"
            elif "pyqt5" in scene_text or "qt" in scene_text:
                domain = "PyQt5"
            elif "label studio" in scene_text:
                domain = "Label Studio"

        entries.append(PatternEntry(
            name=name,
            file=md_file.name,
            domain=domain,
        ))
    return entries


def parse_projects(projects_dir: Path) -> list[ProjectEntry]:
    """解析 projects 目录下的所有项目"""
    entries = []
    for proj_dir in sorted(projects_dir.iterdir()):
        if not proj_dir.is_dir():
            continue
        readme = proj_dir / "README.md"
        if not readme.exists():
            entries.append(ProjectEntry(
                name=proj_dir.name,
                dir=proj_dir.name,
                status="（无 README）",
            ))
            continue

        content = readme.read_text(encoding="utf-8")

        # 提取技术栈
        tech_match = re.search(r"(?i)(?:技术栈|Tech Stack)[：:]\s*\n(.+)", content)
        tech_stack = ""
        if tech_match:
            tech_stack = tech_match.group(1).strip()

        # 提取状态
        status_match = re.search(r"(?i)(?:状态|结果|Status)[：:]\s*(.+)", content)
        status = status_match.group(1).strip() if status_match else ""

        # 提取标题
        title_match = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        name = title_match.group(1).strip() if title_match else proj_dir.name

        entries.append(ProjectEntry(
            name=name,
            dir=proj_dir.name,
            tech_stack=tech_stack,
            status=status,
        ))
    return entries


def build_bug_index(bugs: list[BugEntry]) -> str:
    lines = [
        "# Bug 索引",
        "",
        f"> 自动生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 由 tools/build_index.py 自动生成，请勿手动编辑",
        "",
        f"共 {len(bugs)} 条记录",
        "",
        "| # | 标题 | 文件 |",
        "|---|------|------|",
    ]
    for bug in bugs:
        lines.append(f"| {bug.num} | {bug.title} | `failure_database/{bug.file}` |")
    return "\n".join(lines) + "\n"


def build_pattern_index(patterns: list[PatternEntry]) -> str:
    lines = [
        "# 模式索引",
        "",
        f"> 自动生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 由 tools/build_index.py 自动生成，请勿手动编辑",
        "",
        f"共 {len(patterns)} 条记录",
        "",
        "| # | 模式名称 | 文件 | 领域 |",
        "|---|---------|------|------|",
    ]
    for i, p in enumerate(patterns, 1):
        lines.append(f"| {i} | {p.name} | `patterns/{p.file}` | {p.domain} |")
    return "\n".join(lines) + "\n"


def build_project_index(projects: list[ProjectEntry]) -> str:
    lines = [
        "# 项目索引",
        "",
        f"> 自动生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "> 由 tools/build_index.py 自动生成，请勿手动编辑",
        "",
        f"共 {len(projects)} 条记录",
        "",
        "| 项目名称 | 目录 | 技术栈 | 状态 |",
        "|---------|------|--------|------|",
    ]
    for p in projects:
        lines.append(f"| {p.name} | `projects/{p.dir}/` | {p.tech_stack} | {p.status} |")
    return "\n".join(lines) + "\n"


def write_index(file_path: Path, content: str):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    print(f"  [OK] {file_path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="AI 项目经验库 — 索引构建工具",
    )
    parser.add_argument("--check", action="store_true",
                        help="仅检查不一致，不写入文件")

    args = parser.parse_args()

    lib_root = find_experience_lib()
    index_dir = lib_root / "index"
    bugs_dir = lib_root / "bugs"
    fail_dir = lib_root / "failure_database"
    patterns_dir = lib_root / "patterns"
    projects_dir = lib_root / "projects"

    if not lib_root.exists():
        print(f"❌ 经验库根目录不存在：{lib_root}")
        sys.exit(1)

    print("[INFO] 构建经验库索引...\n")

    # 解析数据
    bugs = parse_bugs(bugs_dir) if bugs_dir.exists() else []
    bugs += parse_failure_db(fail_dir) if fail_dir.exists() else []
    print(f"  [BUGS] Bug 记录：{len(bugs)} 条（bugs: {bugs_dir.name if bugs_dir.exists() else 'N/A'} + failure_database）")
    patterns = parse_patterns(patterns_dir)
    print(f"  [PATTERNS] 模式文档：{len(patterns)} 篇")
    projects = parse_projects(projects_dir)
    print(f"  [PROJECTS] 项目文档：{len(projects)} 篇")

    if args.check:
        print("\n[DONE] 检查完成，未写入任何文件。")
        return

    print("\n写入索引文件...")

    # 生成并写入索引
    write_index(index_dir / "bug_index.md", build_bug_index(bugs))
    write_index(index_dir / "pattern_index.md", build_pattern_index(patterns))
    write_index(index_dir / "project_index.md", build_project_index(projects))

    print(f"\n[DONE] 索引构建完成！")
    print(f"   生成文件：")
    print(f"     index/bug_index.md")
    print(f"     index/pattern_index.md")
    print(f"     index/project_index.md")


if __name__ == "__main__":
    main()
