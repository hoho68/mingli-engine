# Real-Use V1 Contract

## Public Python Surface

```python
def handle_real_use(request: RealUseRequestV1) -> RealUseResponseV1:
    """Execute one validated request in one process and return a typed envelope."""

def handle_real_use_json(payload: bytes) -> bytes:
    """Parse, execute, serialize, and size-check one strict JSON request."""

def response_status_from_json_bytes(payload: bytes) -> ResponseStatus:
    """Read only the status from an internally generated response envelope."""
```

The root package exports these operations and every V1 request and response DTO. Existing low-level engine functions remain available.

## Request Envelope

```json
{
  "schema_version": "real-use-request-v1",
  "request_id": "synthetic-analysis-001",
  "operation": "analysis",
  "profile": {
    "calendar_type": "gregorian",
    "birth_date": "1996-12-15",
    "birth_time": "09:30",
    "birthplace": "Synthetic UTC+08 Place",
    "gender": "unknown",
    "focus_topic": "traditional structural overview"
  },
  "authorization": {
    "subject_relation": "self",
    "attested": true
  },
  "options": {
    "report_format": null,
    "include_profile_in_report": false
  }
}
```

Exact request fields:

```text
RealUseProfileV1: calendar_type, birth_date, birth_time, birthplace, gender, focus_topic
AuthorizationAttestationV1: subject_relation, attested
RealUseOptionsV1: report_format, include_profile_in_report
RealUseRequestV1: schema_version, request_id, operation, profile, authorization, options
```

Request rules:

- Root and nested objects require every listed field exactly once and reject unknown or missing fields.
- `schema_version` is exactly `real-use-request-v1`.
- `operation` is `analysis` or `report`.
- The `request_id` field is required; its value is null or 1 to 64 ASCII letters, digits, `_`, or `-`.
- `calendar_type` is exactly `gregorian`.
- Supported dates are 1901-01-01 through 2099-12-31 under the documented UTC+08 wall-time assumption.
- Aware datetimes, longitude, timezone lookup, true solar time, external charts, and precomputed calculation bundles are unsupported.
- `subject_relation` is `self` or `authorized_other`; any other value is `invalid_request`.
- `attested=false` is schema-valid and produces `authorization_required` before calculation.
- Analysis requires `report_format=null`.
- Report requires `report_format` of `json`, `markdown`, or `html`.
- The `include_profile_in_report` field is required and must be boolean; omission and defaulting are invalid.

## Strict Input Boundary

- Maximum request size is 32 KiB.
- Maximum JSON nesting depth is 8.
- File and stdin readers request at most 32 KiB plus one sentinel byte and stop on overflow.
- Invalid UTF-8, duplicate keys, and non-finite numbers are rejected.
- `focus_topic` is at most 500 Unicode code points.
- `birthplace` is at most 160 Unicode code points.
- Other free text is at most 500 Unicode code points.
- Validation and safety copies are normalized with NFKC.
- Accepted original values remain only in the typed request for controlled processing.
- Errors never include raw or normalized invalid values.

## Mandatory Processing Order

1. Create a random UUID4 trace ID.
2. Enforce byte, JSON, depth, schema, literal, and field limits.
3. Require true attestation and an allowed subject relationship.
4. Run focus-topic and high-risk safety checks.
5. Refuse without invoking calculation when authorization or safety fails.
6. Calculate chart and analysis in the same process and request.
7. Build a report from the original bound bundle when requested.
8. Enforce post-build safety before redaction or rendering.
9. Redact the complete report object when profile inclusion is disabled.
10. Escape included untrusted values at Markdown and HTML insertion boundaries.
11. Serialize an explicit response mapping and enforce the output-size limit.

Lexical third-party detection is defense in depth and never substitutes for structural authorization.

## Response Envelope

```json
{
  "schema_version": "real-use-response-v1",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation": "analysis",
  "status": "ok",
  "result": {
    "chart": {},
    "calculation": {}
  },
  "safety": {
    "allowed": true,
    "decision": "allowed",
    "categories": [],
    "redirect_message": "",
    "requires_narrowing": false
  },
  "provenance": {
    "engine_version": "0.2.0",
    "ruleset_version": "bazi-rules-v1",
    "provider_version": "lunar-python-1.4.8",
    "chart_source_type": "calculated",
    "chart_source_confidence": "deterministic_supported_range",
    "evidence_baseline_id": "tracked-evidence-baseline",
    "evidence_ids": []
  },
  "warnings": [],
  "privacy": {
    "retention": "not_stored_by_engine",
    "contains_sensitive_profile": false
  },
  "error": null
}
```

Exact response fields:

```text
ApplicationErrorV1: code, message, field_path, retryable, trace_id
ApplicationSafetyV1: allowed, decision, categories, redirect_message, requires_narrowing
ApplicationProvenanceV1: engine_version, ruleset_version, provider_version, chart_source_type, chart_source_confidence, evidence_baseline_id, evidence_ids
ApplicationWarningV1: code, message
ApplicationPrivacyV1: retention, contains_sensitive_profile
ApplicationContentV1: media_type, content, contains_sensitive_profile
ApplicationAnalysisResultV1: chart, calculation
ApplicationReportResultV1: report, content
RealUseResponseV1: schema_version, trace_id, operation, status, result, safety, provenance, warnings, privacy, error
```

