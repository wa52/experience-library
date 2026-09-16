#!/usr/bin/env python3
"""
经验库搜索工具 — 按关键词搜索所有 Markdown 文件内容。

用法：
    python tools/search_experience.py "关键词"
    python tools/search_experience.py "关键词1 关键词2"    # AND 搜索
    python tools/search_experience.py --help
"""

import argparse
import re
import sys
from pathlib import Path


def find_experience_lib() -> Path:
    """自动定位经验库根目录（本文件在 tools/ 下）"""
    return Path(__file__).resolve().parent.parent


def gather_md_files(root: Path) -> list[Path]:
    """收集经验库下所有 .md 文件"""
    files = []
    # 排除隐藏目录和 __pycache__
    for p in root.rglob("*.md"):
        rel = p.relative_to(root).as_posix()
        if "/." not in rel and not rel.startswith(".") and "__pycache__" not in rel:
            files.append(p)
    return sorted(files)


def search_files(files: list[Path], keywords: list[str], case_sensitive: bool = False) -> list[dict]:
    """
    在文件中搜索关键词（AND 逻辑）。
    返回 [(文件路径, 行号, 匹配行内容), ...]
    """
    results = []
    flags = 0 if case_sensitive else re.IGNORECASE

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue  # 跳过无法读取的文件

        lines = content.split("\n")
        file_matches = []

        for lineno, line in enumerate(lines, 1):
            matched_all = True
            for kw in keywords:
                if not re.search(re.escape(kw), line, flags):
                    matched_all = False
                    break
            if matched_all:
                file_matches.append((lineno, line.strip()))

        if file_matches:
            results.append({
                "path": str(file_path.relative_to(file_path.parents[1])),  # 相对经验库根
                "title": _extract_title(content),
                "matches": file_matches,
            })

    return results


def _extract_title(content: str) -> str:
    """从 Markdown 内容中提取标题"""
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# ") or line.startswith("## "):
            return line.lstrip("# ").strip()
    return "(无标题)"


def print_results(results: list[dict], keywords: list[str]):
    """格式化输出搜索结果"""
    if not results:
        print(f"未找到包含关键词「{' '.join(keywords)}」的内容。")
        return

    total_matches = sum(len(r["matches"]) for r in results)
    print(f"找到 {len(results)} 个文件，共 {total_matches} 处匹配：\n")

    for r in results:
        print(f"  [FILE] {r['path']}")
        print(f"    标题：{r['title']}")
        for lineno, line in r["matches"][:5]:  # 每个文件最多显示 5 处
            marker = "  [H]" if _is_heading_line(line) else "     "
            print(f"{marker} L{lineno}: {line[:120]}")
        if len(r["matches"]) > 5:
            print(f"    ... 还有 {len(r['matches']) - 5} 处匹配")
        print()


def _is_heading_line(line: str) -> bool:
    return line.startswith("#")


def main():
    parser = argparse.ArgumentParser(
        description="AI 项目经验库 — 全文搜索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  search_experience.py "PyQt5"              # 查找 PyQt5 相关内容
  search_experience.py "相机 连接"            # AND 搜索同时包含两个关键词
  search_experience.py "HALCON ROI" -s      # 区分大小写
  search_experience.py -l                    # 列出所有索引文件
        """,
    )
    parser.add_argument("keywords", nargs="*", help="搜索关键词（多关键词=AND）")
    parser.add_argument("-s", "--case-sensitive", action="store_true", help="区分大小写")
    parser.add_argument("-l", "--list", action="store_true", help="列出所有经验库文件")

    args = parser.parse_args()

    lib_root = find_experience_lib()
    md_files = gather_md_files(lib_root)

    if args.list:
        print(f"经验库根目录：{lib_root}")
        print(f"共 {len(md_files)} 个 Markdown 文件：\n")
        for f in md_files:
            rel = f.relative_to(lib_root).as_posix()
            print(f"  {rel}")
        return

    if not args.keywords:
        parser.print_help()
        sys.exit(1)

    results = search_files(md_files, args.keywords, args.case_sensitive)
    print_results(results, args.keywords)

    # 返回状态码：找到结果返回 0，否则 1
    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
