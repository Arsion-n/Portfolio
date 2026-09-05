# 逐步安裝：ledger.arison.me（Synology DS925+）

跟住由上做到下。**未做完 Step 4（Access 閘）之前，唔好公開 hostname。**  
真正交易只留喺 NAS，唔好 upload 返 GitHub。

準備：電腦、DS925+ 已開機、`arison.me` 已喺 Cloudflare、你嘅 Cloudflare 登入 email。

---

## Step 1 — 下載套件

1. 電腦開：  
   https://github.com/arison-nsh/Portfolio/tree/cursor/ledger-nas-kit-f98d
2. 綠色 **Code** → **Download ZIP**
3. 解壓。入去資料夾 `ledger/`（同層有 `docker-compose.yml`、`Caddyfile`、`data/`、`api/`、`schema/`）。
4. **之後上傳嘅係呢層入面嘅檔，唔係外層成個 Portfolio。**

---

## Step 2 — DSM 安裝 Container Manager

1. 瀏覽器開 DSM（`http://<NAS-IP>:5000` 或 QuickConnect）。
2. **套件中心** → 搜尋 `Container Manager` → **安裝**。
3. 安裝完開一次，同意條款即可。

---

## Step 3 — 開 NAS 資料夾並上傳

1. **控制台 → 共用資料夾**  
   - 若未有 `docker`：新增，名稱 `docker`，位置 `volume1`，儲存。
2. **File Station** → 入 `docker` → **新增資料夾** → 名稱 `ledger`。
3. 入 `docker/ledger`，將 Step 1 嗰層檔 **全部上傳**（可一次拖入）。  
   完成後你應該見到：

   ```
   docker/ledger/
     docker-compose.yml
     Caddyfile
     .env.example
     api/
     data/
     schema/
     synology/
     shortcuts/
     README.md
     SETUP.md
   ```

   若見到 `docker/ledger/ledger/docker-compose.yml`（多重一層），把內層檔移上嚟再刪多餘資料夾。

4. File Station 右上 **設定（齒輪）→ 勾選「顯示隱藏檔」**（`.env` 以點開頭，唔勾會睇唔到）。
5. 喺 `ledger` 入面：對 `.env.example` **右鍵 → 複製**，貼喺同一層。  
   對複本 **右鍵 → 重新命名** 做 `.env`（前面有點）。

---

## Step 4 — 改科目同期初（可之後再改，但建議而家做）

File Station 對檔案右鍵 → **開啟方式 → Text Editor**。

### 4a. `data/accounts.beancount`

- 銀行名改成你真正用嗰啲（例如得 HSBC 就刪 `HangSeng` 嗰行）。
- 加卡：複製 `Liabilities:CreditCard:HSBC` 一行改名。
- 科目名只可以用英文、數字、`-`，層級用 `:`。

### 4b. `data/opening.beancount`

每個真實帳戶一筆。**刪行首 `; `**，改日期同金額。只填資產／負債嗰行；`Equity:Opening-Balances` 唔填數。

例（HSBC 有 12,345.67 HKD）：

```
2026-09-05 * "Opening balance" "HSBC"
  Assets:Bank:HSBC              12345.67 HKD
  Equity:Opening-Balances
```

信用卡欠款用負數或正數負債：欠 800 就 `800.00 HKD` 寫喺 `Liabilities:...` 嗰行。

### 4c. `schema/columns.yaml`（自訂欄位總表）

而家已有 `member`、`pay`、`project`、`original` 等。  
加付款方式：喺 `pay` 嘅 `values:` 下面加一行 `- FPS` 格式。  
加新欄：複製一段，`key` 只可用小寫英文／數字／底線。

儲存所有已改檔。

---

## Step 5 — Cloudflare Zero Trust（閘）

用管 `arison.me` 嗰個 Cloudflare 帳戶。

### 5a. 開 Zero Trust

1. 開 https://dash.cloudflare.com/ → 左欄 **Zero Trust**（或 https://one.dash.cloudflare.com/）
2. 第一次會要 **team name**（內部名，例如 `arison`）→ 揀 **Free** plan → 填付款資料（Free **唔會**收費，但 Cloudflare 仍可能要卡）。
3. 新帳戶預設 login 係 **Cloudflare 帳戶本身**（同你而家登 Dashboard 嗰個）。個人用最省事，**唔使**再設 email PIN。

### 5b. 建 Access application（未開 Tunnel 都要先做）

1. Zero Trust → **Access controls → Applications → Create new application**
2. 揀 **Self-hosted and private**
3. **Add public hostname**
   - Subdomain: `ledger`
   - Domain: `arison.me`  
   → 完整係 `ledger.arison.me`
