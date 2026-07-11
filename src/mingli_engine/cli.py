import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from mingli_engine import classical_sources
from mingli_engine.chart_calculator import ChartCalculationError, calculate_bazi_chart
from mingli_engine.evidence_curation import build_knowledge_activation_summary
from mingli_engine.high_risk import classify_high_risk_request
from mingli_engine.html import render_html_report
from mingli_engine.markdown import render_markdown_report
from mingli_engine.models import (
    BaziChart,
    BirthProfile,
    SafetyReviewResult,
)
from mingli_engine.report_inputs import (
    InputContractError,
    birth_profile_from_dict,
    chart_from_dict,
    require_fields,
)
from mingli_engine.report_schema import KnowledgeActivationError, build_report
from mingli_engine.report_acceptance import build_report_acceptance_summary
from mingli_engine.report_release import (
    ReportReleaseError,
    build_report_release_summary,
)
from mingli_engine.safety import safety_check
from mingli_engine.validation import validate_birth_profile
from mingli_engine import promotion
from mingli_engine.models import PromotionPlan, PromotionResult


def _read_json(path: Path) -> dict[str, Any]:
    if str(path) == "-":
        payload = json.load(sys.stdin)
    else:
        with path.open("r", encoding="utf-8") as file:
            payload = json.load(file)

    if not isinstance(payload, dict):
        raise InputContractError("top-level JSON value must be an object")
    return payload


