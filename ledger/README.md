# ledger.arison.me — NAS 部署套件（Synology DS925+）

**由零開始安裝：先睇 [SETUP.md](SETUP.md)（逐步撳掣）。** 下面係架構同檔案說明。

Portfolio 網站繼續只服務 `arison.me`。呢個目錄係 **copy 去 NAS** 用，**唔會**跟 Astro / wrangler 上線。真正交易只存在 NAS 嘅 `data/journal/`，唔好 commit 返 GitHub。

| 你用 | 做咩 |
|---|---|
| 屋企電腦瀏覽器 | Fava（Beancount Web UI） |
| 出街 iPhone | Shortcuts → `POST /hook/txn` |
| 自訂欄位 | 只改一個檔：`schema/columns.yaml` |

```
iPhone / 電腦
  → https://ledger.arison.me
  → Cloudflare Access（email PIN 或 Shortcuts 用 Service Token）
  → Cloudflare Tunnel（NAS 出站，唔使開 port）
  → Caddy  →  /hook* = API    其餘 = Fava
  → data/*.beancount
```

---

## 家庭版難唔難

而家得你用已經預留咗 `member` 欄。

| 想做 | 難度 | 點做 |
|---|---|---|
| 加第二個人入網站 | 易（5 分鐘） | Cloudflare Access policy 加佢 email。**佢會見到全部帳。** |
| 分人記帳 | 易 | 交易填 `member:`；Shortcuts 選單加名 |
| 分開 Assets（聯名戶） | 易 | `accounts.beancount` 加 `Assets:Bank:Joint` |
| 各看各嘅、權限隔離 | 難 | Fava **冇** multi-user ACL。要分開 ledger 檔／分開 container。到時先做。 |

結論：加家人睇同一本帳好易；要私隱隔離先算大工程。

---

## 0. NAS 準備（一次過）

1. DSM 登入 DS925+。
2. **套件中心** → 安裝 **Container Manager**。
3. **控制台 → 共用資料夾** → 新增 `docker`（若未有）。
4. **File Station** → `docker` → 新增資料夾 `ledger`。
5. 將 GitHub 呢個 repo 入面成個 `ledger/` 目錄內容，上傳去 `/docker/ledger/`（即 DSM 路徑 `/volume1/docker/ledger`）。
   - 要有：`docker-compose.yml`、`Caddyfile`、`api/`、`data/`、`schema/`、`synology/`、`.env.example`
6. File Station 複製 `.env.example` 改名做 `.env`。

---

## 1. 填科目同期初

用 Text Editor 開 NAS 上嘅檔（或電腦改完再 upload）：

1. `data/accounts.beancount` — 銀行／卡名改成你真正用嗰啲。唔用嘅科目可以刪。
2. `data/opening.beancount` — 取消註解，**只填資產／負債嗰行金額**（HKD）。`Equity:Opening-Balances` 唔填數，Beancount 會自動平衡。
3. 外幣訂閱：銀行扣完手續費之後幾多 HKD 就記幾多。想留 USD 原文，用欄位 `original`（見 Step 7）。

---

## 2. 自訂欄位（你要嘅「全部 custom name」）

檔案：`schema/columns.yaml`

而家已有：`member`、`pay`、`project`、`location`、`original`、`invoice`、`receipt`、`split_with`、`note`。

加一欄：

```yaml
  - key: shop_type
    label: 店舖類型
    type: enum
    required: false
    shortcut: true
    values:
      - cafe
      - supermarket
```

- `key` 只可用小寫英文、數字、底線。
- `shortcut: true` 會出現喺 `GET /hook/schema`，方便 iPhone 做選單。
- 改完 YAML **唔使**重建 image；下一次 API request 會重讀。
- 未知 key 會被 API 拒絕，避免 Shortcuts 打錯字。

Fava 入帳時喺交易下面加同樣 metadata，例如 `pay: "FPS"`。

---

## 3. Cloudflare Access（閘）— 開 Tunnel 之前做

### 3a. Zero Trust

