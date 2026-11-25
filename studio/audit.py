from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AuditEntry:
    timestamp: str
    operation: str
    parameters: dict[str, Any] = field(default_factory=dict)
    rows_before: int = 0
    rows_after: int = 0
    affected: int = 0
    note: str = ""

    def as_line(self) -> str:
        params = ", ".join(f"{key}={value}" for key, value in self.parameters.items())
        suffix = f" | {params}" if params else ""
        extra = f" | {self.note}" if self.note else ""
        return (
            f"[{self.timestamp}] {self.operation}: "
            f"dotknięto {self.affected} rekordów "
            f"(wiersze {self.rows_before} → {self.rows_after}){suffix}{extra}"
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def now_stamp() -> str:
    return datetime.now().isoformat(timespec="seconds")
