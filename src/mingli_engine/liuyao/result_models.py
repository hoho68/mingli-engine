"""Immutable liuyao request, chart, and analysis models (V1)."""

from __future__ import annotations

from dataclasses import dataclass
import re

CAST_MODES: tuple[str, ...] = ("explicit", "time", "number")
_DATETIME_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


def _require_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


@dataclass(frozen=True)
class LiuyaoLineInput:
    position: int
    yin_yang: str
    moving: bool

    def __post_init__(self) -> None:
        if not isinstance(self.position, int) or isinstance(self.position, bool):
            raise TypeError("line position must be an integer")
        if not 1 <= self.position <= 6:
            raise ValueError("line position must be between 1 and 6")
        if self.yin_yang not in {"yang", "yin"}:
            raise ValueError("line yin_yang must be 'yang' or 'yin'")
        if not isinstance(self.moving, bool):
            raise TypeError("line moving must be a boolean")


@dataclass(frozen=True)
class LiuyaoCastRequest:
    cast_mode: str
    cast_datetime: str
    lines: tuple[LiuyaoLineInput, ...] = ()
    numbers: tuple[int, ...] = ()
    request_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "lines", tuple(self.lines))
        object.__setattr__(self, "numbers", tuple(self.numbers))
        if self.cast_mode not in CAST_MODES:
            raise ValueError("cast_mode must be explicit, time, or number")
        _require_text(self.cast_datetime, "cast_datetime")
        if not _DATETIME_PATTERN.fullmatch(self.cast_datetime):
            raise ValueError("cast_datetime must use YYYY-MM-DDTHH:MM")
        if self.request_id is not None and (
            not isinstance(self.request_id, str) or len(self.request_id) > 128
        ):
            raise ValueError("request_id must be a short string or null")
        if self.cast_mode == "explicit":
            if len(self.lines) != 6:
                raise ValueError("explicit casting requires exactly six lines")
            positions = [line.position for line in self.lines]
            if sorted(positions) != [1, 2, 3, 4, 5, 6]:
                raise ValueError("explicit lines must cover positions 1-6 exactly once")
            if not all(isinstance(line, LiuyaoLineInput) for line in self.lines):
                raise TypeError("lines must contain LiuyaoLineInput values")
            if self.numbers:
                raise ValueError("explicit casting does not take numbers")
        elif self.cast_mode == "time":
            if self.lines or self.numbers:
                raise ValueError("time casting takes no lines or numbers")
        else:
            if self.lines:
                raise ValueError("number casting does not take lines")
            if len(self.numbers) != 2 or any(
                not isinstance(value, int) or isinstance(value, bool) or value <= 0
                for value in self.numbers
            ):
                raise ValueError("number casting requires exactly two positive integers")


@dataclass(frozen=True)
class TrigramInfo:
    name: str
    symbol_lines: tuple[int, int, int]
    element: str
    xiantian_index: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "symbol_lines", tuple(self.symbol_lines))
        _require_text(self.name, "trigram name")
        if len(self.symbol_lines) != 3 or set(self.symbol_lines) - {0, 1}:
            raise ValueError("trigram symbol lines are invalid")
        _require_text(self.element, "trigram element")
        if not 1 <= self.xiantian_index <= 8:
            raise ValueError("xiantian index must be between 1 and 8")


@dataclass(frozen=True)
class GuaInfo:
    gua_name: str
    upper_trigram: str
    lower_trigram: str
    palace: str
    palace_sequence: int
    shi_position: int
    ying_position: int

    def __post_init__(self) -> None:
        _require_text(self.gua_name, "gua name")
        _require_text(self.upper_trigram, "upper trigram")
        _require_text(self.lower_trigram, "lower trigram")
        _require_text(self.palace, "palace")
        if not 0 <= self.palace_sequence <= 7:
            raise ValueError("palace sequence must be between 0 and 7")
        if not 1 <= self.shi_position <= 6 or not 1 <= self.ying_position <= 6:
            raise ValueError("shi/ying positions must be between 1 and 6")


@dataclass(frozen=True)
class HiddenSpirit:
    ganzhi: str
    six_relation: str
    attached_position: int

    def __post_init__(self) -> None:
        _require_text(self.ganzhi, "hidden spirit ganzhi")
        _require_text(self.six_relation, "hidden spirit relation")
        if not 1 <= self.attached_position <= 6:
            raise ValueError("hidden spirit position must be between 1 and 6")


@dataclass(frozen=True)
class LiuyaoLine:
    position: int
    yin_yang: str
    moving: bool
    ganzhi: str
    element: str
    six_relation: str
    six_spirit: str
    shi_ying: str
    hidden_spirit: HiddenSpirit | None
    void: bool
    month_break: bool
    day_break: bool

    def __post_init__(self) -> None:
        if not 1 <= self.position <= 6:
            raise ValueError("line position must be between 1 and 6")
        if self.yin_yang not in {"yang", "yin"}:
            raise ValueError("line yin_yang must be 'yang' or 'yin'")
        for value, field_name in (
            (self.ganzhi, "line ganzhi"),
            (self.element, "line element"),
            (self.six_relation, "line six relation"),
            (self.six_spirit, "line six spirit"),
        ):
            _require_text(value, field_name)
        if self.shi_ying not in {"", "shi", "ying"}:
            raise ValueError("shi_ying must be '', 'shi', or 'ying'")
        if self.hidden_spirit is not None and not isinstance(
            self.hidden_spirit, HiddenSpirit
        ):
            raise TypeError("hidden_spirit must be a HiddenSpirit or None")


@dataclass(frozen=True)
class LiuyaoChart:
    cast_mode: str
    cast_datetime: str
    ben_gua: GuaInfo
    bian_gua: GuaInfo | None
    hu_gua: GuaInfo
    lines: tuple[LiuyaoLine, ...]
    month_command: str
    day_ganzhi: str
    xun_void_branches: tuple[str, ...]
    assumptions: tuple[str, ...]
    request_id: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "lines", tuple(self.lines))
        object.__setattr__(self, "xun_void_branches", tuple(self.xun_void_branches))
        object.__setattr__(self, "assumptions", tuple(self.assumptions))
        if self.cast_mode not in CAST_MODES:
            raise ValueError("chart cast_mode is invalid")
        if not _DATETIME_PATTERN.fullmatch(self.cast_datetime):
            raise ValueError("chart cast_datetime is invalid")
        if not isinstance(self.ben_gua, GuaInfo) or not isinstance(self.hu_gua, GuaInfo):
            raise TypeError("chart gua fields are invalid")
        if self.bian_gua is not None and not isinstance(self.bian_gua, GuaInfo):
            raise TypeError("chart bian_gua must be a GuaInfo or None")
        if len(self.lines) != 6 or not all(
            isinstance(line, LiuyaoLine) for line in self.lines
        ):
            raise ValueError("chart requires exactly six LiuyaoLine values")
        if [line.position for line in self.lines] != [1, 2, 3, 4, 5, 6]:
            raise ValueError("chart lines must be ordered by position 1-6")
        if self.bian_gua is None and any(line.moving for line in self.lines):
            raise ValueError("a chart with moving lines requires a bian_gua")
        if self.bian_gua is not None and not any(line.moving for line in self.lines):
            raise ValueError("a chart without moving lines must not carry a bian_gua")
        _require_text(self.month_command, "month command")
        _require_text(self.day_ganzhi, "day ganzhi")
        if len(self.xun_void_branches) != 2:
            raise ValueError("xun void branches must contain exactly two branches")
        if not self.assumptions:
            raise ValueError("chart assumptions must be documented")