1. [dash.cloudflare.com](https://dash.cloudflare.com/) → **Zero Trust**
2. 建立 organization（免費 plan 夠個人用）
3. **Settings → Authentication** → 開 **One-time PIN**

### 3b. Access application（瀏覽器）

1. **Zero Trust → Access controls → Applications → Create**
2. **Self-hosted and private** → **Add public hostname**
   - Subdomain: `ledger`
   - Domain: `arison.me`
3. Policy 1：**Allow**
   - Include → **Emails** → 你嘅 email
4. Identity provider：One-time PIN
5. Session：24 hours（隨意）
6. Create

未過呢頁，任何人開 `https://ledger.arison.me` 都唔應該見到 Fava。

### 3c. Service Token（iPhone Shortcuts 用）

1. **Zero Trust → Access controls → Service credentials → Service Tokens → Create**
2. 名：`iphone-shortcuts`；Duration 一年都得
3. **立刻複製** Client ID + Client Secret（Secret 只顯示一次）
4. 返 Access application → 加 Policy 2：
   - Action: **Service Auth**
   - Include → **Service Token** → `iphone-shortcuts`

Policy 次序：Allow email 同 Service Auth 並存即可。

---

## 4. Cloudflare Tunnel

1. Dashboard → **Networking → Tunnels → Create a tunnel**
2. 名：`nas-ledger` → Create
3. Connector 揀 **Docker**，複製 token（好長嗰段 `eyJ...`）
4. NAS `.env`：

```
TUNNEL_TOKEN=eyJ...貼上
API_KEY=（見下一格）
DEFAULT_ASSET_ACCOUNT=Assets:Bank:HSBC
```

`API_KEY` 喺任何電腦產生：

```bash
openssl rand -hex 32
```

5. Tunnel 狀態未 Healthy 都正常，container 未開。
6. 該 Tunnel → **Routes → Add route → Published application**
   - Hostname: `ledger.arison.me`
   - Service URL: `http://ledger-proxy:80`
   - 開 **Protect with Access**，綁 Step 3 個 application

`ledger-proxy` 係 compose 入面 Caddy 嘅 container 名。Cloudflared 同 Caddy 同一個 Docker network，用呢個名。

---

## 5. Container Manager 開 Project

1. **Container Manager → 專案 → 新增**
2. 專案名稱：`ledger`
3. 路徑：選 `/docker/ledger`
4. 應該自動讀到 `docker-compose.yml`
5. 建立／啟動（第一次會 **build** `ledger-api` image，DS925+ 大概一兩分鐘）

若 build 失敗，**控制台 → 終端機及 SNMP** 開 SSH，然後：

```bash
cd /volume1/docker/ledger
sudo docker compose build
sudo docker compose up -d
```

6. 四個 container 都要 **running**：`ledger-proxy`、`ledger-fava`、`ledger-api`、`ledger-tunnel`
7. Cloudflare Tunnel 頁應變 **Healthy**

**唔好**喺 Router / DSM 防火牆開 5000 或 80 俾外網。

屋企 LAN 想直接試（可選）：改 `docker-compose.yml`，取消 `proxy.ports` 註解，重建專案，瀏覽器開 `http://<NAS-IP>:5000`。試完加返註解。

---

## 6. 驗證

1. 手機用 **4G**（唔係屋企 Wi-Fi）開 `https://ledger.arison.me`
2. Cloudflare 要你 email → 收 PIN → 入到 Fava
3. Journal 應見到科目；期初填咗就有 Balance Sheet
4. API health（會被 Access 擋住；用 Service Token）：

```bash
curl -sS "https://ledger.arison.me/hook/health" \
  -H "CF-Access-Client-Id: <CLIENT_ID>" \
  -H "CF-Access-Client-Secret: <CLIENT_SECRET>"
```

應回 `{"ok":true}`。

---

## 7. iPhone Shortcuts

逐步撳掣見 `shortcuts/README.md`。

請求本體：

```json
{
  "payee": "Cafe",
  "narration": "午餐",
  "amount": 85,
  "expense_account": "Expenses:Food",
  "asset_account": "Assets:Bank:HSBC",
  "pay": "FPS",
  "original": "10.00 USD"
}
```

- 金額永遠係 **扣費後 HKD**
- `original` 可選，只備註外幣
- 省略 `date` = 香港當日
- 省略 `asset_account` = `.env` 嘅 `DEFAULT_ASSET_ACCOUNT`
- Header：`Authorization: Bearer <API_KEY>` + 兩條 `CF-Access-*`

讀欄位同科目選單：

```
GET https://ledger.arison.me/hook/schema
```

（同樣三條 header）

---

## 8. 日常備份

**控制台 → 工作排程 → 新增 → 使用者定義的指令碼**，每日：

```bash
/bin/bash /volume1/docker/ledger/synology/backup.sh
```

會 copy `data/` + `schema/` 去 `backups/YYYY-MM-DD/`，90 日後刪。建議再加 **Hyper Backup** 成個 `docker/ledger` 去外置碟（加密）。

---

## 檔案地圖

```
ledger/
  schema/columns.yaml     ← 自訂欄位總表
  data/main.beancount     ← include 入口
  data/accounts.beancount ← 科目
  data/opening.beancount  ← 期初
  data/queries.beancount  ← Fava 左側 Query
  data/journal/YYYY.beancount  ← 真正交易
  api/                    ← Shortcuts HTTP API
  docker-compose.yml
  Caddyfile
  synology/backup.sh
  shortcuts/README.md
```

跨年：API 會自動開 `journal/2027.beancount` 並喺 `main.beancount` 加 `include`。Fava 嘅 `default-file` 要手動改去新年份。
