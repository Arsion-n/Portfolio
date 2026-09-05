# iPhone Shortcuts → ledger.arison.me

iOS 捷徑 App 用 **Get Contents of URL**。唔需要安裝額外 App。

事前準備（NAS README Step 3–4）：

- `API_KEY`（`.env`）
- Cloudflare Access Service Token 嘅 **Client ID** + **Client Secret**

三條 header **每條 request 都要**：

| Header | Value |
|---|---|
| `Authorization` | `Bearer <API_KEY>` |
| `CF-Access-Client-Id` | Service Token Client ID |
| `CF-Access-Client-Secret` | Service Token Client Secret |

Secret 只存 Shortcuts（可開「私密」欄位），唔好放相簿或備忘錄。

---

## 建立捷徑「記一筆」

1. 開 **Shortcuts** → **+** → 名：`記一筆`
2. **Ask for Input**：Prompt `店名`，Input Type Text → Magic Variable 改名 `Payee`
3. **Ask for Input**：Prompt `金額 HKD`、Input Type Number → `Amount`
4. **Ask for Input**：Prompt `備註`（Allow Empty）→ `Narration`
5. **Choose from Menu**（科目）例如：
   - 食 → `Expenses:Food`
   - 交通 → `Expenses:Transport`
   - 訂閱 → `Expenses:Subscription`
   - 其他 → `Expenses:Other`  
   每個 menu item 下面放 **Set Variable** `Expense` = 該帳戶字串
6. **Choose from Menu**（付款）：FPS / PayMe / Octopus / Visa / Cash / Autopay → Variable `Pay`
7. （可選）**Ask for Input** `外幣原文` Allow Empty → `Original`（例如 `12.99 USD`）
8. **Get Contents of URL**
   - URL: `https://ledger.arison.me/hook/txn`
   - Method: **POST**
   - Headers：上面三條
   - Request Body: **JSON**
     - `payee` → Payee
     - `narration` → Narration
     - `amount` → Amount（Number）
     - `expense_account` → Expense
     - `pay` → Pay
     - `original` → Original（空就唔加呢個 key）
9. **Show Result** 或 **Show Notification**：顯示回應。成功會有 `"ok": true` 同寫入嘅 Beancount 文字。

第一次行：手機用流動數據，確認唔係靠屋企 LAN。

---

## 進階：自動拉選單

`GET https://ledger.arison.me/hook/schema`（同樣 header）會回：

- `columns[]`：`schema/columns.yaml`（`shortcut: true` 嘅欄最適合做 Menu）
- `accounts.expenses` / `accounts.assets`
- `defaults.asset_account`

改 YAML 加欄之後，捷徑可以改做「先 GET schema 再 Choose from List」，唔使每次改捷徑。第一版用固定 Menu 較穩。

---

## 電腦測試

```bash
curl -sS "https://ledger.arison.me/hook/txn" \
  -H "Authorization: Bearer $API_KEY" \
  -H "CF-Access-Client-Id: $CF_ID" \
  -H "CF-Access-Client-Secret: $CF_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "payee": "Cafe",
    "narration": "午餐",
    "amount": 85,
    "expense_account": "Expenses:Food",
    "pay": "FPS"
  }'
```

Fava 開咗 `auto-reload`，Journal 幾秒內會出現新一筆。
