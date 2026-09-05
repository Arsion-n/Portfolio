from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ledger import (
    TxnError,
    ensure_include,
    extract_meta,
    format_transaction,
    group_accounts,
    parse_amount,
    parse_open_accounts,
    quote_beancount,
    year_relpath,
)
from schema_loader import load_schema

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = load_schema(ROOT / "schema" / "columns.yaml")


def test_schema_has_member_and_pay():
    assert "member" in SCHEMA["by_key"]
    assert "pay" in SCHEMA["by_key"]
    assert "arison" in SCHEMA["by_key"]["member"]["values"]


def test_parse_amount_rounds_hkd():
    assert parse_amount("12.5") == Decimal("12.50")
    assert parse_amount(12.345) == Decimal("12.35")
    with pytest.raises(TxnError):
        parse_amount("0")
    with pytest.raises(TxnError):
        parse_amount("-1")


def test_quote_and_format_transaction():
    text = format_transaction(
        txn_date="2026-09-05",
        payee='7-Eleven',
        narration='水 "凍"',
        amount=Decimal("12.50"),
        expense_account="Expenses:Food",
        asset_account="Assets:Bank:HSBC",
        meta={"member": "arison", "pay": "FPS"},
        column_order=["member", "pay", "project"],
    )
    assert '2026-09-05 * "7-Eleven" "水 \\"凍\\""' in text
    assert '  member: "arison"' in text
    assert "  Expenses:Food  12.50 HKD" in text
    assert "  Assets:Bank:HSBC  -12.50 HKD" in text
    assert quote_beancount('a"b') == '"a\\"b"'


def test_extract_meta_default_member_and_reject_unknown():
    meta = extract_meta({"payee": "x"}, SCHEMA)
    assert meta["member"] == "arison"
    with pytest.raises(TxnError, match="未定義"):
        extract_meta({"foo": "bar"}, SCHEMA)
    with pytest.raises(TxnError, match="只能係"):
        extract_meta({"pay": "Bitcoin"}, SCHEMA)


def test_accounts_and_include():
    accounts = parse_open_accounts(
        (ROOT / "data" / "accounts.beancount").read_text(encoding="utf-8")
    )
    grouped = group_accounts(accounts)
    assert "Expenses:Food" in grouped["expenses"]
    assert "Assets:Bank:HSBC" in grouped["assets"]
    main = 'include "journal/2026.beancount"\n'
    assert ensure_include(main, "journal/2026.beancount") is None
    updated = ensure_include(main, "journal/2027.beancount")
    assert 'include "journal/2027.beancount"' in updated
    assert year_relpath("2027-01-02") == "journal/2027.beancount"


def test_api_post_txn(tmp_path, monkeypatch):
    data = tmp_path / "bean"
    data.mkdir()
    (data / "journal").mkdir()
    (data / "main.beancount").write_text(
        'include "accounts.beancount"\ninclude "journal/2026.beancount"\n',
        encoding="utf-8",
    )
    (data / "accounts.beancount").write_text(
        (ROOT / "data" / "accounts.beancount").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (data / "journal" / "2026.beancount").write_text("; 2026\n", encoding="utf-8")

    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("BEAN_ROOT", str(data))
    monkeypatch.setenv("SCHEMA_PATH", str(ROOT / "schema" / "columns.yaml"))
    monkeypatch.setenv("DEFAULT_ASSET_ACCOUNT", "Assets:Bank:HSBC")

    from app import app

    client = TestClient(app)
    assert client.get("/hook/health").json() == {"ok": True}
    denied = client.get("/hook/schema")
    assert denied.status_code == 401

    schema = client.get("/hook/schema", headers={"Authorization": "Bearer test-key"})
    assert schema.status_code == 200
    assert "Expenses:Food" in schema.json()["accounts"]["expenses"]

    res = client.post(
        "/hook/txn",
        headers={"Authorization": "Bearer test-key"},
        json={
            "date": "2026-09-05",
            "payee": "Cafe",
            "narration": "午餐",
            "amount": 85,
            "expense_account": "Expenses:Food",
            "pay": "FPS",
            "original": "10.00 USD",
        },
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    journal = (data / "journal" / "2026.beancount").read_text(encoding="utf-8")
    assert "Cafe" in journal
    assert 'pay: "FPS"' in journal
    assert 'original: "10.00 USD"' in journal
    assert " -85.00 HKD" in journal
