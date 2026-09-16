from __future__ import annotations

from pathlib import Path


def test_knowledge_base_contains_at_least_30_markdown_files() -> None:
    root = Path(__file__).resolve().parents[2]
    files = list((root / "knowledge_base").rglob("*.md"))
    assert len(files) >= 30


def test_nine_top_level_knowledge_directories_exist() -> None:
    root = Path(__file__).resolve().parents[2]
    expected = {
        "01_基础知识",
        "02_技术知识",
        "03_AI知识",
        "04_项目经验",
        "05_问题与Bug",
        "06_解决方案",
        "07_代码案例",
        "08_最佳实践",
        "09_资料来源",
    }
    actual = {path.name for path in (root / "knowledge_base").iterdir() if path.is_dir()}
    assert expected.issubset(actual)
