#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Stage:
    key: str
    number: int
    prompt_file: str
    outputs: tuple[str, ...]
    context_files: tuple[str, ...]
    description: str
    file_instructions: tuple[str, ...]


REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = REPO_ROOT / "workspace"
INPUT_DIR = WORKSPACE_DIR / "input"
INTERMEDIATE_DIR = WORKSPACE_DIR / "intermediate"
OUTPUT_DIR = WORKSPACE_DIR / "output"
LOGS_DIR = WORKSPACE_DIR / "logs"
AGENT_FILE = REPO_ROOT / "AGENT.md"
EXTRACTION_TEMPLATE = REPO_ROOT / "templates" / "extraction_template.json"
EXTRACTION_FILE = INTERMEDIATE_DIR / "extraction.json"
WORKSPACE_PRESERVED_FILES = {".gitkeep"}


COMPACT_STAGES: tuple[Stage, ...] = (
    Stage(
        key="analyze",
        number=1,
        prompt_file="prompts/compact/01_analyze_paper.md",
        outputs=(
            "workspace/intermediate/evidence_pack.md",
            "workspace/intermediate/extraction.json",
        ),
        context_files=(
            "templates/evidence_pack_template.md",
            "templates/extraction_template.json",
        ),
        description="Read the paper once, build a durable evidence pack, and fully populate the extraction JSON.",
        file_instructions=(
            "Write a comprehensive evidence pack to `workspace/intermediate/evidence_pack.md`.",
            "Also update `workspace/intermediate/extraction.json` in place.",
            "Keep `workspace/intermediate/extraction.json` valid JSON after your edits.",
        ),
    ),
    Stage(
        key="report",
        number=2,
        prompt_file="prompts/compact/02_write_report.md",
        outputs=("workspace/output/final_report.md",),
        context_files=(
            "workspace/intermediate/evidence_pack.md",
            "workspace/intermediate/extraction.json",
            "templates/report_template.md",
            "configs/report_schema.md",
            "configs/style_guide.md",
        ),
        description="Write the final report from the evidence pack while verifying important claims against the PDF.",
        file_instructions=(
            "Write the report to `workspace/output/final_report.md`.",
        ),
    ),
    Stage(
        key="review",
        number=3,
        prompt_file="prompts/compact/03_review_and_revise.md",
        outputs=(
            "workspace/intermediate/review_notes.md",
            "workspace/output/final_report.md",
        ),
        context_files=(
            "workspace/intermediate/evidence_pack.md",
            "workspace/intermediate/extraction.json",
            "workspace/output/final_report.md",
            "configs/quality_checklist.md",
            "configs/quality_rubric.md",
        ),
        description="Review the report, log issues, and revise the final output.",
        file_instructions=(
            "Write review findings to `workspace/intermediate/review_notes.md`.",
            "Revise `workspace/output/final_report.md` directly after the review.",
        ),
    ),
)