4. **Access policies** → 建立／選一個 **Allow**
   - Include → **Emails** → 填你 Cloudflare 登入用嘅 email  
   （或 Include → **Cloudflare User** / account member，視介面字眼）
5. Login method：保留 **Cloudflare**（預設）
6. Session duration：例如 24 hours
7. **Create** / Save

做到呢步，未有 Tunnel 都得。重點係閘已經存在。

### 5c. Service Token（iPhone Shortcuts 稍後要用；而家一併整）

1. Zero Trust → **Access controls → Service credentials → Service Tokens → Create Service Token**
2. Name: `iphone-shortcuts`；Duration 可揀 1 year
3. **Generate** → **立刻抄低**  
   - Client ID  
   - Client Secret（只顯示一次）  
   存密碼器，唔好放 GitHub。
4. 返 Step 5b 個 application → **Policies** → 再加一條：
   - Action: **Service Auth**
   - Include → **Service Token** → `iphone-shortcuts`
5. Save

而家有兩條政策：**Allow email**（瀏覽器）+ **Service Auth**（Shortcuts）。

---

## Step 6 — 開 Tunnel，攞 token

1. Cloudflare Dashboard → **Networking → Tunnels**  
   （有啲帳戶喺 Zero Trust → **Networks → Tunnels**）
2. **Create a tunnel**
3. 名稱：`nas-ledger` → **Create Tunnel**
4. Connector 畫面揀 **Docker**。你會見到一條好長嘅 `docker run ... --token eyJ...`
5. **只抄 `eyJ` 開始嗰段 token**，唔好而家喺 NAS 跑呢條 `docker run`（我哋用 compose）。
6. 隧道暫時 **Inactive** 正常。若畫面迫你等 Healthy，揀 Continue / Skip / 關閉都可以，稍後喺 Tunnels 列表再入番個 tunnel。
7. 入 `nas-ledger` → **Routes** → **Add route** → **Published application**
   - Hostname: subdomain `ledger`，domain `arison.me`
   - Service URL: `http://ledger-proxy:80`  
     （一字不差；呢個係 NAS 上 Caddy container 名）
   - 若有 **Protect with Access**：打開，選 Step 5b 個 application
8. Save。Cloudflare 通常會自動加 DNS `CNAME`：`ledger` → `xxxx.cfargotunnel.com`（Proxied 橙雲）。  
   去 **DNS → Records** 確認有 `ledger`。冇就手動加呢條 CNAME，Proxy 開。

---

## Step 7 — 填 NAS 上嘅 `.env`

File Station 開 `docker/ledger/.env`（記得已顯示隱藏檔）。

```
TUNNEL_TOKEN=eyJ...貼 Step 6 整段
API_KEY=
DEFAULT_ASSET_ACCOUNT=Assets:Bank:HSBC
```

`API_KEY`：電腦 Terminal 跑：

```bash
openssl rand -hex 32
```

把輸出貼去 `API_KEY=` 後面（唔好加引號、唔好空格）。  
冇 openssl 就用密碼器產生 32+ 位亂碼。

`DEFAULT_ASSET_ACCOUNT` 改成你 Shortcuts 預設扣嘅帳戶，必須同 `accounts.beancount` 入面某一行 `open` 完全一樣。

儲存。Token / API_KEY **唔好** screenshot 上傳 GitHub。

---

## Step 8 — Container Manager 開專案

1. DSM → **Container Manager** → 左欄 **專案** → **新增**
2. 專案名稱：`ledger`
3. **設定路徑** → 選共用資料夾 `docker` 入面嘅 `ledger` → 選擇
4. 勾選 **使用現有的 docker-compose.yml 來建立專案** → 確定
5. 預覽 YAML 無誤 → 下一步  
   （「網頁入口」可略過，我哋唔用 DSM 反代）
6. **完成** / 啟動。第一次會 download image 同 **build** `ledger-api`，DS925+ 約 1–3 分鐘。
7. 專案狀態要變 **執行中**（綠）。入專案應見四個 container 都 running：

   | 名 | 做咩 |
   |---|---|
   | `ledger-proxy` | Caddy 分流 |
   | `ledger-fava` | 網頁帳本 |
   | `ledger-api` | Shortcuts API |
   | `ledger-tunnel` | 連 Cloudflare |

8. 返 Cloudflare **Tunnels**：`nas-ledger` 應變 **Healthy**。

