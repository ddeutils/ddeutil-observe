from pathlib import Path

from ddeutil.workflow import Workflow, YamlParser


def test_get_workflow_data(test_path: Path):
    for wf in YamlParser.finds(
        Workflow, paths=[test_path.parent / "docs/examples/conf"]
    ):
        print(wf)
