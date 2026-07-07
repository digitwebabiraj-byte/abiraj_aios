# REQ-04-D07 — Shared Modules Inventory (Non-BLOS Code in `ledsone-centralizer`)

> **Shared-repo modules — NOT part of the BLOS / Project Sentinel scope. Inventoried so a new person does not mistake them for BLOS work. Owner: see git authorship per row.**

| Field | Value |
|---|---|
| **Date** | 2026-07-07 |
| **Deliverable** | REQ-04-D07 |
| **Project** | PRJ-2026-003_blos-project-sentinel |
| **Status** | DRAFT |
| **Repository** | `C:\Users\digit\OneDrive\Documents\GitHub\ledsone-centralizer` @ `bc1204a` (branch `Abiraj`) |

## How "no Account-SPA UI page" was established (applies to every row)

The Account SPA route table is `resources/js/Account/Router.js` lines 16–24. Its complete page list is: `Dashboard`, `ThresholdConfigurator`, `OilConfigurator`, `RuleBuilder`, `FileManager`, `Login` (plus redirects). **No POS, PPC/ETL, order-management, inventory, or stock page exists in the SPA** — that single fact is the shared per-row evidence, cited as "Router.js 16–24" below. Additionally, a repo-wide grep of `resources/js/` for the module endpoints (`/products`, `/sales`, `/inventory`, `/reports`, `testData`, `warehouse-location-wise-stock-update`) returns no frontend callers.

Authorship format: `first-commit author, date → last-commit author, date` (from `git log --reverse --format="%an %ad" -- <path> | head -1` and `git log -1`).

---