Response invariants:

- `schema_version` is exactly `real-use-response-v1`.
- `status` is `ok`, `refused`, or `error`.
- Strict parsing failures use `operation=null`; every typed or successfully parsed request carries its operation.
- An `ok` analysis has exactly `ApplicationAnalysisResultV1`.
- An `ok` report has exactly `ApplicationReportResultV1`.
- Refused and error responses have null result.
- Provenance is present only when trustworthy calculation data exists.
- Error trace ID equals root trace ID.
- Sequences are tuples in typed DTOs.
- Serialized JSON is deterministic UTF-8 with sorted keys and no NaN.
- Maximum response size is 1 MiB. Oversized normal output becomes a small `response_too_large` envelope.

## Required Non-OK Response Matrix

| Outcome | status | operation | result | safety | provenance | privacy | error |
|---|---|---|---|---|---|---|---|
| Parse error (`payload_too_large`, `invalid_json`, `invalid_request`, or parse-time `unsupported_input`) | `error` | null | null | `allowed=false`, `decision=not_evaluated`, `categories=()`, `redirect_message=""`, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null matching code; trace ID equals root trace ID |
| Authorization refusal | `refused` | parsed `analysis` or `report` | null | `allowed=false`, `decision=authorization_required`, `categories=("authorization",)`, `redirect_message="Provide a true self-use or authorized-other attestation."`, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `authorization_required`; trace ID equals root trace ID |
| Unsafe refusal | `refused` | parsed `analysis` or `report` | null | `allowed=false`, `decision=unsafe_request`, non-empty normalized categories, non-empty safe redirect, `requires_narrowing=true` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `unsafe_request`; trace ID equals root trace ID |
| Internal error after successful parse | `error` | parsed `analysis` or `report` | null | `allowed=false`, `decision=error`, `categories=()`, `redirect_message=""`, `requires_narrowing=false` | null | `retention=not_stored_by_engine`, `contains_sensitive_profile=false` | non-null `internal_error`; trace ID equals root trace ID |

All four outcomes use a non-null `ApplicationSafetyV1` and `ApplicationPrivacyV1`; only `operation`, `result`, and `provenance` have the nullability shown above. Tests assert every field value, not only status and error code.

## Stable Error Contract

Allowed codes:

```text
invalid_json
invalid_request
authorization_required
unsafe_request
unsupported_input
payload_too_large
response_too_large
calculation_failed
knowledge_unavailable
internal_error
```

An error contains only `code`, `message`, `field_path`, `retryable`, and `trace_id`. It never contains request values, exception text, file paths, report bodies, or Python representations.

## Analysis Serialization

Analysis output includes chart source and pillars without the raw birth profile, complete public calculation result fields, filtered assumptions, computation states, confidence, signals, rule IDs, evidence IDs, and school views. Serializers construct explicit mappings and never apply generic `asdict()` to public response objects.

## Report Serialization And Privacy

Report JSON includes stable report fields, evidence audit, formal traces, safety result, and knowledge activation summary. Markdown and HTML use `ApplicationContentV1` with media type and sensitivity flag.

Every successful JSON, Markdown, and HTML report preserves source locators, source IDs, evidence IDs, and rule IDs for major conclusions; contains the required traditional-analysis disclaimer and qualified-professional boundary; uses conditional, uncertainty, and school-dependent language; and rejects prohibited absolute terms such as `必定`, `注定`, `一定会`, and `死定` before output.

When `include_profile_in_report=false`, all raw and NFKC-normalized occurrences of `calendar_type`, `birth_date`, `birth_time`, `birthplace`, `gender`, and `focus_topic` are removed from every explicit report field, nested value, metadata value, and rendered output before any renderer runs.

When inclusion is true, content is marked `contains_sensitive_profile=true`. Markdown and HTML escape ATX and Setext headings, raw HTML, links, images, tables, blockquotes, emphasis, code spans, and fences originating from profile values. Ordinary non-active legacy values remain byte compatible.

The privacy statement is: birth-profile and report data are not stored by the engine. Callers, terminals, shell redirection, and host operating systems may retain output.

The engine creates no request or response logs, stable profile hashes, application-managed files, database rows, caches, or sessions. Test-only diagnostics may contain only operation, status, duration bucket, payload-size bucket, safety categories, and version identifiers.

## Same-Process Provenance

The application constructs the profile, calculates the chart, analyzes the chart, and builds any report in one request scope. Bound calculation trust rejects cross-request reuse, shallow or deep copies, and serialized reconstruction. Weak process-local registry entries are released after object garbage collection. Application responses are never accepted as trusted calculation inputs.

## CLI Contract

```text
mingli-engine real-use --input REQUEST_PATH_OR_STDIN
```

- `-` selects stdin.
- Exactly one strict request is accepted.
- Exactly one response envelope is written to stdout.
- Controlled outcomes write nothing to stderr.
- Exit code 0 means `ok`.
- Exit code 3 means `refused`.
- Exit code 1 means invalid request or controlled application error.

## Compatibility And Exclusions

Existing low-level APIs and CLI commands retain their interfaces except documented escaping of active untrusted markup. This contract provides no HTTP server, browser or desktop UI, account, database, session persistence, remote service, external chart input, geographic timezone lookup, longitude handling, or true-solar-time calculation.
