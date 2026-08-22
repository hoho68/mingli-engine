import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import fields, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mingli_engine import classical_sources
from mingli_engine.bazi import analyze_bazi_chart
from mingli_engine.bazi.result_models import (
    BranchRelationResult,
    CalculationBundle,
    ReasonedResult,
    StrengthContribution,
)
from mingli_engine.application_serialization import (
    response_status_from_json_bytes,
    serialize_branch_relation,
    serialize_calculation_bundle,
    serialize_reasoned_result,
    serialize_strength_contribution,
)
from mingli_engine.application_inputs import MAX_REQUEST_BYTES
from mingli_engine.application_service import handle_real_use_json
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
from mingli_engine.liuyao.analysis import analyze_liuyao_chart
from mingli_engine.liuyao.calendar_bridge import CalendarBridgeError
from mingli_engine.liuyao.casting import CastingError, assemble_liuyao_chart
from mingli_engine.liuyao.najia import NajiaError
from mingli_engine.liuyao.report import LiuyaoReportError, build_liuyao_report
from mingli_engine.liuyao.report_markdown import render_liuyao_markdown
from mingli_engine.liuyao.result_models import LiuyaoCastRequest, LiuyaoLineInput
from mingli_engine.new_material_learning import (
    DEFAULT_BATCH_ID as NEW_MATERIAL_BATCH_ID,
    ManifestError as NewMaterialLearningError,
    build_new_material_learning_summary,
    render_new_material_learning_markdown,
    validate_new_material_learning,
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
from mingli_engine.project_completion import (
    ProjectCompletionError,
    build_project_completion_summary,
)
from mingli_engine.safety import safety_check
from mingli_engine.validation import validate_birth_profile
from mingli_engine import promotion


class AnalysisExecutionError(RuntimeError):
    pass


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
    if isinstance(payload, Mapping):
        return {key: _to_json_payload(value) for key, value in payload.items()}
    if isinstance(payload, Sequence) and not isinstance(
        payload, (str, bytes, bytearray)
    ):
        return [_to_json_payload(value) for value in payload]
    if not is_dataclass(payload) or isinstance(payload, type):
        return payload

    data = {
        model_field.name: _to_json_payload(getattr(payload, model_field.name))
        for model_field in fields(payload)
    }
    if isinstance(payload, BaziChart):
        for pillar in data["pillars"]:
            pillar["gan_zhi"] = pillar["heavenly_stem"] + pillar["earthly_branch"]
    return data


def _birth_datetime(profile: BirthProfile) -> datetime:
    return datetime.strptime(
        f"{profile.birth_date} {profile.birth_time}",
        "%Y-%m-%d %H:%M",
    )


def _public_reasoning(reasoning: ReasonedResult) -> dict[str, object]:
    return serialize_reasoned_result(reasoning)


def _public_relation(relation: BranchRelationResult) -> dict[str, object]:
    return serialize_branch_relation(relation)


def _public_strength_contribution(
    contribution: StrengthContribution,
) -> dict[str, object]:
    return serialize_strength_contribution(contribution)


def _public_calculation_payload(
    calculation: CalculationBundle,
) -> dict[str, object]:
    return serialize_calculation_bundle(calculation)


def _configure_stream_encoding(stream: Any) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        reconfigure(encoding="utf-8")


def _read_real_use_input(path: Path) -> bytes:
    if str(path) == "-":
        return sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
    with path.open("rb") as stream:
        return stream.read(MAX_REQUEST_BYTES + 1)


def _write_real_use_response(payload: bytes) -> None:
    output = getattr(sys.stdout, "buffer", None)
    if output is None:
        sys.stdout.write(payload.decode("utf-8"))
    else:
        output.write(payload)


def _real_use(args: argparse.Namespace) -> int:
    try:
        request_payload = _read_real_use_input(args.input)
    except OSError:
        request_payload = b""
    response_payload = handle_real_use_json(request_payload)
    _write_real_use_response(response_payload)
    status = response_status_from_json_bytes(response_payload)
    return {"ok": 0, "refused": 3, "error": 1}[status]


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

    chart = calculate_bazi_chart(profile)
    if args.analysis:
        try:
            calculation = analyze_bazi_chart(
                chart,
                birth_datetime=_birth_datetime(profile),
            )
            output = _to_json_payload(chart)
            output["calculation"] = _public_calculation_payload(calculation)
        except (ValueError, RuntimeError):
            raise AnalysisExecutionError from None
        _write_json(output)
    else:
        _write_json(chart)
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
    if args.analysis:
        try:
            calculation = analyze_bazi_chart(
                chart,
                birth_datetime=_birth_datetime(profile),
            )
            report = build_report(chart, calculation)
        except (ValueError, RuntimeError):
            raise AnalysisExecutionError from None
    else:
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


def _project_completion_summary(args: argparse.Namespace) -> int:
    summary = build_project_completion_summary()
    _write_json(summary)
    return 4 if summary.completion_status == "blocked" else 0


def _validate_new_material_learning(args: argparse.Namespace) -> int:
    if args.batch != NEW_MATERIAL_BATCH_ID:
        raise NewMaterialLearningError("the requested learning batch is unsupported")
    _write_json(validate_new_material_learning())
    return 0


def _new_material_learning_summary(args: argparse.Namespace) -> int:
    if args.batch != NEW_MATERIAL_BATCH_ID:
        raise NewMaterialLearningError("the requested learning batch is unsupported")
    summary = build_new_material_learning_summary()
    sys.stdout.write(render_new_material_learning_markdown(summary))
    return 0


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
    calculate_parser.add_argument("--analysis", action="store_true")
    calculate_parser.set_defaults(handler=_calculate_chart)

    calculated_report_parser = subparsers.add_parser("calculate-report")
    calculated_report_parser.add_argument("--input", required=True, type=Path)
    calculated_report_parser.add_argument(
        "--format",
        choices=["markdown", "html"],
        required=True,
    )
    calculated_report_parser.add_argument("--analysis", action="store_true")
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

    completion_parser = subparsers.add_parser("project-completion-summary")
    completion_parser.set_defaults(handler=_project_completion_summary)

    real_use_parser = subparsers.add_parser("real-use")
    real_use_parser.add_argument("--input", required=True, type=Path)
    real_use_parser.set_defaults(handler=_real_use)

    liuyao_calculate_parser = subparsers.add_parser("liuyao-calculate")
    liuyao_calculate_parser.add_argument("--input", required=True, type=Path)
    liuyao_calculate_parser.set_defaults(handler=_liuyao_calculate)

    liuyao_report_parser = subparsers.add_parser("liuyao-report")
    liuyao_report_parser.add_argument("--input", required=True, type=Path)
    liuyao_report_parser.set_defaults(handler=_liuyao_report)

    liuyao_promote_parser = subparsers.add_parser("liuyao-promote-batch")
    liuyao_promote_parser.add_argument("--batch", required=True)
    liuyao_promote_parser.add_argument("--confirm-promotion", action="store_true")
    liuyao_promote_parser.set_defaults(handler=_liuyao_promote_batch)

    new_material_validation_parser = subparsers.add_parser(
        "validate-new-material-learning"
    )
    new_material_validation_parser.add_argument("--batch", required=True)
    new_material_validation_parser.set_defaults(
        handler=_validate_new_material_learning
    )

    new_material_summary_parser = subparsers.add_parser(
        "new-material-learning-summary"
    )
    new_material_summary_parser.add_argument("--batch", required=True)
    new_material_summary_parser.set_defaults(handler=_new_material_learning_summary)

    return parser


def _liuyao_error(message: str) -> int:
    print(f"Liuyao error: {message}", file=sys.stderr)
    return 1


def _read_bounded_liuyao_json(path: Path) -> dict[str, Any]:
    try:
        if str(path) == "-":
            raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        else:
            raw = path.read_bytes()
    except OSError:
        raise InputContractError("invalid request envelope") from None
    if len(raw) > MAX_REQUEST_BYTES:
        raise InputContractError("invalid request envelope")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise InputContractError("invalid request envelope") from None
    if not isinstance(payload, dict):
        raise InputContractError("invalid request envelope")
    return payload


def _liuyao_cast_request_from_dict(payload: dict[str, Any]) -> LiuyaoCastRequest:
    allowed = {"cast_mode", "cast_datetime", "lines", "numbers", "request_id"}
    if any(key not in allowed for key in payload):
        raise InputContractError("invalid request fields")
    if "cast_mode" not in payload or "cast_datetime" not in payload:
        raise InputContractError("invalid request fields")
    lines_raw = payload.get("lines")
    numbers_raw = payload.get("numbers")
    request_id = payload.get("request_id")
    if request_id is not None and not isinstance(request_id, str):
        raise InputContractError("invalid request fields")
    lines: tuple[LiuyaoLineInput, ...] = ()
    if lines_raw is not None:
        if not isinstance(lines_raw, list):
            raise InputContractError("invalid request fields")
        parsed_lines: list[LiuyaoLineInput] = []
        for item in lines_raw:
            if not isinstance(item, dict) or set(item) != {
                "position",
                "yin_yang",
                "moving",
            }:
                raise InputContractError("invalid request fields")
            try:
                parsed_lines.append(
                    LiuyaoLineInput(
                        position=item["position"],
                        yin_yang=item["yin_yang"],
                        moving=item["moving"],
                    )
                )
            except (TypeError, ValueError):
                raise InputContractError("invalid request fields") from None
        lines = tuple(parsed_lines)
    numbers: tuple[int, ...] = ()
    if numbers_raw is not None:
        if not isinstance(numbers_raw, list) or any(
            not isinstance(value, int) or isinstance(value, bool)
            for value in numbers_raw
        ):
            raise InputContractError("invalid request fields")
        numbers = tuple(numbers_raw)
    try:
        return LiuyaoCastRequest(
            cast_mode=payload["cast_mode"],
            cast_datetime=payload["cast_datetime"],
            lines=lines,
            numbers=numbers,
            request_id=request_id,
        )
    except (TypeError, ValueError) as error:
        message = str(error)
        if "cast_datetime must use" in message:
            raise InputContractError("invalid request fields") from None
        raise InputContractError(
            "cast mode requirements are not met"
        ) from None


def _liuyao_chart_from_args(args: argparse.Namespace) -> Any:
    payload = _read_bounded_liuyao_json(args.input)
    request = _liuyao_cast_request_from_dict(payload)
    return assemble_liuyao_chart(request)


def _liuyao_calculate(args: argparse.Namespace) -> int:
    try:
        chart = _liuyao_chart_from_args(args)
    except InputContractError as error:
        return _liuyao_error(str(error))
    except CalendarBridgeError as error:
        return _liuyao_error(str(error))
    except (CastingError, NajiaError) as error:
        return _liuyao_error(f"cast mode requirements are not met ({error})")
    _write_json(chart)
    return 0


def _liuyao_report(args: argparse.Namespace) -> int:
    try:
        chart = _liuyao_chart_from_args(args)
        report = build_liuyao_report(analyze_liuyao_chart(chart))
    except InputContractError as error:
        return _liuyao_error(str(error))
    except CalendarBridgeError as error:
        return _liuyao_error(str(error))
    except (CastingError, NajiaError) as error:
        return _liuyao_error(f"cast mode requirements are not met ({error})")
    except LiuyaoReportError:
        return _liuyao_error(
            "request cannot be answered within the safety boundary"
        )
    markdown = render_liuyao_markdown(report)
    sys.stdout.write(markdown)
    if not markdown.endswith("\n"):
        sys.stdout.write("\n")
    return 0


def _liuyao_promote_batch(args: argparse.Namespace) -> int:
    if args.batch != "batch_20260714":
        return _liuyao_error("the requested learning batch is unsupported")
    if not args.confirm_promotion:
        return _liuyao_error("batch promotion requires explicit confirmation")
    from mingli_engine.liuyao.knowledge import (
        LiuyaoKnowledgeError,
        promote_liuyao_batch_candidates,
    )

    batch_root = (
        Path(__file__).resolve().parent / "data" / "new_material_learning"
    )
    try:
        summary = promote_liuyao_batch_candidates(
            batch_root,
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
    except LiuyaoKnowledgeError as error:
        return _liuyao_error(str(error))
    _write_json(summary)
    return 0


def main(argv: list[str] | None = None) -> int:
    _configure_stream_encoding(sys.stdin)
    _configure_stream_encoding(sys.stdout)
    _configure_stream_encoding(sys.stderr)
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except AnalysisExecutionError:
        print("Analysis error: analysis could not be completed", file=sys.stderr)
        return 1
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
    except ProjectCompletionError as error:
        print(f"Project completion error: {error}", file=sys.stderr)
        return 1
    except NewMaterialLearningError as error:
        print(f"New material learning error: {error}", file=sys.stderr)
        return 1
    except (KeyError, TypeError, AttributeError) as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Input error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
