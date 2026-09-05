from __future__ import annotations

import fcntl
import os
from decimal import Decimal
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from ledger import (
    TxnError,
    bean_root,
    default_asset_account,
    ensure_include,
    extract_meta,
    format_transaction,
    group_accounts,
    hk_today_aware,
    journal_header,
    parse_amount,
    parse_open_accounts,
    year_relpath,
)
from schema_loader import SchemaError, load_schema, public_schema

app = FastAPI(title="ledger-hook", docs_url=None, redoc_url=None)


class TxnBody(BaseModel):
    model_config = ConfigDict(extra="allow")

    date: str | None = None
    payee: str
    narration: str = ""
    amount: Decimal
    expense_account: str
    asset_account: str | None = None
    flag: str = "*"


def schema_path() -> Path:
    return Path(os.environ.get("SCHEMA_PATH", "/schema/columns.yaml"))


def require_api_key(authorization: str | None) -> None:
    expected = os.environ.get("API_KEY", "")
    if not expected:
        raise HTTPException(status_code=500, detail="伺服器未設定 API_KEY")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization Bearer")
    token = authorization.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=401, detail="API_KEY 不正確")


def load_or_500():
    try:
        return load_schema(schema_path())
    except (OSError, SchemaError) as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/hook/health")
def health():
    return {"ok": True}


@app.get("/hook/schema")
def get_schema(authorization: str | None = Header(default=None)):
    require_api_key(authorization)
    schema = load_or_500()
    accounts_file = bean_root() / "accounts.beancount"
    accounts = parse_open_accounts(accounts_file.read_text(encoding="utf-8"))
    return {
        "columns": public_schema(schema),
        "accounts": group_accounts(accounts),
        "defaults": {
            "asset_account": default_asset_account(),
            "currency": "HKD",
        },
    }


@app.post("/hook/txn")
def post_txn(body: TxnBody, authorization: str | None = Header(default=None)):
    require_api_key(authorization)
    schema = load_or_500()
    payload = body.model_dump()
    extra = body.model_extra or {}
    payload.update(extra)

    txn_date = (body.date or hk_today_aware()).strip()
    try:
        amount = parse_amount(body.amount)
        meta = extract_meta(payload, schema)
        asset = (body.asset_account or default_asset_account()).strip()
        text = format_transaction(
            txn_date=txn_date,
            payee=body.payee,
            narration=body.narration,
            amount=amount,
            expense_account=body.expense_account,
            asset_account=asset,
            meta=meta,
            column_order=[c["key"] for c in schema["columns"]],
            flag=body.flag,
        )
    except TxnError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    root = bean_root()
    rel = year_relpath(txn_date)
    journal = root / rel
    journal.parent.mkdir(parents=True, exist_ok=True)

    main_file = root / "main.beancount"
    with open(main_file, "r+", encoding="utf-8") as main_fh:
        fcntl.flock(main_fh.fileno(), fcntl.LOCK_EX)
        main_text = main_fh.read()
        updated = ensure_include(main_text, rel)
        if updated is not None:
            main_fh.seek(0)
            main_fh.truncate()
            main_fh.write(updated)
            main_fh.flush()
            os.fsync(main_fh.fileno())

    created_year = not journal.exists()
    with open(journal, "a+", encoding="utf-8") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        fh.seek(0, os.SEEK_END)
        if created_year or fh.tell() == 0:
            fh.write(journal_header(txn_date[:4]))
        fh.write(text)
        fh.flush()
        os.fsync(fh.fileno())

    return JSONResponse({"ok": True, "file": rel, "entry": text})