LEGACY_STAGES: tuple[Stage, ...] = (
    Stage(
        key="parse",
        number=1,
        prompt_file="prompts/01_parse_and_index.md",
        outputs=("workspace/intermediate/parsed_notes.md",),
        context_files=(),
        description="Parse the PDF structure and build an index of sections, figures, and tables.",
        file_instructions=(
            "Write a structured parsing note to `workspace/intermediate/parsed_notes.md`.",
            "Do not write polished summary prose yet.",
        ),
    ),
    Stage(
        key="claims",
        number=2,
        prompt_file="prompts/02_extract_core_claims.md",
        outputs=("workspace/intermediate/extraction.json",),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "templates/extraction_template.json",
        ),
        description="Extract motivation, problem setting, and main contributions.",
        file_instructions=(
            "Update `workspace/intermediate/extraction.json` in place.",
            "Keep the file as valid JSON after your edits.",
        ),
    ),
    Stage(
        key="method",
        number=3,
        prompt_file="prompts/03_extract_main_technology.md",
        outputs=(
            "workspace/intermediate/method_notes.md",
            "workspace/intermediate/extraction.json",
        ),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "workspace/intermediate/extraction.json",
        ),
        description="Extract the mechanism-level method details.",
        file_instructions=(
            "Write mechanism-focused notes to `workspace/intermediate/method_notes.md`.",
            "Also update the `main_technology` fields inside `workspace/intermediate/extraction.json`.",
            "Keep `workspace/intermediate/extraction.json` valid JSON after your edits.",
        ),
    ),
    Stage(
        key="experiments",
        number=4,
        prompt_file="prompts/04_extract_experiments.md",
        outputs=(
            "workspace/intermediate/experiment_notes.md",
            "workspace/intermediate/extraction.json",
        ),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "workspace/intermediate/extraction.json",
        ),
        description="Extract datasets, metrics, results, ablations, and key tables.",
        file_instructions=(
            "Write experiment notes to `workspace/intermediate/experiment_notes.md`.",
            "Also update the `experiments`, `tables`, and `figures` fields inside `workspace/intermediate/extraction.json`.",
            "Keep `workspace/intermediate/extraction.json` valid JSON after your edits.",
        ),
    ),
    Stage(
        key="compare",
        number=5,
        prompt_file="prompts/05_compare_and_limitations.md",
        outputs=("workspace/intermediate/extraction.json",),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "workspace/intermediate/method_notes.md",
            "workspace/intermediate/experiment_notes.md",
            "workspace/intermediate/extraction.json",
        ),
        description="Add comparison, limitations, and future-work analysis.",
        file_instructions=(
            "Update `workspace/intermediate/extraction.json` in place.",
            "Fill the `comparison`, `limitations`, and `future_work` sections.",
            "Keep the file as valid JSON after your edits.",
        ),
    ),
    Stage(
        key="report",
        number=6,
        prompt_file="prompts/06_write_report.md",
        outputs=("workspace/output/final_report.md",),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "workspace/intermediate/method_notes.md",
            "workspace/intermediate/experiment_notes.md",
            "workspace/intermediate/extraction.json",
            "templates/report_template.md",
            "templates/extraction_template.json",
            "configs/report_schema.md",
            "configs/style_guide.md",
        ),
        description="Write the full Markdown report from the structured extraction.",
        file_instructions=(
            "Write the report to `workspace/output/final_report.md`.",
            "Use the template and config files listed below.",
        ),
    ),
    Stage(
        key="review",
        number=7,
        prompt_file="prompts/07_review_and_revise.md",
        outputs=(
            "workspace/intermediate/review_notes.md",
            "workspace/output/final_report.md",
        ),
        context_files=(
            "workspace/intermediate/parsed_notes.md",
            "workspace/intermediate/method_notes.md",
            "workspace/intermediate/experiment_notes.md",
            "workspace/intermediate/extraction.json",
            "workspace/output/final_report.md",
            "configs/quality_checklist.md",
            "configs/quality_rubric.md",
        ),
        description="Review the report, log issues, and revise the final output.",
        file_instructions=(
            "Write review findings to `workspace/intermediate/review_notes.md`.",
            "Revise `workspace/output/final_report.md` directly after the review.",
        ),
    ),
)


WORKFLOWS: dict[str, tuple[Stage, ...]] = {
    "compact": COMPACT_STAGES,
    "legacy": LEGACY_STAGES,
}
DEFAULT_WORKFLOW = "compact"


class PipelineError(RuntimeError):
    pass


TOKEN_USED_PATTERN = re.compile(r"tokens used\s*\n\s*([0-9][0-9,]*)", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orchestrate the paper report pipeline with codex exec."
    )
    parser.add_argument(
        "--pdf",
        required=True,
        help="Path to the input paper PDF. Relative paths are resolved from the repo root.",
    )
    parser.add_argument(
        "--workflow",
        choices=WORKFLOWS.keys(),
        default=DEFAULT_WORKFLOW,
        help="Workflow to run. `compact` is optimized for high-context models; `legacy` preserves the original seven-stage split.",
    )
    parser.add_argument(
        "--from-stage",
        help="Stage to start from. Because `workspace/intermediate` is reset on each run, this must be the first stage of the selected workflow.",
    )
    parser.add_argument(
        "--to-stage",
        help="Stage to stop at. Defaults to the last stage of the selected workflow.",
    )
    parser.add_argument(
        "--codex-bin",
        default="codex",
        help="Codex CLI executable to invoke.",
    )
    parser.add_argument(
        "--model",
        help="Optional model name passed through to codex exec.",
    )
    parser.add_argument(
        "--profile",
        help="Optional Codex profile passed through to codex exec.",
    )
    parser.add_argument(
        "--sandbox",
        choices=("read-only", "workspace-write", "danger-full-access"),
        default="workspace-write",
        help="Sandbox mode passed to codex exec.",
    )
    parser.add_argument(
        "--full-auto",
        action="store_true",
        help="Pass --full-auto to codex exec.",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Pass --search to codex exec.",
    )
    parser.add_argument(
        "--skip-git-repo-check",
        action="store_true",
        default=True,
        help="Pass --skip-git-repo-check to codex exec. Enabled by default.",
    )
    parser.add_argument(
        "--no-skip-git-repo-check",
        dest="skip_git_repo_check",
        action="store_false",
        help="Do not pass --skip-git-repo-check.",
    )
    parser.add_argument(
        "--ephemeral",
        action="store_true",
        help="Pass --ephemeral to codex exec.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Prepare prompts and logs without invoking codex exec.",
    )
    parser.add_argument(
        "--force-init-extraction",
        action="store_true",
        help="Always overwrite workspace/intermediate/extraction.json from the template before running.",
    )
    parser.add_argument(
        "--codex-arg",
        action="append",
        default=[],
        help="Additional raw argument to append to codex exec. Repeat as needed.",
    )
    return parser.parse_args()


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