## 1. POS / Catalog (products, categories, sales, images)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Models/Product.php` | POS product catalog model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Category.php` | POS product category model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Sale.php` | POS sale header model | None — Router.js 16–24 | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 (touch only) |
| `app/Models/SaleItem.php` | POS sale line-item model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Inventory.php` (root) | POS per-product stock quantity model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/Image.php` | Product/category image attachment model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Models/ImageType.php` | Image type lookup model | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `routes/api.php` lines 5–11, 28–33, 97–112 (POS route group) | REST routes for products/categories/sales/inventory/reports/images | None — Router.js 16–24; **no callers in `resources/js/`** | routes introduced by sajeesans2 2026-04-16 (`24169cf`) |
| `database/migrations/2023_01_17_081228_create_product_table.php` | Creates the POS `product` table | n/a (migration) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |

**Caution (for Sajeesan review, reported only):** the controllers those POS routes point at — `Api\CategoryController`, `Api\ProductController`, `Api\InventoryController`, `Api\SaleController`, `Api\ReportController`, `Api\ImageController` — **do not exist in `app/` and never existed in git history** (`git log --all -- <each path>` is empty). The routes are dangling; hitting them 500s. Documented in the companion verification-findings file, Section 5.

## 2. PPC / ETL (Amazon, eBay, Google Ads centralized ETL)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Http/Controllers/Ppc/TestingController.php` | Dev/testing endpoint that copies Amazon performance data into PPC ETL tables (`/testData`) | None — Router.js 16–24 | gajan 2026-05-05 → gajan 2026-05-11 |
| `app/Console/Commands/Ppc/PpcEtlData.php` | Artisan `command:PpcEtlData` — saves campaigns, ad groups, asset groups, assets, performance to ETL tables | None (CLI) | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/Amazon/` (7 models: AmazonAdGroups, AmazonAds, AmazonCampaigns, AmazonPerformanceData, AmazonProducts, AmazonSellerStores, AmazonStoreMarketPlacesDev) | Amazon ads source-data models, all on `ppc` DB connection (`protected $connection = 'ppc'`) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 (directory-level) |
| `app/Models/CentralizedEtlData/Ppc/Ebay/` (6 models: EbayAdGroups, EbayAds, EbayCampaignReportData, EbayCampaigns, EbayPerformanceData, EbaySellerStores) | eBay ads source-data models (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/GoogleAds/` (8 models: GoogleAccounts, GoogleAdGroups, GoogleAssetGroups, GoogleAssetGroupsAssets, GoogleAssetsPerformance, GoogleCampaignPerformance, GoogleCampaigns, GoogleProductPerformance) | Google Ads source-data models (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `app/Models/CentralizedEtlData/Ppc/Common/` (5 models: MarketPlaces, PpcEtl, PpcEtlPerformanceData, Region, States) | Cross-channel ETL target tables + reference data (`ppc` connection) | None — Router.js 16–24 | gajan 2026-05-05 → GAJAN 2026-05-08 |
| `routes/web.php` line 5 (`GET /testData`) | Web route to `TestingController::testData` (PPC ETL trigger) | None — Router.js 16–24 | route added by gajan 2026-05-05 (file last: gajan 2026-05-05) |
| `config/database.php` connection `'ppc'` (line 93) | Dedicated MySQL connection for PPC ETL schema | n/a (config) | config/database.php: sajeesans2 2026-04-16 → gajan 2026-05-05 |

## 3. Order-management / Inventory / Stock-sync

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Http/Controllers/Inventory/StockController.php` | Warehouse/location-wise stock recalculation and sync (`WarehouseLocationWiseStockUpdate`, `GetInvStock`) | None — Router.js 16–24 | sajeesans2 2026-05-05 → sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProducts.php` | Order-management product model (`orders` DB connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 (directory-level) |
| `app/Models/Inventory/InvStock.php` | Stock rows on `orders` connection | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProductCombo.php` | Combo/bundle product mapping (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/InvProductMapping.php` | SKU mapping model (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/ProductPK.php` | Product primary-key/lookup helper (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/Warehouse.php` | Warehouse master (`orders` connection) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `app/Models/Inventory/LocationWiseStock.php` | Location-wise stock result table (**writes to local `mysql` connection**) | None — Router.js 16–24 | sajeesans2 2026-05-05 |
| `routes/api.php` line 22 (`GET /warehouse-location-wise-stock-update`) | Stock-sync trigger route — **outside auth middleware (public)** | None — Router.js 16–24 | sajeesans2 (route group first authored 2026-04-16; stock line added ~2026-05-05) |
| `app/Jobs/CreateBulkShipments.php` | Queued job broadcasting order-update events (stub: `sleep(20)` + broadcast) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Jobs/CreateBulkRuleRun.php` | Queued bulk-rule-run job (order pipeline stub) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Events/OrderUpdateEvents.php` | Broadcast event for order updates (websockets) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Events/MessageSent.php` | Generic broadcast message event (websockets) | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `app/Http/Middleware/WebSocketMiddleware.php` | Websocket auth middleware for the broadcast stack | None — Router.js 16–24 | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `config/websockets.php` + `config/broadcasting.php` | Laravel-websockets / broadcast config supporting the order-event stack | n/a (config) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `database/migrations/0000_00_00_000000_create_websockets_statistics_entries_table.php` | Websockets statistics table (broadcast infra) | n/a (migration) | sajeesans2 2026-04-16 → sajeesans2 2026-04-16 |
| `config/database.php` connections `'orders'` (line 72), `'accounts_management'` (line 114), `'order_management'` (line 134) | External MySQL connections for order/stock/accounts systems | n/a (config) | sajeesans2 2026-04-16 → gajan 2026-05-05 |

## 4. Shared auth plumbing (dual-use — used by BLOS *and* the shared modules; do not refactor unilaterally)

| Path | Purpose (one line) | Account-SPA UI? | Git authorship |
|---|---|---|---|
| `app/Models/auth/User.php` | Legacy/secondary user model under `auth` namespace (not the one used by `CheckAuthMiddleware`, which uses root `App\Models\User`) | Login page only | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 |
| `app/Models/User.php` (root) | Active user model (token auth) — **shared**: created for the POS/base app, later reused by BLOS | Login/Dashboard | sajeesans2 2026-04-16 → digitwebabiraj 2026-05-13 |
| `app/Http/Controllers/auth/AuthController.php` | Login/register/logout/configurations — created with the base app; BLOS SPA consumes login only | Login page | sajeesans2 2026-04-16 → sajeesans2 2026-04-29 |
| `database/migrations/2025_03_15_000001_add_token_to_users_table.php` | Adds `token` column for bearer auth | n/a | sajeesans2 2026-04-16 → digitwebabiraj 2026-04-21 |

---

## Authorship summary

- **POS/catalog, order-management/stock-sync, websockets, base auth:** created and owned by **sajeesans2** (bulk import commit `24169cf`, 2026-04-16; Inventory stock module 2026-05-05).
- **PPC/ETL (CentralizedEtlData, TestingController, PpcEtlData command):** created and owned by **gajan / GAJAN** (2026-05-05 → 2026-05-11).
- **BLOS work (thresholds, rules, file library, Account SPA)** is authored by **digitwebabiraj** — the only overlap with the rows above is incidental touches to shared auth files and `app/Models/Sale.php` (2026-04-21 formatting-era commit).

Nothing in this inventory has an Account-SPA page, and none of it is referenced by the BLOS threshold/rule/file-library controllers. Internals deliberately not documented further — out of BLOS scope.

*Prepared as REQ-04-D07 (DRAFT) — for Sajeesan review where flagged; verification was strictly read-only.*
