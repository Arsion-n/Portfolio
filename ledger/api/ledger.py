from __future__ import annotations

import os
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

HK = ZoneInfo("Asia/Hong_Kong")
HKD_QUANT = Decimal("0.01")
RESERVED = {
    "date",
    "payee",
    "narration",
    "amount",
    "expense_account",
    "asset_account",
    "flag",
}
ACCOUNT_RE = re.compile(r"^[A-Z][A-Za-z0-9-]*(:[A-Z][A-Za-z0-9-]*)+$")
OPEN_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\s+open\s+(\S+)")
INCLUDE_RE = re.compile(r'^include\s+"([^"]+)"\s*$')
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class TxnError(ValueError):
    pass


def hk_today_aware() -> str:
    return datetime.now(HK).date().isoformat()


def parse_amount(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TxnError("amount 必須係數字") from exc
    if amount <= 0:
        raise TxnError("amount 必須大於 0")
    return amount.quantize(HKD_QUANT, rounding=ROUND_HALF_UP)


def quote_beancount(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_amount(amount: Decimal) -> str:
    return f"{amount:.2f}"


def validate_account(name: str) -> str:
    name = name.strip()
    if not ACCOUNT_RE.match(name):
        raise TxnError(f"帳戶名無效: {name}")
    return name


def parse_open_accounts(accounts_text: str) -> list[str]:
    found: list[str] = []
    for line in accounts_text.splitlines():
        match = OPEN_RE.match(line.strip())
        if match:
            found.append(match.group(1))
    return found


def group_accounts(accounts: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {
        "assets": [],
        "liabilities": [],
        "expenses": [],
        "income": [],
        "equity": [],
        "other": [],
    }
    for name in accounts:
        root = name.split(":", 1)[0].lower()
        if root in groups:
            groups[root].append(name)
        else:
            groups["other"].append(name)
    return groups


def extract_meta(payload: dict, schema: dict) -> dict[str, str]:
    by_key = schema["by_key"]
    unknown = [k for k in payload if k not in RESERVED and k not in by_key]
    if unknown:
        raise TxnError(
            f"未定義嘅自訂欄位: {', '.join(sorted(unknown))}（改 schema/columns.yaml）"
        )

    meta: dict[str, str] = {}
    for col in schema["columns"]:
        key = col["key"]
        raw = payload.get(key, None)
        if raw is None or raw == "":
            if col.get("required"):
                raise TxnError(f"缺少必填欄位: {key}")
            default = col.get("default")
            if default is None or default == "":
                continue
            raw = default
        value = str(raw).strip()
        col_type = col.get("type") or "string"
        if col_type == "enum":
            allowed = col.get("values") or []
            if value not in allowed:
                raise TxnError(f"{key} 只能係: {', '.join(allowed)}")
        elif col_type == "number":
            parse_amount(value)
        elif col_type == "date":
            if not DATE_RE.match(value):
                raise TxnError(f"{key} 必須係 YYYY-MM-DD")
        meta[key] = value
    return meta


def format_transaction(
    *,
    txn_date: str,
    payee: str,
    narration: str,
    amount: Decimal,
    expense_account: str,
    asset_account: str,
    meta: dict[str, str],
    column_order: list[str],
    flag: str = "*",
) -> str:
    if not DATE_RE.match(txn_date):
        raise TxnError("date 必須係 YYYY-MM-DD")
    if flag not in {"*", "!"}:
        raise TxnError("flag 只能係 * 或 !")
    payee = payee.strip()
    if not payee:
        raise TxnError("payee 不能空白")
    expense_account = validate_account(expense_account)
    asset_account = validate_account(asset_account)
    amt = format_amount(amount)
    lines = [f"{txn_date} {flag} {quote_beancount(payee)} {quote_beancount(narration)}"]
    for key in column_order:
        if key in meta:
            lines.append(f"  {key}: {quote_beancount(meta[key])}")
    lines.append(f"  {expense_account}  {amt} HKD")
    lines.append(f"  {asset_account}  -{amt} HKD")
    lines.append("")
    return "\n".join(lines) + "\n"


def year_relpath(txn_date: str) -> str:
    return f"journal/{txn_date[:4]}.beancount"


def ensure_include(main_text: str, relpath: str) -> str | None:
    for line in main_text.splitlines():
        match = INCLUDE_RE.match(line.strip())
        if match and match.group(1) == relpath:
            return None
    if not main_text.endswith("\n"):
        main_text += "\n"
    return main_text + f'include "{relpath}"\n'


def journal_header(year: str) -> str:
    return f"; {year} 交易 — Fava 同 Shortcuts API 都會 append 喺呢個檔。\n\n"


def default_asset_account() -> str:
    return os.environ.get("DEFAULT_ASSET_ACCOUNT", "Assets:Bank:HSBC")


def bean_root() -> Path:
    return Path(os.environ.get("BEAN_ROOT", "/bean"))