def ensure_repo_layout() -> None:
    if not AGENT_FILE.exists():
        raise PipelineError(f"Missing required file: {AGENT_FILE}")
    if not EXTRACTION_TEMPLATE.exists():
        raise PipelineError(f"Missing required file: {EXTRACTION_TEMPLATE}")
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def ensure_extraction_file(force_reset: bool) -> None:
    if force_reset or not EXTRACTION_FILE.exists():
        shutil.copyfile(EXTRACTION_TEMPLATE, EXTRACTION_FILE)


def reset_intermediate_dir() -> int:
    removed_entries = 0
    for entry in INTERMEDIATE_DIR.iterdir():
        if entry.name in WORKSPACE_PRESERVED_FILES:
            continue

        if entry.is_dir() and not entry.is_symlink():
            shutil.rmtree(entry)
        else:
            entry.unlink()
        removed_entries += 1

    return removed_entries


def relative_to_root(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def stage_slice(stages: tuple[Stage, ...], from_stage: str, to_stage: str) -> tuple[Stage, ...]:
    stage_by_key = {stage.key: stage for stage in stages}
    if from_stage not in stage_by_key:
        available = ", ".join(stage.key for stage in stages)
        raise PipelineError(f"Unknown stage `{from_stage}` for this workflow. Available stages: {available}")
    if to_stage not in stage_by_key:
        available = ", ".join(stage.key for stage in stages)
        raise PipelineError(f"Unknown stage `{to_stage}` for this workflow. Available stages: {available}")

    start = next(i for i, stage in enumerate(stages) if stage.key == from_stage)
    end = next(i for i, stage in enumerate(stages) if stage.key == to_stage)
    if start > end:
        raise PipelineError("--from-stage must come before or equal to --to-stage.")
    return stages[start : end + 1]


def validate_entry_stage(stages: tuple[Stage, ...], from_stage: str) -> None:
    first_stage = stages[0].key
    if from_stage != first_stage:
        raise PipelineError(
            f"`--from-stage {from_stage}` is not supported because "
            "`workspace/intermediate` is cleared at the start of every run. "
            f"Start from `{first_stage}` instead."
        )


def build_stage_prompt(stage: Stage, total_stages: int, pdf_path: Path) -> str:
    must_read = [
        "AGENT.md",
        stage.prompt_file,
        relative_to_root(pdf_path),
    ]
    if stage.context_files:
        must_read.extend(stage.context_files)

    must_read_block = "\n".join(f"- `{item}`" for item in must_read)
    output_block = "\n".join(f"- `{item}`" for item in stage.outputs)
    instruction_block = "\n".join(f"- {item}" for item in stage.file_instructions)

    return textwrap.dedent(
        f"""\
        You are executing stage {stage.number} of {total_stages} for the paper report pipeline.

        Stage key:
        - `{stage.key}`

        Stage goal:
        - {stage.description}

        Read these files before writing anything:
        {must_read_block}

        Required output files for this stage:
        {output_block}

        File-writing requirements:
        {instruction_block}

        Global requirements:
        - Follow `AGENT.md` and the stage prompt file exactly.
        - Treat `{relative_to_root(pdf_path)}` as the only input paper.
        - All intermediate notes and the final report should be written in Chinese unless the source wording must stay in English.
        - Be faithful to the paper. If a detail is missing or ambiguous, say so explicitly instead of guessing.
        - Do not invent figure numbers, table numbers, equations, metadata, or experimental values.
        - If you edit `workspace/intermediate/extraction.json`, keep it valid JSON.
        - Update the required output files directly in the workspace.
        - Keep your final response short: report status, files updated, and any unresolved uncertainty.
        """
    )


def build_codex_command(args: argparse.Namespace, last_message_path: Path) -> list[str]:
    command = [args.codex_bin]
    if args.search:
        command.append("--search")
    command.extend(
        [
            "exec",
            "-C",
            str(REPO_ROOT),
            "--sandbox",
            args.sandbox,
            "-o",
            str(last_message_path),
        ]
    )
    if args.skip_git_repo_check:
        command.append("--skip-git-repo-check")
    if args.model:
        command.extend(["--model", args.model])
    if args.profile:
        command.extend(["--profile", args.profile])
    if args.full_auto:
        command.append("--full-auto")
    if args.ephemeral:
        command.append("--ephemeral")
    command.extend(args.codex_arg)
    command.append("-")
    return command


def write_run_manifest(
    run_dir: Path,
    args: argparse.Namespace,
    pdf_path: Path,
    stages: Iterable[Stage],
    intermediate_entries_cleared: int,
) -> None:
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "repo_root": str(REPO_ROOT),
        "pdf": relative_to_root(pdf_path),
        "workflow": args.workflow,
        "intermediate_reset_on_startup": True,
        "intermediate_entries_cleared": intermediate_entries_cleared,
        "stages": [stage.key for stage in stages],
        "codex_bin": args.codex_bin,
        "model": args.model,
        "profile": args.profile,
        "sandbox": args.sandbox,
        "full_auto": args.full_auto,
        "search": args.search,
        "ephemeral": args.ephemeral,
        "skip_git_repo_check": args.skip_git_repo_check,
        "dry_run": args.dry_run,
        "force_init_extraction": args.force_init_extraction,
        "codex_arg": args.codex_arg,
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def extract_tokens_used(log_path: Path) -> int | None:
    if not log_path.exists():
        return None

    content = log_path.read_text(encoding="utf-8", errors="replace")
    matches = TOKEN_USED_PATTERN.findall(content)
    if not matches:
        return None

    return int(matches[-1].replace(",", ""))


def write_token_summary(run_dir: Path, stage_tokens: list[tuple[Stage, int | None]]) -> Path:
    total_known = 0
    missing_stages: list[str] = []
    stages_payload = []

    for stage, tokens_used in stage_tokens:
        if tokens_used is None:
            missing_stages.append(stage.key)
        else:
            total_known += tokens_used

        stages_payload.append(
            {
                "stage": stage.key,
                "stage_number": stage.number,
                "tokens_used": tokens_used,
            }
        )

    payload = {
        "stages": stages_payload,
        "total_tokens_used": total_known,
        "all_stage_tokens_available": not missing_stages,
        "missing_stages": missing_stages,
    }

    summary_path = run_dir / "token_usage.json"
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return summary_path


def print_token_summary(stage_tokens: list[tuple[Stage, int | None]], summary_path: Path) -> None:
    print()
    print("token usage:")

    total_known = 0
    missing_stages: list[str] = []
    for stage, tokens_used in stage_tokens:
        if tokens_used is None:
            missing_stages.append(stage.key)
            print(f"- {stage.key}: unavailable")
            continue

        total_known += tokens_used
        print(f"- {stage.key}: {tokens_used:,}")

    if missing_stages:
        print(f"known total tokens used: {total_known:,}")
        print(f"stages without token data: {', '.join(missing_stages)}")
    else:
        print(f"total tokens used: {total_known:,}")

    print(f"token summary: {relative_to_root(summary_path)}")


def stream_process(command: list[str], prompt_text: str, log_path: Path) -> int:
    with log_path.open("w", encoding="utf-8") as log_file:
        log_file.write("$ " + " ".join(command) + "\n\n")
        process = subprocess.Popen(
            command,
            cwd=REPO_ROOT,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        assert process.stdin is not None
        assert process.stdout is not None
        process.stdin.write(prompt_text)
        process.stdin.close()

        for line in process.stdout:
            sys.stdout.write(line)
            log_file.write(line)

        return process.wait()


def validate_json_file(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {relative_to_root(path)}: {exc}") from exc

    if not isinstance(data, dict):
        raise PipelineError(f"{relative_to_root(path)} must contain a top-level JSON object.")

    template_data = json.loads(EXTRACTION_TEMPLATE.read_text(encoding="utf-8"))
    missing_keys = [key for key in template_data.keys() if key not in data]
    if missing_keys:
        raise PipelineError(
            f"{relative_to_root(path)} is missing top-level keys: {', '.join(missing_keys)}"
        )


def validate_non_empty(path: Path) -> None:
    if not path.exists():
        raise PipelineError(f"Expected output file was not created: {relative_to_root(path)}")
    if path.stat().st_size == 0:
        raise PipelineError(f"Expected output file is empty: {relative_to_root(path)}")


def validate_stage_outputs(stage: Stage) -> None:
    for output in stage.outputs:
        output_path = REPO_ROOT / output
        validate_non_empty(output_path)
        if output_path == EXTRACTION_FILE:
            validate_json_file(output_path)


def validate_stage_context(stage: Stage, pdf_path: Path) -> None:
    required_files = [AGENT_FILE, REPO_ROOT / stage.prompt_file, pdf_path]
    required_files.extend(REPO_ROOT / context_file for context_file in stage.context_files)
    for required_file in required_files:
        if not required_file.exists():
            raise PipelineError(f"Missing required stage input: {required_file}")


def print_stage_header(stage: Stage, total_stages: int, run_dir: Path) -> None:
    print()
    print(f"[stage {stage.number}/{total_stages}] {stage.key}")
    print(f"run dir: {relative_to_root(run_dir)}")
    print(f"prompt: {stage.prompt_file}")
    print(f"outputs: {', '.join(stage.outputs)}")


def run_stage(
    stage: Stage,
    total_stages: int,
    args: argparse.Namespace,
    pdf_path: Path,
    run_dir: Path,
) -> int | None:
    print_stage_header(stage, total_stages, run_dir)
    validate_stage_context(stage, pdf_path)
    prompt_text = build_stage_prompt(stage, total_stages, pdf_path)

    prompt_path = run_dir / f"{stage.number:02d}_{stage.key}.prompt.txt"
    last_message_path = run_dir / f"{stage.number:02d}_{stage.key}.last_message.txt"
    log_suffix = "log"
    log_path = run_dir / f"{stage.number:02d}_{stage.key}.stdout.{log_suffix}"

    prompt_path.write_text(prompt_text, encoding="utf-8")

    if args.dry_run:
        last_message_path.write_text("dry-run: codex exec was not invoked.\n", encoding="utf-8")
        log_path.write_text("dry-run: no codex output.\n", encoding="utf-8")
        return None

    command = build_codex_command(args, last_message_path)
    return_code = stream_process(command, prompt_text, log_path)
    if return_code != 0:
        raise PipelineError(
            f"codex exec failed at stage `{stage.key}` with exit code {return_code}. "
            f"See {relative_to_root(log_path)}"
        )

    validate_stage_outputs(stage)
    return extract_tokens_used(log_path)


def main() -> int:
    args = parse_args()
    ensure_repo_layout()

    if shutil.which(args.codex_bin) is None:
        raise PipelineError(f"Codex executable not found on PATH: {args.codex_bin}")
    if args.full_auto and args.sandbox != "workspace-write":
        raise PipelineError("--full-auto requires --sandbox workspace-write.")

    pdf_path = resolve_path(args.pdf)
    if not pdf_path.exists():
        raise PipelineError(f"Input PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise PipelineError(f"Input file must be a PDF: {pdf_path}")
    if not pdf_path.is_relative_to(REPO_ROOT):
        raise PipelineError(
            "Input PDF must be inside the repository so codex exec can access it under the repo root."
        )

    workflow_stages = WORKFLOWS[args.workflow]
    from_stage = args.from_stage or workflow_stages[0].key
    to_stage = args.to_stage or workflow_stages[-1].key

    selected_stages = stage_slice(workflow_stages, from_stage, to_stage)
    validate_entry_stage(workflow_stages, from_stage)
    cleared_entries = reset_intermediate_dir()
    needs_extraction = any(
        (REPO_ROOT / output).resolve() == EXTRACTION_FILE for stage in selected_stages for output in stage.outputs
    )
    if needs_extraction or args.force_init_extraction:
        ensure_extraction_file(args.force_init_extraction)

    run_dir = LOGS_DIR / f"run-{time.strftime('%Y%m%d-%H%M%S')}"
    run_dir.mkdir(parents=True, exist_ok=False)
    write_run_manifest(run_dir, args, pdf_path, selected_stages, cleared_entries)

    print(f"repo root: {REPO_ROOT}")
    print(f"input pdf: {relative_to_root(pdf_path) if pdf_path.is_relative_to(REPO_ROOT) else pdf_path}")
    print(f"workflow: {args.workflow}")
    print(f"intermediate reset: cleared {cleared_entries} entr{'y' if cleared_entries == 1 else 'ies'}")
    print(f"run logs: {relative_to_root(run_dir)}")
    print(f"stages: {', '.join(stage.key for stage in selected_stages)}")

    stage_tokens: list[tuple[Stage, int | None]] = []
    for stage in selected_stages:
        tokens_used = run_stage(stage, len(workflow_stages), args, pdf_path, run_dir)
        stage_tokens.append((stage, tokens_used))

    summary_path = write_token_summary(run_dir, stage_tokens)
    print_token_summary(stage_tokens, summary_path)

    print()
    print("pipeline completed successfully")
    print(f"final run logs: {relative_to_root(run_dir)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PipelineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