def _write_json(payload: Any) -> None:
    json.dump(_to_json_payload(payload), sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


def _to_json_payload(payload: Any) -> Any:
    data = asdict(payload)
    if isinstance(payload, BaziChart):
        for pillar in data["pillars"]:
            pillar["gan_zhi"] = pillar["heavenly_stem"] + pillar["earthly_branch"]
    return data


def _configure_stream_encoding(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def _validate_intake(args: argparse.Namespace) -> int:
    profile = birth_profile_from_dict(_read_json(args.input))
    _write_json(validate_birth_profile(profile))
    return 0


def _safety_check(args: argparse.Namespace) -> int:
    payload = _read_json(args.input)
    require_fields(payload, ("text",))
    if not isinstance(payload["text"], str):
        raise TypeError("text must be a string")
    _write_json(safety_check(payload["text"]))
    return 0


def _safety_review_focus_topic(
    profile: BirthProfile,
    *,
    disclaimer_present: bool,
) -> SafetyReviewResult:
    review = safety_check(
        profile.focus_topic,
        disclaimer_present=disclaimer_present,
    )
    high_risk_review = classify_high_risk_request(profile.focus_topic)
    if review.allowed and not high_risk_review.allowed:
        return SafetyReviewResult(
            allowed=False,
            red_line_categories=high_risk_review.categories,
            prohibited_phrases=[],
            disclaimer_present=disclaimer_present,
            redirect_message=high_risk_review.redirect_message,
        )
    return review


def _calculate_chart(args: argparse.Namespace) -> int:
    profile = birth_profile_from_dict(_read_json(args.input))
    safety_review = _safety_review_focus_topic(profile, disclaimer_present=False)
    if not safety_review.allowed:
        _write_json(safety_review)
        return 3

    _write_json(calculate_bazi_chart(profile))
    return 0


def _render_report(report: Any, report_format: str) -> str:
    if report_format == "html":
        return render_html_report(report)
    return render_markdown_report(report)


def _calculate_report(args: argparse.Namespace) -> int:
    profile = birth_profile_from_dict(_read_json(args.input))
    safety_review = _safety_review_focus_topic(profile, disclaimer_present=True)
    if not safety_review.allowed:
        _write_json(safety_review)
        return 3

    chart = calculate_bazi_chart(profile)
    report = build_report(chart)
    if not report.safety_review.allowed:
        _write_json(report.safety_review)
        return 3

    sys.stdout.write(_render_report(report, args.format))
    return 0


def _generate_report(args: argparse.Namespace) -> int:
    chart = chart_from_dict(_read_json(args.input))
    intake_review = validate_birth_profile(chart.birth_profile)
    if not intake_review.report_ready:
        _write_json(intake_review)
        return 2

    report = build_report(chart)
    if not report.safety_review.allowed:
        _write_json(report.safety_review)
        return 3

    sys.stdout.write(_render_report(report, args.format))
    return 0
def _promote(args: argparse.Namespace) -> int:
    overrides = _read_json(args.overrides)
    if not isinstance(overrides, dict):
        raise InputContractError("overrides must be a JSON object keyed by target evidence id")

    if args.apply:
        result = promotion.apply_promotion(
            intake_dir=args.intake_dir,
            corpus_dir=args.corpus_dir,
            promotion_batch_id=args.batch,
            evidence_overrides=overrides,
            curation_batch_id=args.curation_batch or "",
        )
        _write_json(result)
    else:
        plan = promotion.plan_promotion(
            intake_dir=args.intake_dir,
            corpus_dir=args.corpus_dir,
            promotion_batch_id=args.batch,
            evidence_overrides=overrides,
            curation_batch_id=args.curation_batch or "",
        )
        _write_json(plan)
    return 0


def _knowledge_activation_summary(args: argparse.Namespace) -> int:
    sources = classical_sources.load_classical_sources(args.corpus_dir)
    evidence_units = classical_sources.load_approved_evidence_units(args.corpus_dir)
    conflicts = classical_sources.load_source_conflicts(args.corpus_dir)
    _write_json(build_knowledge_activation_summary(sources, evidence_units, conflicts))
    return 0


def _report_acceptance_summary(args: argparse.Namespace) -> int:
    _write_json(build_report_acceptance_summary())
    return 0


def _report_release_summary(args: argparse.Namespace) -> int:
    summary = build_report_release_summary()
    _write_json(summary)
    return 4 if summary.release_status == "blocked" else 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mingli-engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate-intake")
    validate_parser.add_argument("--input", required=True, type=Path)
    validate_parser.set_defaults(handler=_validate_intake)

    safety_parser = subparsers.add_parser("safety-check")
    safety_parser.add_argument("--input", required=True, type=Path)
    safety_parser.set_defaults(handler=_safety_check)

    calculate_parser = subparsers.add_parser("calculate-chart")
    calculate_parser.add_argument("--input", required=True, type=Path)
    calculate_parser.set_defaults(handler=_calculate_chart)

    calculated_report_parser = subparsers.add_parser("calculate-report")
    calculated_report_parser.add_argument("--input", required=True, type=Path)
    calculated_report_parser.add_argument(
        "--format",
        choices=["markdown", "html"],
        required=True,
    )
    calculated_report_parser.set_defaults(handler=_calculate_report)

    report_parser = subparsers.add_parser("generate-report")
    report_parser.add_argument("--input", required=True, type=Path)
    report_parser.add_argument("--format", choices=["markdown", "html"], required=True)
    report_parser.set_defaults(handler=_generate_report)
    promote_parser = subparsers.add_parser("promote")
    promote_parser.add_argument("--batch", required=True)
    promote_parser.add_argument("--overrides", required=True, type=Path)
    promote_parser.add_argument("--curation-batch", default="")
    promote_parser.add_argument("--intake-dir", default=None)
    promote_parser.add_argument("--corpus-dir", default=None)
    promote_parser.add_argument("--apply", action="store_true")
    promote_parser.set_defaults(handler=_promote)

    activation_parser = subparsers.add_parser("knowledge-activation-summary")
    activation_parser.add_argument("--corpus-dir", default=None)
    activation_parser.set_defaults(handler=_knowledge_activation_summary)

    acceptance_parser = subparsers.add_parser("report-acceptance-summary")
    acceptance_parser.set_defaults(handler=_report_acceptance_summary)

    release_parser = subparsers.add_parser("report-release-summary")
    release_parser.set_defaults(handler=_report_release_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stream_encoding(sys.stdin)
    _configure_stream_encoding(sys.stdout)
    _configure_stream_encoding(sys.stderr)
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except json.JSONDecodeError as error:
        print(f"Invalid JSON: {error}", file=sys.stderr)
        return 1
    except InputContractError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except ChartCalculationError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except promotion.PromotionError as error:
        print(f"Promotion error: {error}", file=sys.stderr)
        return 1
    except classical_sources.ClassicalEvidenceError as error:
        print(f"Classical evidence error: {error}", file=sys.stderr)
        return 1
    except KnowledgeActivationError as error:
        print(f"Knowledge activation error: {error}", file=sys.stderr)
        return 1
    except ReportReleaseError as error:
        print(f"Report release error: {error}", file=sys.stderr)
        return 1
    except (KeyError, TypeError, AttributeError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
