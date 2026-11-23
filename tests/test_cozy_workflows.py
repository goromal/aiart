import glob
import json
import os

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..", "cozy-workflows")
FILES = sorted(glob.glob(os.path.join(ROOT, "*.api.json")))


def test_workflows_present():
    names = {os.path.basename(f)[:-len(".api.json")] for f in FILES}
    assert {"imggen21", "imgedit4", "imggen-quantized"} <= names


@pytest.mark.parametrize("path", FILES, ids=os.path.basename)
def test_cozy_workflow_shape(path):
    with open(path) as f:
        graph = json.load(f)
    meta = graph.pop("_cozy", {})
    for node_id, node in graph.items():
        assert "class_type" in node and "inputs" in node, node_id
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[1], int):
                assert value[0] in graph, (node_id, value)
    assert any(n["class_type"] == "SaveImage" for n in graph.values())
    if meta.get("kind") == "edit":
        assert graph[meta["image_node"]]["class_type"] == "LoadImage"
        assert "text" in graph[meta["prompt_node"]]["inputs"]
    else:
        prompts = [n for n in graph.values() if n["class_type"] == "PrimitiveStringMultiline"
                   and n.get("_meta", {}).get("title") == "Prompt"]
        assert len(prompts) == 1
