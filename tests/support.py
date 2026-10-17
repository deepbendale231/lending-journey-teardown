"""Build a small, internally consistent evidence repo in a temp dir, so tests can break one thing at a time."""

from __future__ import annotations

from pathlib import Path

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def build(
    root: Path,
    steps: int = 3,
    friction: list[tuple] | None = None,
    rice: list[tuple] | None = None,
    rbi_observed: tuple = ("Yes", "No", "Could not observe"),
    verified: str = "2026-10-17",
    boundary: str = "up to the OTP gate",
    screenshots: tuple = ("01", "02", "03"),
    with_pdfs: bool = True,
) -> Path:
    (root / "screenshots").mkdir(parents=True, exist_ok=True)
    (root / "exports").mkdir(exist_ok=True)
    (root / "reports").mkdir(exist_ok=True)
    for n in screenshots:
        (root / "screenshots" / f"{n}_screen.png").write_bytes(PNG)
    idx = "\n".join(f"| {n} | `{n}_screen.png` | Screen {n} | {int(n)} | none |" for n in screenshots)
    (root / "screenshots" / "INDEX.md").write_text(
        f"# Index\n<!-- INDEX:START -->\n| No | File | Screen | Step | Redactions |\n|---|---|---|---|---|\n{idx}\n<!-- INDEX:END -->\n"
    )
    rows = "\n".join(f"| {i} | Screen {i} | goal | asks | 2 taps | {10 * i} | 0{min(i, 3)} | |" for i in range(1, steps + 1))
    (root / "01_journey_map.md").write_text(
        f"---\nflow_source: app\nevidence_boundary: {boundary}\ne2e_time_seconds: 95\n---\n# Journey\n"
        f"<!-- JOURNEY:START -->\n| # | Screen | User goal | What is asked | Effort (taps/fields) | Time (s) | Screenshot | Notes |\n"
        f"|---|---|---|---|---|---|---|---|\n{rows}\n<!-- JOURNEY:END -->\n"
    )
    friction = (
        friction
        if friction is not None
        else [
            ("F-01", "1", "Cost is hidden", "trust", "3", "01", "N1"),
            ("F-02", "2", "Too many fields", "effort", "2", "02", "N3"),
        ]
    )
    (root / "02_friction_log.csv").write_text(
        "id,step,issue,type,severity,evidence,need\n" + "".join(",".join(f'"{c}"' for c in r) + "\n" for r in friction)
    )
    obs = "\n".join(f"| {i} | Requirement {i} | para {i} | {o} | | | {verified} |" for i, o in enumerate(rbi_observed, 1))
    (root / "03_rbi_checklist.md").write_text(
        "# RBI\n<!-- RBI:START -->\n| # | Requirement (paraphrased) | RBI ref | Observed in app? | Screenshot | Note | Verified vs source |\n"
        f"|---|---|---|---|---|---|---|\n{obs}\n<!-- RBI:END -->\n"
    )
    rice = (
        rice
        if rice is not None
        else [
            ("Show cost upfront", "F-01", "40000", "users per quarter at amount screen", "2", "80", "2", "person-months"),
            ("Cut form fields", "F-02", "60000", "users per quarter at the form", "1", "80", "3", "person-months"),
            ("Add progress bar", "F-02", "60000", "all starts", "0.5", "50", "1", "person-months"),
        ]
    )
    (root / "04_rice.csv").write_text(
        "fix,friction_ids,reach,reach_assumption,impact,confidence,effort,effort_assumption,score,rank\n"
        + "".join(",".join(f'"{c}"' for c in r) + ",,\n" for r in rice)
    )
    for name in ("05_user_stories.md", "08_metrics_tree.md"):
        (root / name).write_text(f"# {name}\nPlain finished content.\n")
    (root / "06_PRD.md").write_text("# PRD\nPlain finished content.\n<!-- EVIDENCE:START -->\n<!-- EVIDENCE:END -->\n")
    (root / "07_ab_test_plan.md").write_text(
        "---\nbaseline_p: 0.30\ndelta: 0.02\nalpha: 0.05\npower: 0.80\nweekly_starts: 10000\nguardrail_p: 0.03\nguardrail_margin: 0.005\n---\n"
        "# Plan\n<!-- SAMPLE:START -->\n<!-- SAMPLE:END -->\n"
    )
    (root / "README.md").write_text("# Teardown\n<!-- HEADLINE:START -->\n<!-- HEADLINE:END -->\n")
    if with_pdfs:
        (root / "exports" / "PRD.pdf").write_bytes(b"%PDF-1.4")
        (root / "exports" / "RICE.pdf").write_bytes(b"%PDF-1.4")
    return root
