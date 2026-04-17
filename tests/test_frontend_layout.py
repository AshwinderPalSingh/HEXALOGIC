from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "api" / "static" / "layout-utils.js"
DOCK_MODULE = ROOT / "api" / "static" / "dock-layout.js"
APP_MODULE = ROOT / "api" / "static" / "sim8051-app.js"


def _run_node_layout_probe() -> dict:
    if shutil.which("node") is None:
        pytest.skip("node is not available in this environment")
    script = f"""
import * as layout from {json.dumps(MODULE.as_uri())};
import * as dock from {json.dumps(DOCK_MODULE.as_uri())};

const vertical = layout.resolveVerticalSplit(240, 260, 80);
const left = layout.resolveLeftColumnWidth({{
  leftStart: 320,
  delta: 120,
  workspaceWidth: 1400,
  rightWidth: 520,
}});
const right = layout.resolveRightColumnWidth({{
  rightStart: 560,
  delta: -140,
  workspaceWidth: 1400,
  leftWidth: 320,
}});
const center = dock.resolveStackDropZone(
  {{ left: 100, top: 100, right: 320, bottom: 280, width: 220, height: 180 }},
  210,
  190,
);
const edge = dock.resolveStackDropZone(
  {{ left: 100, top: 100, right: 320, bottom: 280, width: 220, height: 180 }},
  108,
  190,
);
let root = dock.createSplit(\"row\", [dock.createStack([\"a\"]), dock.createStack([\"b\"])], [0.5, 0.5]);
const rightId = root.children[1].id;
root = dock.splitStackInLayout(root, rightId, \"bottom\", \"c\");
const inserted = dock.findPanelLocation(root, \"c\");
root = dock.removePanelFromLayout(root, \"c\");
const removed = dock.findPanelLocation(root, \"c\");

console.log(JSON.stringify({{
  vertical,
  left,
  right,
  center,
  edge,
  insertedType: inserted?.parent?.type || inserted?.stack?.type || null,
  removed: removed || null,
}}));
"""
    result = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout.strip())


def test_frontend_layout_resize_math_stays_within_expected_bounds():
    payload = _run_node_layout_probe()

    assert payload["vertical"] == {"previous": 320, "next": 180}
    assert payload["left"] == 440
    assert payload["right"] == 644
    assert payload["center"]["zone"] == "center"
    assert payload["edge"]["zone"] == "left"
    assert payload["insertedType"] == "split"
    assert payload["removed"] is None


def test_frontend_renderer_uses_null_safe_panel_updates():
    source = APP_MODULE.read_text()

    assert "function safeSetHTML" in source
    assert "function refreshPanelRegistry" in source
    assert "function _beginUiTimingMeasurement" in source
    assert "function _finishUiTimingMeasurement" in source
    assert "ui_receive_to_paint_ms" in source
    assert "ui_dropped_frames" in source

    critical_patterns = [
        'byId("exec-state-panel").innerHTML',
        'byId("registers-panel-body").innerHTML',
        'byId("memory-ram").innerHTML',
        'byId("memory-xram").innerHTML',
        'byId("memory-rom").innerHTML',
        'byId("assembler-panel-body").innerHTML',
        'byId("trace-panel-body").innerHTML',
    ]
    for pattern in critical_patterns:
        assert pattern not in source


def test_dock_layout_keeps_inactive_panels_mounted_for_stable_rendering():
    source = DOCK_MODULE.read_text()

    assert "panel.hidden = panelId !== node.active;" in source
    assert "body.appendChild(panel);" in source


def test_dock_layout_uses_transform_based_panel_motion():
    source = DOCK_MODULE.read_text()

    assert "translate3d(" in source
    assert "panel.style.transform =" in source