若專案失敗：專案 → 詳情 → **日誌**。常見原因：`.env` 空 `TUNNEL_TOKEN`、路徑揀錯多重一層 `ledger/ledger`、build 失敗。  
SSH 備案（**控制台 → 終端機及 SNMP** 開 SSH）：

```bash
cd /volume1/docker/ledger
sudo docker compose build
sudo docker compose up -d
sudo docker compose ps
```

**唔好**喺 Router / DSM 防火牆開 80、443、5000 俾外網。

---

## Step 9 — 驗證網站

1. 手機開 **流動數據**（關 Wi-Fi），避免誤以為「得 LAN 先得」。
2. 開 `https://ledger.arison.me`
3. 應出現 Cloudflare Access 登入 → 用你嘅 **Cloudflare 帳戶** 登入（同 Dashboard 嗰個）。
4. 成功後見到 **Fava**（左側有 Journal、Income Statement、Balance Sheet）。
5. Journal / Balance Sheet：期初填咗就有數。

若直接見到 Fava、冇登入頁：Access 未綁到 hostname，即刻返 Step 5–6，唔好繼續用。  
若 1033 / 空白 / 522：Tunnel 未 Healthy，睇 `ledger-tunnel` 日誌。  
若 404：Service URL 唔係 `http://ledger-proxy:80`。

電腦測 API（將三個秘密換走）：

```bash
curl -sS "https://ledger.arison.me/hook/health" \
  -H "CF-Access-Client-Id: <CLIENT_ID>" \
  -H "CF-Access-Client-Secret: <CLIENT_SECRET>"
```

應回 `{"ok":true}`。

---

## Step 10 — iPhone Shortcuts「記一筆」

開 iPhone **Shortcuts（捷徑）** → **+**。

1. **Ask for Input** → Prompt `店名` → Text → 變數改名 `Payee`
2. **Ask for Input** → Prompt `金額 HKD` → Number → `Amount`
3. **Ask for Input** → Prompt `備註` → 允許空白 → `Narration`
4. **Choose from Menu** 科目，每個 item 用 **Set Variable** `Expense`：
   - 食 = `Expenses:Food`
   - 交通 = `Expenses:Transport`
   - 訂閱 = `Expenses:Subscription`
   - 其他 = `Expenses:Other`
5. **Choose from Menu** 付款 → Set Variable `Pay`：`FPS` / `PayMe` / `Octopus` / `Visa` / `Cash` / `Autopay`  
   （字串必須同 `schema/columns.yaml` 入面 `pay.values` **完全一樣**）
6. **Get Contents of URL**
   - URL: `https://ledger.arison.me/hook/txn`
   - Method: **POST**
   - Headers：
     - `Authorization` = `Bearer ` + 你 `.env` 嘅 `API_KEY`（Bearer 後面有一個空格）
     - `CF-Access-Client-Id` = Service Token Client ID
     - `CF-Access-Client-Secret` = Service Token Client Secret
   - Request Body: **JSON**
     - `payee` → Payee
     - `narration` → Narration
     - `amount` → Amount（Number）
     - `expense_account` → Expense
     - `pay` → Pay
7. **Show Notification**：顯示回應。成功有 `"ok": true`。
8. 用 **4G** 跑一次。返 Fava Journal，幾秒內應出現新一筆。

外幣訂閱：`amount` 填銀行扣完手續費嘅 HKD；可另加 JSON key `original` = `12.99 USD`。

---

## Step 11 — 每日備份

1. DSM **控制台 → 工作排程 → 新增 → 排程的工作 → 使用者定義的指令碼**
2. 工作名稱：`ledger-backup`；日期：每日（例如 03:00）
3. 工作設定指令碼：

```bash
/bin/bash /volume1/docker/ledger/synology/backup.sh
```

4. 確定。會 copy 去 `docker/ledger/backups/YYYY-MM-DD/`，90 日後刪。
5. （建議）**Hyper Backup** 再把整個 `docker/ledger` 備份去外置碟，開加密。

---

## 之後點用

| 場景 | 去邊 |
|---|---|
| 屋企電腦入帳、睇報表 | `https://ledger.arison.me` → Fava |
| 出街記一筆 | Shortcuts「記一筆」 |
| 加自訂欄 | 只改 NAS 上 `schema/columns.yaml` |
| 加銀行科目 | 改 `data/accounts.beancount`，然後重載 Fava（或等 auto-reload） |
| 加家人登入（同一本帳） | Access policy 加佢 email；佢會見到全部帳 |

Architecture、家庭版限制、檔案地圖：見 [README.md](README.md)。
