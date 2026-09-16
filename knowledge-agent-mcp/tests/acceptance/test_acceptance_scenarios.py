from __future__ import annotations

from pathlib import Path

from knowledge_agent_mcp.application import build_application
from knowledge_agent_mcp.models import ConsultKnowledgeRequest, ProjectContext


def test_acceptance_halcon_template_matching() -> None:
    app = build_application(Path(__file__).resolve().parents[2])
    result = app._consult_knowledge(
        ConsultKnowledgeRequest(
            task="开发HALCON 20.11模板匹配工具，使用C#和HDevelop。",
            stage="planning",
            project_context=ProjectContext(
                project_name="CSharp-Halcon",
                languages=["CSharp", "HDevelop"],
                technologies=["HALCON"],
                versions={"HALCON": "20.11"},
            ),
            max_results=10,
        ),
        "acc-halcon-template",
    )
    assert result["recommended_solutions"]
    assert result["similar_projects"]
    assert result["code_examples"]
    assert result["version_notes"]


def test_acceptance_label_studio_startup_error() -> None:
    app = build_application(Path(__file__).resolve().parents[2])
    result = app._consult_knowledge(
        ConsultKnowledgeRequest(
            task="No module named label_studio.__main__",
            stage="debugging",
            project_context=ProjectContext(
                languages=["Python"],
                technologies=["LabelStudio"],
            ),
            error_context="No module named label_studio.__main__",
            max_results=10,
        ),
        "acc-label-studio",
    )
    assert result["known_bugs"]
    assert result["recommended_solutions"]
    assert result["similar_projects"]


def test_acceptance_segmentation_offset() -> None:
    app = build_application(Path(__file__).resolve().parents[2])
    result = app._consult_knowledge(
        ConsultKnowledgeRequest(
            task="HALCON语义分割输出映射回原图发生偏移。",
            stage="debugging",
            project_context=ProjectContext(
                languages=["HDevelop"],
                technologies=["HALCON"],
                versions={"HALCON": "20.11"},
            ),
            error_context="坐标偏移 letterbox resize",
            max_results=10,
        ),
        "acc-segmentation-offset",
    )
    assert result["known_bugs"]
    assert result["recommended_solutions"]
    assert result["code_examples"]
    assert result["test_requirements"]
