# ModFraze MVP Operating System
### Architecture Document v1.0 — Shopify + TikTok Shop Bootstrap Build
**Brand:** ModFraze (a branch of MichaelStuartThompson.com)
**Prepared:** July 2026
**Status:** APPROVED-DRAFT — living document, revise as reality teaches you

---

# 1. Executive Summary

ModFraze is a maximalist abstract design brand that sells one-of-a-kind graphics digitally and on print-on-demand merchandise. But it is really **two products in one system**:

1. **A revenue engine** — designs become products, products get listed, content drives traffic, ads amplify winners, email captures buyers for repeat sales.
2. **A portfolio artifact** — every schema, dashboard, automation, and decision framework you build is proof-of-work for your identity as an artist/AI generalist/systems builder.

**What gets built first:** A Shopify store (the brand home you own), a TikTok Shop presence (the discovery engine you rent), a Printify fulfillment backbone, a Google Sheets command dashboard, a Mailchimp welcome flow, and a set of JSON-schema-driven records that make everything traceable. That's it. Five designs, live, tracked.

**What gets deferred:** Etsy, Pinterest, Meta, X, Threads, Reddit, LinkedIn, Printful, and every automation that doesn't directly touch "design → listed → sold → measured." You will feel the pull to add channels. Resist it for 30 days.

**How Shopify and TikTok Shop work together:** TikTok Shop is the top of the funnel — impulse buys, discovery, algorithmic reach. Shopify is the bottom of the funnel and the brand's permanent address — full catalog, email capture, higher-margin sales, retargeting destination. TikTok converts strangers; Shopify converts fans. Every TikTok viewer who doesn't buy in-app should have a path to the Shopify store and the email list.

**How the system supports both revenue and portfolio:** The portfolio layer is not a separate project. Every operational artifact (dashboard, schema, automation log, ad decision record) is captured *as it's created* into `11_Portfolio_Case_Study`. If ModFraze makes $500 in month one, you have revenue proof. If it makes $0, you still have a documented, professionally architected e-commerce operating system — which is itself the résumé item.

**How to think about it operationally:** You are running a factory with four stations — **Make** (design), **List** (product), **Tell** (content/email), **Measure** (dashboard/ads). Each morning, 5 minutes at the dashboard tells you which station needs you today. The system's job is to eliminate the question "what should I do next?" — the dashboard answers it.

---

# 2. MVP Scope

## Must Build Now (Weeks 1–4)
| System | Why it's essential |
|---|---|
| Shopify store, 5 products live | Nothing else matters without something to sell |
| Printify → Shopify connection | Fulfillment without inventory |
| TikTok Shop seller account + 3 listings | Discovery channel; approval takes days, start early |
| Google Sheets dashboard (core tabs) | Your daily decision engine |
| Design → Product JSON records | Traceability + portfolio proof |
| Mailchimp signup form + welcome sequence | Owned audience from day one |
| Content cadence (3 TikToks/week minimum) | TikTok Shop is dead without video |
| Ad Decision framework (rules on paper) | Prevents ad-spend bleeding before it starts |
| Naming conventions + folder structure | Cheap now, expensive to retrofit |
| Portfolio Evidence Log | Capture proof daily, not retroactively |

## Build Next (Weeks 5–10, after first sales/tests)
- Abandoned cart email flow (needs traffic to matter)
- Etsy onboarding (best 3–5 proven designs only)
- Pinterest (evergreen pins of proven products)
- First paid ad tests ($5–10/day TikTok Spark Ads on organic winners)
- `generate_product_copy.py` and `calculate_ad_decisions.py` scripts
- Buyer/non-buyer email segmentation
- Product drop email template + first "drop" event

## Defer Until Later (Month 3+)
- Meta Business Suite / Facebook / Instagram ads
- X, Threads, Reddit, LinkedIn presence (founder-narrative content only, opportunistic)
- Printful as second supplier (only if Printify quality fails)
- Zapier/Make paid automations
- Airtable migration (Sheets is fine under ~500 rows per tab)
- Custom API integrations beyond CSV import/export
- VIP/collector tiers, limited editions, digital-download products

---

# 3. Recommended Project Folder Structure

Local root: `ModFraze_MVP_OS/`

```
ModFraze_MVP_OS/
│
├── 00_Command_Center/
│   ├── ModFraze_Dashboard_LINK.md        # link to the Google Sheet
│   ├── Weekly_Review_Template.md
│   ├── Daily_5min_Checklist.md
│   ├── Decision_Log.md                   # every non-trivial decision, dated
│   └── 30_Day_Build_Plan.md
│
├── 01_Brand_System/
│   ├── Brand_Voice_Rules.md
│   ├── Visual_Placeholders.md            # candidate palettes/fonts until final
│   ├── Approved_Phrases.md
│   ├── Forbidden_Cliches.md
│   └── Logo_WIP/
│
├── 02_Design_Pipeline/
│   ├── 01_Raw/                           # untouched source files
│   ├── 02_Working/                       # in-progress edits
│   ├── 03_Approved/                      # final masters, full-res
│   ├── 04_Exports/                       # sized per product type
│   │   ├── Tees_4500x5400/
│   │   ├── Posters_300dpi/
│   │   └── Mugs_Wraps/
│   └── Design_Records/                   # one JSON per design
│
├── 03_Product_Catalog/
│   ├── Product_Records/                  # one JSON per product listing
│   ├── Mockups/
│   │   └── MF-PROD-*/                    # folder per product
│   ├── Pricing_Sheet.md                  # cost × 2.5 floor, per product type
│   └── Copy_Bank/                        # approved titles/descriptions
│
├── 04_Sales_Channels/
│   ├── Shopify/
│   │   ├── Store_Settings_Notes.md
│   │   ├── Collections_Map.md
│   │   └── CSV_Exports/
│   ├── TikTok_Shop/
│   │   ├── Listing_Checklist.md
│   │   ├── Video_Product_Map.md          # which video pushes which product
│   │   └── CSV_Exports/
│   ├── Etsy_Queue/                       # deferred; park proven designs here
│   └── Pinterest_Queue/                  # deferred
│
├── 05_Content_Engine/
│   ├── Content_Calendar_LINK.md
│   ├── Hooks_Bank.md
│   ├── Scripts/                          # TikTok video scripts
│   ├── CapCut_Projects/
│   ├── Canva_Assets_LINK.md
│   └── Posted_Archive/                   # post records (JSON)
│
├── 06_Ad_System/
│   ├── Ad_Decision_Rules.md              # push/iterate/pause/kill thresholds
│   ├── Campaign_Records/                 # one JSON per campaign
│   ├── Creative_Variants/
│   └── Ad_Performance_Log/               # one JSON per ad, per review
│
├── 07_Email_System/
│   ├── Flow_Map.md
│   ├── Welcome_Sequence/                 # drafts of each email
│   ├── Drop_Announcements/
│   ├── Studio_Notes/
│   └── Email_Records/                    # one JSON per campaign
│
├── 08_Analytics_Dashboard/
│   ├── Sheets_Backups/                   # weekly CSV export of the dashboard
│   ├── Metric_Definitions.md             # how each KPI is calculated
│   └── Weekly_Snapshots/                 # screenshot per week (portfolio gold)
│
├── 09_Automations/
│   ├── Automation_Inventory.md           # what exists, what's planned
│   ├── scripts/
│   │   ├── generate_product_copy.py
│   │   ├── calculate_ad_decisions.py
│   │   ├── validate_json_records.py
│   │   ├── export_platform_csvs.py
│   │   └── generate_portfolio_log.py
│   └── Automation_Log.md                 # every run, dated
│
├── 10_API_Integrations/
│   ├── Integration_Notes.md              # keys location, rate limits, quirks
│   ├── .env.example                      # never commit real keys
│   └── CSV_Fallbacks.md                  # manual paths when APIs misbehave
│
├── 11_Portfolio_Case_Study/
│   ├── Evidence_Log.md                   # dated entries, added daily
│   ├── Screenshots/
│   │   ├── Week01/ Week02/ Week03/ Week04/
│   ├── Metrics_Snapshots/
│   ├── Technical_Decisions.md
│   ├── Before_After/
│   └── Case_Study_Draft.md
│
└── 99_Archive/
    ├── Killed_Ads/
    ├── Retired_Designs/
    └── Old_Versions/
```

**Why each major folder exists:**
- **00_Command_Center** — the single place you open every morning. If a file answers "what do I do today?", it lives here.
- **01_Brand_System** — governance, not aesthetics. Keeps copy consistent while visual branding is still in flux.
- **02_Design_Pipeline** — enforces the raw → working → approved → exported flow so you never lose a master file or ship an unapproved design.
- **03_Product_Catalog** — the bridge between art and commerce. Every sellable thing has a record here regardless of platform.
- **04_Sales_Channels** — platform-specific operational notes and CSV exports. Queues for deferred channels prevent "I'll just quickly set up Etsy" scope creep — park the idea, keep moving.
- **05_Content_Engine** — hooks, scripts, and posted-content records. Content is the fuel for TikTok Shop; treat it like inventory.
- **06_Ad_System** — the rules live here *before* the first dollar is spent, so ad decisions are mechanical, not emotional.
- **07_Email_System** — drafts and records for the owned-audience machine.
- **08_Analytics_Dashboard** — backups and definitions. The Sheet is live in Google; this folder is its paper trail.
- **09_Automations** — code and the log proving it ran. The log is portfolio evidence.
- **10_API_Integrations** — credentials hygiene and the honest list of what's manual vs. automated.
- **11_Portfolio_Case_Study** — the second product. Populated daily via the Evidence Log habit.
- **99_Archive** — nothing gets deleted; killed things get archived with their data intact (kill decisions are portfolio material too).

---

# 4. Naming Conventions

**Master pattern:** `MF-{TYPE}-{YYYYMMDD}-{ShortName}-V{NN}`

| Asset | Pattern | Example |
|---|---|---|
| Design | `MF-DES-YYYYMMDD-ShortName-V01` | `MF-DES-20260701-NeonSprawl-V01` |
| Product SKU | `MF-{DesignShort}-{ProductCode}-{Variant}` | `MF-NEONSPRAWL-TEE-BLK-L` |
| Collection | `MFC-ShortName` | `MFC-Maximal-Vol1` |
| Mockup | `MF-MOCK-{SKU-root}-{Scene}-V01` | `MF-MOCK-NEONSPRAWL-TEE-Studio-V01` |
| Canva file | `MF-CANVA-{Purpose}-{ShortName}-V01` | `MF-CANVA-Promo-NeonSprawl-V01` |
| CapCut file | `MF-CAP-{Hook}-{ShortName}-V01` | `MF-CAP-Reveal-NeonSprawl-V01` |
| Ad campaign | `MF-AD-{Platform}-{YYYYMM}-{Objective}-{NN}` | `MF-AD-TT-202607-Conversions-01` |
| Email campaign | `MF-EM-{FlowOrDate}-{ShortName}` | `MF-EM-20260715-DropNeonSprawl` |
| TikTok video | `MF-TT-YYYYMMDD-{Hook}-{ShortName}` | `MF-TT-20260710-POV-NeonSprawl` |
| Social post | `MF-POST-{Platform}-YYYYMMDD-{NN}` | `MF-POST-IG-20260712-01` |
| Exported asset | `{DesignName}_{ProductCode}_{Dimensions}.png` | `NeonSprawl_TEE_4500x5400.png` |
| JSON file | `{record_id}.json` | `MF-DES-20260701-NeonSprawl-V01.json` |
| Dashboard backup | `MF-DASH-YYYYMMDD.csv` | `MF-DASH-20260707.csv` |

**Product codes:** `TEE`, `HOOD`, `POSTER`, `MUG`, `TOTE`, `PHONE`, `STICKER`, `CANVAS`.

**Version/status rules (used in JSON `status` fields and filenames):**
| Status | Meaning | Rule |
|---|---|---|
| `draft` | In progress, not reviewed | Lives in `02_Working` |
| `review` | Awaiting a decision | Max 48 hours in review — decide or archive |
| `approved` | Final master, ready to productize | Moves to `03_Approved`; version locks |
| `published` | Live on at least one platform | Record must list platform URLs |
| `archived` | Retired or killed | Moves to `99_Archive` with data intact |

Version numbers increment only on *approved-file changes* (`V01` → `V02`). Drafts overwrite themselves.

---

# 5. Data Model and JSON Schemas

Every core object gets one JSON record. These live in the folders above and mirror rows in the dashboard. Validate weekly with `validate_json_records.py`.

## 5.1 Design Asset — `Design_Records/`
```json
{
  "design_id": "MF-DES-20260701-NeonSprawl-V01",
  "title": "Neon Sprawl",
  "collection": "MFC-Maximal-Vol1",
  "visual_description": "Dense layered neon geometry over deep navy field; magenta-to-crimson gradient bands colliding with fragmented grid structures",
  "mood_tags": ["electric", "dense", "urban", "loud"],
  "color_tags": ["#FF204E", "#A0153E", "#5D0E41", "#00224D"],
  "source_file": "02_Design_Pipeline/03_Approved/MF-DES-20260701-NeonSprawl-V01.psd",
  "export_files": [
    "02_Design_Pipeline/04_Exports/Tees_4500x5400/NeonSprawl_TEE_4500x5400.png",
    "02_Design_Pipeline/04_Exports/Posters_300dpi/NeonSprawl_POSTER_24x36.png"
  ],
  "created_date": "2026-07-01",
  "status": "approved",
  "usage_rights": "original-work-full-rights",
  "notes": "Strong candidate for launch drop. Test tee + poster first."
}
```

## 5.2 Product Listing — `Product_Records/`
```json
{
  "product_id": "MF-NEONSPRAWL-TEE",
  "design_id": "MF-DES-20260701-NeonSprawl-V01",
  "product_type": "TEE",
  "vendor": "Printify",
  "platform": ["shopify", "tiktok_shop"],
  "title": "Neon Sprawl — Maximalist Graphic Tee",
  "description": "A dense collision of neon geometry you can wear. Original abstract design by Michael Stuart Thompson. Printed on premium heavyweight cotton.",
  "tags": ["abstract", "maximalist", "graphic tee", "neon", "art tee"],
  "price": 29.99,
  "cost": 11.5,
  "margin": 0.62,
  "mockup_urls": ["03_Product_Catalog/Mockups/MF-NEONSPRAWL-TEE/MF-MOCK-NEONSPRAWL-TEE-Studio-V01.png"],
  "listing_status": "published",
  "publish_date": "2026-07-08",
  "platform_urls": {
    "shopify": "https://modfraze.com/products/neon-sprawl-tee",
    "tiktok_shop": "https://shop.tiktok.com/..."
  }
}
```
**Rule embedded in schema:** `price >= cost * 2.5`. The validation script enforces this.

## 5.3 Campaign — `Campaign_Records/`
```json
{
  "campaign_id": "MF-AD-TT-202607-Conversions-01",
  "platform": "tiktok",
  "objective": "conversions",
  "target_audience": "US, 18-34, interests: streetwear, abstract art, graphic design",
  "product_ids": ["MF-NEONSPRAWL-TEE"],
  "creative_assets": ["MF-TT-20260710-POV-NeonSprawl"],
  "budget": {"daily": 10, "total_cap": 70},
  "start_date": "2026-07-14",
  "end_date": "2026-07-21",
  "status": "active",
  "KPI_targets": {"ROAS": 2.0, "CTR": 0.01, "CPC_max": 1.0}
}
```

## 5.4 Content Post — `Posted_Archive/`
```json
{
  "post_id": "MF-TT-20260710-POV-NeonSprawl",
  "platform": "tiktok",
  "content_type": "product_reveal_video",
  "hook": "POV: your closet finally matches your personality",
  "caption": "Neon Sprawl just dropped. One design, never repeated. #maximalist #graphictee #abstractart",
  "CTA": "Tap the product link before it's gone",
  "asset_url": "05_Content_Engine/CapCut_Projects/MF-CAP-Reveal-NeonSprawl-V01.mp4",
  "product_id": "MF-NEONSPRAWL-TEE",
  "scheduled_date": "2026-07-10",
  "posted_url": "https://tiktok.com/@modfraze/video/...",
  "performance_metrics": {"views": 0, "likes": 0, "shares": 0, "product_clicks": 0, "sales": 0}
}
```

## 5.5 Email Campaign — `Email_Records/`
```json
{
  "email_id": "MF-EM-20260715-DropNeonSprawl",
  "segment": "all_subscribers",
  "subject_line": "One design. Never repeated. Meet Neon Sprawl.",
  "preview_text": "The first ModFraze drop is live — and it doesn't come back.",
  "body_theme": "product_drop",
  "products_featured": ["MF-NEONSPRAWL-TEE"],
  "CTA": "Shop the drop",
  "send_date": "2026-07-15",
  "performance_metrics": {"sent": 0, "open_rate": 0, "click_rate": 0, "revenue": 0}
}
```

## 5.6 Ad Performance Record — `Ad_Performance_Log/`
```json
{
  "ad_id": "MF-AD-TT-202607-Conversions-01-A",
  "campaign_id": "MF-AD-TT-202607-Conversions-01",
  "platform": "tiktok",
  "review_date": "2026-07-17",
  "spend": 30.0,
  "impressions": 14200,
  "clicks": 168,
  "CTR": 0.0118,
  "CPC": 0.18,
  "conversions": 2,
  "revenue": 59.98,
  "ROAS": 2.0,
  "decision": "iterate",
  "next_action": "Test new hook on same creative; keep budget flat 3 more days"
}
```

---

# 6. Spreadsheet / Dashboard Architecture

**Tool:** Google Sheets (one workbook: `ModFraze_Dashboard`). Migrate to Airtable only if any tab exceeds ~500 rows or you need relational lookups you can't fake with `VLOOKUP`.

| Tab | Purpose | Key Columns | Status Field | Key Formulas | Review Cadence |
|---|---|---|---|---|---|
| **Dashboard** | The 5-minute morning view | Date, Revenue (7d), Orders (7d), Top Product, Top Design, Top Platform, Ad Spend (7d), Blended ROAS, Email Subs, Flags | — | Pulls from all tabs via `QUERY`/`SUMIFS` | **Daily, 5 min** |
| **Designs** | Master design registry | design_id, title, collection, status, created_date, products_count, total_revenue | draft/review/approved/published/archived | `products_count = COUNTIF(Products!design_id)` | Weekly |
| **Products** | Master product registry | product_id, design_id, type, vendor, price, cost, margin, platforms, listing_status, lifetime_revenue, lifetime_units | draft/published/archived | `margin = (price-cost)/price`; flag if `price < cost*2.5` | Weekly |
| **Shopify Listings** | Platform-specific state | product_id, url, publish_date, views, ATC, conversions, conv_rate | live/paused | `conv_rate = conversions/views` | 2×/week |
| **TikTok Shop Listings** | Platform-specific state | product_id, url, publish_date, linked_videos, video_views, clicks, sales | live/paused | click-through from video views | 2×/week |
| **Etsy Queue** | Deferred parking lot | design_id, priority, why, earliest_date | queued | — | Monthly |
| **Pinterest Queue** | Deferred parking lot | product_id, pin_concept, earliest_date | queued | — | Monthly |
| **Content Calendar** | What posts when | post_id, platform, hook, product_id, scheduled_date, posted_url, views, clicks | planned/posted/skipped | — | Daily glance |
| **Ads** | Campaign registry | campaign_id, platform, objective, product_ids, daily_budget, start, end, status | active/paused/ended | — | Daily during active campaigns |
| **Ad Performance** | Per-ad review rows | ad_id, review_date, spend, impressions, clicks, CTR, CPC, conversions, revenue, ROAS, decision | push/iterate/pause/kill | `ROAS = revenue/spend`; conditional formatting per §7 | Daily during active campaigns |
| **Email Campaigns** | Send log | email_id, segment, subject, send_date, sent, opens, clicks, revenue | draft/scheduled/sent | open_rate, click_rate | Weekly |
| **Audience Segments** | Mailchimp segment sizes | segment, size, growth_7d, last_campaign | — | growth delta | Weekly |
| **Revenue** | Every order | date, order_id, platform, product_id, gross, fees, cost, net | — | `net = gross - fees - cost` | Weekly |
| **Costs** | Every expense | date, category (tools/ads/fees/samples), amount, note | — | monthly SUMIFS | Weekly |
| **Experiments** | Hypothesis log | exp_id, hypothesis, metric, start, end, result, learning | running/done | — | Weekly |
| **Automation Log** | Script/zap run history | date, automation, trigger, result, manual_fallback_used | ok/failed | — | Weekly |
| **Portfolio Evidence Log** | Proof-of-work entries | date, artifact, skill_demonstrated, file_path/screenshot | — | — | **Daily, 2 min** |
| **Archive** | Killed/retired rows | original tab, record_id, archive_date, reason | — | — | Monthly |

**Metrics the Dashboard tab must surface (with source):**
- Revenue (7d / 30d) — Revenue tab
- Gross margin % — Revenue + Costs
- Conversion rate — Shopify Listings
- Email signup rate — Mailchimp subs ÷ Shopify sessions
- CPC, cost per purchase, ROAS, CTR — Ad Performance
- Add-to-cart rate, abandoned checkout rate — Shopify analytics (manual entry weekly)
- Best-selling product type / best design / best platform — `INDEX/MATCH` over Revenue
- Ad decisions due today — count of Ad Performance rows where `decision` is blank and `review_date <= TODAY()`

---

# 7. Ad Decision System

Rules are written *before* the first dollar is spent, so review is mechanical. Minimum data gate: **no decision before $15 spend or 3 days per ad** (whichever comes first) — earlier numbers are noise.

| Decision | Color | Trigger (after minimum data gate) | Action |
|---|---|---|---|
| **PUSH** | 🟢 Green | ROAS > 3.0 **and** CTR ≥ 1.0% | Raise daily budget +20–30% (never double overnight); clone winning creative into 2 variations |
| **ITERATE** | 🟡 Yellow | ROAS 2.0–3.0, **or** CTR ≥ 1.0% but few conversions | Something works, something doesn't. Change ONE variable: hook → thumbnail → caption → audience → offer (in that order). Keep budget flat. |
| **PAUSE** | 🟠 Orange | ROAS 1.5–2.0, **or** high CTR + zero conversions after $25 | Stop spend. Diagnose the *landing page/listing*, not the ad — clicks without buys usually means the product page failed. Fix, then relaunch as new ad. |
| **KILL** | 🔴 Red | ROAS < 1.5 after $25 spend, **or** CTR < 0.5% after $15 | Stop permanently. Archive record with data. Never relaunch the same creative + audience combo. |

**Sheet implementation (Ad Performance tab):**
```
=IFS(spend < 15, "WAIT",
     AND(ROAS > 3, CTR >= 0.01), "PUSH",
     ROAS >= 2, "ITERATE",
     ROAS >= 1.5, "PAUSE",
     TRUE, "KILL")
```
Conditional formatting: PUSH=green, ITERATE=yellow, PAUSE=orange, KILL=red, WAIT=gray.

**Solo-founder guardrails:**
- One decision pass per day, at dashboard time. No mid-day peeking — intraday numbers cause panic edits.
- Max 3 active ads during MVP. More than that and you can't attribute anything.
- The formula decides; you execute. If you disagree with the formula twice in a row, change the *thresholds* (documented in Decision_Log.md), not the individual call.

---

# 8. Product Pipeline

**Design-to-market flow (target: 48–72 hours from approved design to live listing):**

1. **Raw design** → drop source file into `02_Design_Pipeline/01_Raw/`
2. **Design naming** → assign `MF-DES-` ID, create JSON record, set `status: draft`
3. **Export sizing** → generate per-product-type exports into `04_Exports/` (tee 4500×5400 PNG transparent, poster 300dpi at print sizes, mug wrap per Printify spec)
4. **Mockup generation** → Printify auto-mockups + 1–2 Canva lifestyle mockups; save to `03_Product_Catalog/Mockups/`
5. **Product selection** → choose 1–2 product types per design (not five). Tee + poster is the default launch pair.
6. **Product description** → run the description prompt (§14) → edit → save to `Copy_Bank/`
7. **Pricing** → cost × 2.5 minimum; round to .99; log in `Pricing_Sheet.md`
8. **Shopify listing** → publish via Printify → Shopify sync; assign collection; verify mobile view
9. **TikTok Shop listing** → publish; confirm product is taggable in videos
10. **Launch content** → 1 reveal TikTok + 1 mockup post, same week
11. **Email mention** → include in next studio note or drop email
12. **Ad test** → only after organic signal (a video with above-average views) — Spark Ad the winner at $5–10/day
13. **Performance review** → ad decision rules (§7) + weekly product review
14. **Revision or archive** → iterate copy/creative for mid-performers; archive dead products with data

**Checklists** (each lives as a .md template; copy per instance):

**New Design Intake** — ☐ Source file in `01_Raw` ☐ ID assigned ☐ JSON created ☐ Visual description written ☐ Mood/color tags ☐ Status set ☐ Dashboard row added ☐ Evidence Log entry
**New Product Creation** — ☐ Product type chosen ☐ Exports generated ☐ Printify product created ☐ Mockups saved ☐ Copy drafted + edited ☐ Price ≥ cost×2.5 ☐ JSON created ☐ Dashboard row
**Shopify Publish** — ☐ Synced from Printify ☐ Title/description/tags final ☐ Collection assigned ☐ Mobile preview checked ☐ URL logged in JSON ☐ Test order flow to checkout
**TikTok Shop Publish** — ☐ Listing live ☐ Product taggable ☐ Compliance check (no restricted claims) ☐ URL logged ☐ First video scheduled
**Launch Campaign** — ☐ Reveal video posted ☐ Mockup post ☐ Email mention scheduled ☐ Content Calendar rows added ☐ Screenshot to Portfolio
**Post-Launch Review (day 14)** — ☐ Revenue/views/clicks logged ☐ Ad decision recorded (if ads ran) ☐ Iterate/keep/archive call ☐ Learning added to Experiments tab

---

# 9. Platform Strategy

## Shopify — the brand home you own
- **Role:** permanent address, full catalog, email capture, margin protection, retargeting destination.
- **Product organization:** flat catalog during MVP; every product in exactly one collection.
- **Collections:** start with 2 — `Maximal Vol. 1` (launch drop) and `All Designs`. Add themed collections only when you have 10+ products.
- **Product pages:** hero mockup + flat design shot + close-up detail; description leads with the *design story*, not the garment specs; specs collapsed below.
- **Landing pages:** homepage IS the landing page during MVP. One hero, one drop, one CTA.
- **Email capture:** popup at 8-second delay or 40% scroll, offering "early access to drops" (not a discount — protects margin and brand positioning).
- **Analytics:** enable Shopify native analytics day one; log key numbers into the Sheet weekly (manual is fine).
- **Abandoned cart:** turn on Shopify's built-in abandoned checkout email immediately (zero effort); custom Mailchimp flow is a Build-Next item.
- **Upsells/cross-sells:** defer apps; instead, end every product description with "Pairs with:" linking one other product.
- **SEO basics:** unique title/meta per product, alt text on every image describing the design, clean URL handles matching design names.

## TikTok Shop — the discovery engine you rent
- **Role:** algorithmic reach, impulse purchases, creative testing lab. TikTok tells you which designs the market wants; Shopify monetizes that knowledge at better margins.
- **Short-form workflow:** batch-film 3 videos per session (reveal, styling/context, process/behind-the-scenes); edit in CapCut with saved templates; post 3×/week minimum.
- **Product tagging:** every video tags exactly one product. One video = one product = clean attribution.
- **Listing workflow:** mirror Shopify copy but shorten titles to <34 chars visible; punchier first line.
- **Creator-style content:** shoot like a person, not a brand — handheld, voiceover, native text. Polish reads as ad; ads get scrolled.
- **Ad testing:** Spark Ads on organic winners only. Never cold-launch ad creative that hasn't earned organic views.
- **Hooks:** maintain `Hooks_Bank.md`; log every hook's view count; reuse winners across designs.
- **Fulfillment:** Printify handles it, but watch TikTok Shop's shipping-time SLAs — late shipment kills seller scores. Confirm Printify production times fit before listing.

## Etsy (Build Next)
Onboard after 2–3 designs show organic traction. List only proven winners — Etsy rewards listing quality + reviews, so seed it with your best. Posters and prints first (Etsy's art-buyer intent is strong).

## Pinterest (Build Next)
Onboard alongside Etsy. Pin every mockup with keyword-rich descriptions linking to Shopify. It's a slow-burn evergreen channel — 15 min/week, compounds for months.

## Facebook / Instagram / Meta Business Suite (Defer)
Value = retargeting Shopify visitors + brand legitimacy (people check IG before buying). MVP action: reserve @modfraze handles, post 1 mockup/week cross-posted from TikTok content. Real Meta ads wait until Shopify traffic justifies retargeting.

## X / Threads / Reddit / LinkedIn (Defer — founder narrative only)
These sell *Michael*, not tees. Build-in-public posts: dashboard screenshots, automation wins, honest numbers. LinkedIn especially — it's the portfolio layer's distribution channel. Opportunistic, never scheduled during MVP.

## Printify / Printful
Printify is the single supplier during MVP. **One supplier, one catalog, one quality standard.** Order a sample of each product type before launch. Printful enters only if Printify fails on quality or a needed product. Never split one design across both suppliers — variant chaos.

## Canva / CapCut
Repeatable production tools, not creative playgrounds. Build once, reuse forever: 3 Canva templates (product announcement, quote/commentary card, email header) and 2 CapCut templates (reveal video, process video). Template names follow §4 conventions.

## Mailchimp
The owned audience — the only asset no algorithm can take. Every channel funnels here. Goal for month one: 50 subscribers and a welcome sequence that introduces the artist, not just the merch.

---

# 10. Email Strategy (Mailchimp MVP)

**Signup strategy:** one form, one promise — *"Early access to drops. Each design is one-of-a-kind; subscribers see it first."* Placed as Shopify popup + link-in-bio + verbal CTA in TikToks.

| Flow name | Goal | Trigger | Timing |
|---|---|---|---|
| **MF-FLOW-Welcome** | Introduce artist + brand, drive first visit | Signup | Email 1 instant: "Welcome to the loud side" (story + what to expect). Email 2 (+2d): "How a ModFraze design gets made" (process, builds value). Email 3 (+5d): "Start here" (3 current products, soft CTA). |
| **MF-FLOW-AbandonedCart** | Recover checkout drop-offs | Abandoned checkout (Shopify native now; Mailchimp custom later) | +4h reminder; +24h "still here, still one-of-a-kind" |
| **MF-EM-Drop-{Name}** | Launch revenue spike | Manual, per drop | Day-of announcement; optional +48h "last look" |
| **MF-FLOW-StudioNote** | Retention, brand affinity | Manual, biweekly | Behind-the-scenes, one design story, one product link. Not a sales blast. |
| **MF-FLOW-Reengage** | Wake 60-day inactives | Segment: no opens 60d | "Still making loud things — want to keep seeing them?" One email; prune non-responders. |

**Segments:** `buyers` (auto-tag on purchase), `non_buyers`, `VIP/collectors` (2+ purchases — defer active use, but tag from day one so the data exists).

**Subject-line formulas:**
- Drop: `{Design name}. One of one. Live now.`
- Curiosity: `This design almost didn't survive`
- Direct: `New: {Design name} — {product type}`
- Studio note: `From the studio: {one-line hook}`
Rules: under 45 characters, no ALL CAPS, no "🔥 SALE", one emoji max.

---

# 11. Content Engine

**Content categories:** new design reveal · product mockup · behind-the-scenes/process · maximalist design commentary · artist/founder story · AI-assisted workflow · product push (Shopify/TT Shop) · build-in-public/portfolio · email CTA · limited drop CTA.

**Weekly cadence (realistic for one person — ~4 hours total):**

| Day | Task | Output |
|---|---|---|
| Mon | Batch film (60–90 min) | Raw footage for 3 videos |
| Tue | Edit + post TikTok #1 (reveal) | 1 TikTok |
| Wed | Post TikTok #2 (process/BTS) + cross-post mockup to IG | 1 TikTok, 1 IG |
| Thu | Post TikTok #3 (commentary or push) | 1 TikTok |
| Fri | Build-in-public post (LinkedIn or X, 15 min, opportunistic) | 1 post |
| Biweekly | Studio note email | 1 email |

**Reusable post templates:**
- **TikTok:** HOOK (first 1.5s, text on screen) → 15–30s payoff (design reveal/process) → verbal CTA ("link on the product tag") → caption: 1 line + 3–5 hashtags.
- **Instagram:** carousel — mockup, flat design, detail crop; caption = design story (2–3 sentences) + "Link in bio."
- **Facebook:** repost IG carousel + one extra context sentence.
- **X:** image + one wry line about the design; no hashtags; thread only for build-in-public.
- **Threads:** conversational version of the X post; ask a question.
- **Reddit:** value-first only (r/graphic_design process posts); never link-drop; sell nothing directly.
- **LinkedIn:** build-in-public — what you built, screenshot, what you learned, no hard sell.
- **Pinterest:** vertical mockup pin; keyword-stuffed description ("maximalist abstract art t-shirt, bold graphic tee…"); Shopify link.


---

# 12. Automation Architecture

**Governing principle (Mike's rule): manual before automated.** Run every workflow by hand at least 3 times before scripting it. Automate the proven, not the imagined.

## MVP Automations (Weeks 1–4)
| # | Trigger | Action | Tool | Required fields | Risk / limitation | Manual fallback |
|---|---|---|---|---|---|---|
| 1 | New design set to `approved` | Create Products-tab row skeleton | Google Sheets `onEdit` Apps Script (or manual) | design_id, title | Script errors silently | Copy template row by hand |
| 2 | Product row status → `ready` | Generate listing-copy prompt (filled placeholders) | `generate_product_copy.py` or manual prompt from §14 | design JSON + product type | LLM copy needs human edit — always review | Fill prompt template by hand |
| 3 | Printify product published | Auto-sync to Shopify | **Printify native integration** | connected store | Sync lag; verify each listing | Manual Shopify product creation |
| 4 | Shopify listing published | Add row to Content Calendar | Manual (2 min) — automate later | product_id, url | none | is the fallback |
| 5 | Customer purchases (Shopify) | Tag as `buyer` in Mailchimp | **Mailchimp–Shopify native integration** | connected accounts | Sync delay up to 1h | Weekly manual tag pass |
| 6 | Email signup | Trigger welcome sequence | **Mailchimp native automation** | flow built | none | — |
| 7 | Abandoned checkout | Recovery email | **Shopify native** | enabled in settings | generic template | Acceptable for MVP |

## Next Automations (Weeks 5–10)
| Trigger | Action | Tool | Risk | Fallback |
|---|---|---|---|---|
| Ad review row completed | Compute push/iterate/pause/kill | Sheet formula (§7) + `calculate_ad_decisions.py` for JSON logs | garbage-in from typos | Read the table yourself |
| TikTok Shop listing published | Add to video production queue | Sheets checkbox → filter view | none | — |
| Campaign end date reached | Flag "final review due" on Dashboard | Sheets conditional formatting | none | — |
| ROAS < 1.5 on any active ad | Red flag on Dashboard | Sheets formula | intraday noise — daily granularity only | — |
| Weekly | Validate all JSON records | `validate_json_records.py` cron/manual run | schema drift | Spot-check 3 records |
| Weekly | Append portfolio log from Automation Log + screenshots | `generate_portfolio_log.py` | — | Manual Evidence Log entry |

## Later Automations (Month 3+, volume-dependent)
- Zapier/Make: Shopify order → Revenue tab row (replaces weekly manual entry)
- Etsy/Pinterest listing syndication from Product Records via `export_platform_csvs.py`
- Auto-schedule content via a scheduler tool (Buffer/Later) fed from Content Calendar
- Airtable migration with linked records if Sheets strains
- TikTok/Shopify API pulls replacing manual metric entry

---

# 13. API / Script Architecture

All scripts live in `09_Automations/scripts/`. Python 3.11+, no framework, stdlib + `requests` + `jsonschema` only. Every run appends one line to `Automation_Log.md`.

**Honest MVP posture on APIs:** Shopify's Admin API is stable and worth using early *read-only*. TikTok Shop's API has onboarding friction — use **manual CSV export/import** for TikTok during MVP. Printify's API is decent but the native Shopify sync covers 95% of needs. Mailchimp API is easy but the native integrations cover MVP. **Rule: prefer native integrations > CSV > API during MVP.**

| Script | Purpose | Input | Output | Env vars | Location |
|---|---|---|---|---|---|
| `generate_product_copy.py` | Fill copy prompts from design JSON, call Claude API, save draft copy | `--design MF-DES-...` (reads JSON) | Markdown draft in `Copy_Bank/` | `ANTHROPIC_API_KEY` | scripts/ |
| `sync_product_catalog.py` | Reconcile Product Records ↔ Shopify (read-only during MVP: report drift, don't write) | Shopify Admin API + local JSONs | `drift_report.md` | `SHOPIFY_STORE`, `SHOPIFY_TOKEN` | scripts/ |
| `create_content_queue.py` | For each newly published product, emit content-post JSON stubs (reveal, mockup, push) | Product Records with recent publish_date | JSON stubs in `Posted_Archive/queue/` | none | scripts/ |
| `calculate_ad_decisions.py` | Apply §7 thresholds to ad performance JSONs | `Ad_Performance_Log/*.json` | Updated `decision`/`next_action` fields + summary table | none | scripts/ |
| `export_platform_csvs.py` | Transform Product Records into Etsy/TikTok CSV import formats | Product Records + `--platform etsy` | CSV in `04_Sales_Channels/{platform}/CSV_Exports/` | none | scripts/ |
| `validate_json_records.py` | Validate every JSON against §5 schemas; enforce price ≥ cost×2.5 | all record folders | `validation_report.md`, non-zero exit on failure | none | scripts/ |
| `generate_portfolio_log.py` | Compile weekly Evidence Log section from Automation Log, git log, screenshot folder | week number | Appended section in `Evidence_Log.md` | none | scripts/ |

**Pseudo-code, `calculate_ad_decisions.py`:**
```
for record in load_json("06_Ad_System/Ad_Performance_Log/*.json"):
    if record.spend < 15 and days_running(record) < 3: decision = "WAIT"
    elif record.ROAS > 3.0 and record.CTR >= 0.01:     decision = "PUSH"
    elif record.ROAS >= 2.0:                            decision = "ITERATE"
    elif record.ROAS >= 1.5:                            decision = "PAUSE"
    else:                                               decision = "KILL"
    record.decision = decision
    record.next_action = ACTION_TEMPLATES[decision]
    save(record); log_run()
print(summary_table)
```

**Pseudo-code, `validate_json_records.py`:**
```
schemas = load("10_API_Integrations/schemas/*.schema.json")
for folder, schema in RECORD_MAP.items():
    for f in glob(folder + "/*.json"):
        validate(f, schema)            # jsonschema
        if schema == "product" and f.price < f.cost * 2.5:
            errors.append(f"{f}: price below 2.5x floor")
write("validation_report.md"); exit(1 if errors else 0)
```

`.env.example`:
```
ANTHROPIC_API_KEY=
SHOPIFY_STORE=modfraze.myshopify.com
SHOPIFY_TOKEN=
MAILCHIMP_API_KEY=
```

---

# 14. Prompt Library

Lives in `01_Brand_System/../` — actually store at `09_Automations/prompts/` as one file per prompt. Standard placeholders: `{design_title}` `{visual_description}` `{mood_tags}` `{product_type}` `{target_audience}` `{platform}` `{price}` `{brand_voice}` `{CTA}`.

**Brand voice constant to prepend to every prompt:**
> Voice: maximalist, vivid, art-forward, witty, intelligent, slightly irreverent. Confident, never desperate. This is an artist's brand, not a discount POD shop. Forbidden: "elevate your style," "perfect gift," "must-have," "limited time only," excessive exclamation points.

1. **Product naming** — `Given this design: {visual_description} with moods {mood_tags}, generate 8 two-word product names that sound like album titles, not SEO strings. No puns on "art."`
2. **Shopify description** — `Write a 90–120 word Shopify description for {design_title} on a {product_type}. Lead with the design's story/energy ({visual_description}), one sentence on quality, end with: {CTA}. Voice: {brand_voice}.`
3. **TikTok Shop description** — `Same design, but 40 words max, first line must work standalone on mobile, casual register, one concrete visual detail from {visual_description}.`
4. **Ad hooks** — `Generate 10 TikTok hooks (max 8 words each) for {design_title} ({visual_description}) targeting {target_audience}. Mix: 3 POV, 3 pattern-interrupt, 2 question, 2 bold-claim.`
5. **TikTok video script** — `Write a 25-second script for a {content_type} video about {design_title}. Structure: hook (0–2s, on-screen text), visual beat list (2–20s), verbal CTA (20–25s): {CTA}. Voice: {brand_voice}.`
6. **Instagram caption** — `2–3 sentence caption telling the story of {design_title} ({visual_description}). End with "Link in bio." Add 5 hashtags mixing broad and niche.`
7. **Pinterest pin description** — `Keyword-rich 2-sentence description for {design_title} on {product_type}. Include: maximalist, abstract art, {product_type} keywords naturally. End with soft CTA.`
8. **Email subject lines** — `10 subject lines under 45 chars for a {body_theme} email featuring {design_title}. Mix curiosity, direct, and studio-voice. No caps-lock, max one emoji total across all ten.`
9. **Product drop email** — `Write a drop email: subject, preview text, 3 short paragraphs (the design's story, why it's one-of-a-kind, {CTA}), for segment {segment}. Voice: {brand_voice}.`
10. **Audience segmentation** — `Given these buyer behaviors: {data}, propose 3 Mailchimp segments with entry criteria and one campaign idea each.`
11. **Ad analysis** — `Here is an ad performance record: {json}. Using thresholds (push>3.0 ROAS, iterate 2–3, pause 1.5–2, kill<1.5), state the decision, the single most likely cause, and one next action.`
12. **Product performance analysis** — `Given product rows {data}, identify: best seller, best margin, worst performer, one pattern across winners, one recommendation.`
13. **Weekly founder review** — `Given this week's metrics {data} and last week's {data}, write a 10-line review: what moved, what stalled, top 3 next actions, one thing to stop doing.`
14. **Portfolio case study update** — `Given this week's Evidence Log entries {data}, write 2 case-study paragraphs in first person demonstrating systems thinking. Concrete numbers over adjectives.`

---

# 15. Brand Consistency System

**Voice rules (the five tests before publishing any copy):**
1. Would an artist say this, or a dropshipper? (Artist wins.)
2. Is there one concrete visual detail? (Required.)
3. Is it a little too confident? (Good — keep it.)
4. Does it beg? (Delete anything that begs.)
5. Could any other POD shop have written it? (If yes, rewrite.)

**Approved phrases:** "one of one" · "never repeated" · "loud on purpose" · "maximalism is a discipline" · "from the studio" · "wear the design, not the logo" · "made by a human who also builds machines"

**Forbidden clichés:** elevate your style · must-have · perfect gift for · limited time only · treat yourself · vibes (as a noun, alone) · game-changer · 🔥 in subject lines · "Don't miss out!"

**Product description tone:** the design is the protagonist; the garment is the frame. Story → one quality line → CTA. Never lead with "premium cotton."

**Visual placeholder system (until final branding):**
- **Candidate palette A (primary direction):** `#FF204E / #A0153E / #5D0E41 / #00224D` — electric crimson through wine to deep navy. Matches the maximalist-but-controlled energy.
- **Candidate palette B (alt/accent direction):** `#2FC4B2 / #12947F / #E71414 / #F17808` — teal/green vs. red/orange collision, for designs that need heat + cool tension.
- **Candidate typefaces:** **Mindset** (display — loud, condensed, poster energy), **Colby** (workhorse sans for UI/body), **ITC Franklin Gothic** (fallback classic for anything that must read as serious). Rule until finalized: display type only in Canva templates; body text is Colby or system sans everywhere; never mix more than 2 typefaces per asset.
- **Inspiration register (from reference bank):** blob/organic logotypes (Magma), glass/chrome type treatments (dirt), monochrome-field product staging (Eager), extended-width all-caps mastheads (Ragged Edge), single-color + line-illustration systems (puck), classical-collision imagery (Renaissance Edition). ModFraze sits at the intersection: *loud color fields + disciplined type*.
- **Consistency rule while branding is WIP:** every asset uses one candidate palette (never both in one asset) + one display face + Colby. Log every asset's palette choice in its record `notes` — when final branding lands, you'll know exactly what to retrofit.

---

# 16. Portfolio / Resume Builder Layer

**The habit:** 2 minutes daily — one row in Portfolio Evidence Log (date, artifact, skill demonstrated, file path). Plus one screenshot any time something works for the first time.

**What to capture:**
| Category | Specifics |
|---|---|
| Screenshots | Empty Shopify admin (before) → live store (after); first Printify sync; dashboard v1 and every weekly evolution; first TikTok Shop listing; Mailchimp flow builder; first ad decision row turning a color; first sale notification |
| Metrics | Weekly snapshot of every Dashboard KPI, even when zero — the zero-to-something curve IS the story |
| Technical decisions | Every entry in Decision_Log.md: what, options considered, why, dated |
| Automations | Automation_Log.md + script source + one before/after of manual vs. automated time cost |
| Dashboards | Weekly screenshot to `Weekly_Snapshots/`; keep v1 forever |
| Before/after | Manual product listing time vs. pipeline time; raw design vs. published product page |

**`11_Portfolio_Case_Study/` structure:** see §3 tree (Evidence_Log.md, Screenshots/WeekNN, Metrics_Snapshots, Technical_Decisions.md, Before_After, Case_Study_Draft.md).

**Case study outline — "ModFraze: Building an AI-Assisted E-Commerce System for an Independent Artist Brand":**
1. Context — artist + AI generalist, dual objective (revenue + proof-of-work)
2. Strategy — two-channel MVP thesis (owned home + rented discovery), deliberate constraint
3. Data architecture — JSON schemas, naming conventions, single-source-of-truth records (show a schema)
4. The pipeline — design-to-market in 14 steps, 72-hour cycle time (show the checklist)
5. Dashboard design — the 5-minute morning system (show weekly evolution screenshots)
6. Ad decision engineering — mechanical push/iterate/pause/kill, removing emotion from spend (show colored rows)
7. AI prompt engineering — the prompt library, human-in-the-loop copy (show prompt → output → edit)
8. Automation philosophy — manual-first, native-integrations-first, honest CSV fallbacks
9. Email + owned audience — flows and segment architecture
10. Results & experiments — real numbers, including failures, with the Experiments log
11. What I'd do differently — dated learnings from Decision_Log
12. Skills demonstrated — e-commerce strategy, data architecture, automation, dashboard design, prompt engineering, creative direction, marketing ops, solo execution

---

# 17. 30-Day MVP Build Plan

## Week 1: Foundation
- **Goal:** infrastructure exists; nothing is for sale yet and that's fine.
- **Tasks:** create folder structure + Sheet with all tabs; write Brand_Voice_Rules + naming doc; open Shopify trial, connect Printify, connect Mailchimp; apply for TikTok Shop seller (approval lags — do this Day 1); select/approve first 5 designs with JSON records; order 1 Printify sample; build welcome sequence drafts; first Evidence Log entries.
- **Deliverables:** live (unlisted) Shopify store, 5 approved design records, dashboard skeleton, welcome flow built, TikTok Shop application submitted.
- **Success criteria:** you can trace one design from raw file → JSON → dashboard row without confusion.
- **Do NOT yet:** buy ads, touch Etsy/Pinterest/Meta, write any script, obsess over logo.

## Week 2: Product Pipeline
- **Goal:** designs become products; the pipeline gets its first full reps.
- **Tasks:** run the 14-step pipeline manually for 5 products (tee + poster pairs); generate copy via prompts, edit every word; price at ≥2.5× cost; publish all 5 to Shopify; create collections; set up email popup; test full checkout; screenshot everything.
- **Deliverables:** 5 live Shopify products, Copy_Bank seeded, pricing sheet, completed pipeline checklists ×5.
- **Success criteria:** a stranger could buy a product; a second stranger could follow your checklist and list product #6.
- **Do NOT yet:** run ads, list on TikTok before seller approval clears, add product types beyond tee/poster.

## Week 3: Launch Channels
- **Goal:** TikTok Shop live; content engine running; email capturing.
- **Tasks:** publish 3 TikTok Shop listings; batch-film and post first 3 TikToks (one per listing); cross-post 1 mockup to IG (reserve handles everywhere); activate welcome sequence; announce to any existing personal audience; verbal email CTA in every video; log all content in calendar.
- **Deliverables:** 3 TT Shop listings live, 3 videos posted, welcome flow active, first subscribers.
- **Success criteria:** content cadence hit (3 videos), zero missed days on the 5-minute dashboard habit.
- **Do NOT yet:** spend on ads (organic signal first), chase follower counts, start a second content format.

## Week 4: Ads, Email, Analytics, and Review
- **Goal:** first paid test, first email send, first full review loop.
- **Tasks:** pick best-performing organic video → Spark Ad at $5–10/day; log daily ad rows; apply decision formula daily; send first studio note email; complete Revenue/Costs tabs; run week-4 founder review (prompt #13); run first `validate_json_records.py` if written, else manual audit; draft case study sections 1–3 from Evidence Log.
- **Deliverables:** one completed ad test with a recorded decision, one email sent, one written weekly review, case-study draft started.
- **Success criteria:** you made a push/iterate/pause/kill call from the formula without agonizing; the dashboard answered "what next" every morning.
- **Do NOT yet:** scale ad budget past $15/day regardless of results (data first), add channels, automate anything unproven.

---

# 18. Final Recommendations

**The simplest version to build first:** Shopify + Printify + 5 products + a one-tab spreadsheet (Products/Revenue/Content combined) + a Mailchimp form + 3 TikToks a week. Everything else in this document is scaffolding around that spine. If overwhelmed, build the spine.

**Biggest risks:**
1. **Channel sprawl** — the deferred list is a graveyard of momentum. 30 days, two channels, no exceptions.
2. **Content drought** — TikTok Shop without 3 videos/week is a dead listing page. Content is not optional marketing; it IS the channel.
3. **Ad emotion** — spending to "give it a chance." The formula decides; you execute.
4. **Perfection stall** — waiting on final branding to launch. Candidate palettes and placeholder rules exist precisely so you can ship now.
5. **Retroactive portfolio** — if evidence isn't captured daily, it never gets captured. Two minutes, every day.
6. **Technical rabbit holes** — you like building tools (see: listing generator). During MVP, tools serve listings, not the reverse.

**Highest-leverage first actions:** TikTok Shop application (longest external dependency), Printify sample order (quality is your reputation), and the dashboard skeleton (the habit starts on day one, not when there's data).

**The exact first 10 tasks:**
1. Create `ModFraze_MVP_OS/` folder tree (30 min)
2. Create the Google Sheet with all 18 tabs, columns only (60 min)
3. Apply for TikTok Shop seller account (30 min)
4. Open Shopify, connect Printify (45 min)
5. Connect Mailchimp to Shopify, build signup form (30 min)
6. Select 5 launch designs; write their JSON records (90 min)
7. Write Brand_Voice_Rules.md + forbidden/approved lists (45 min)
8. Order one Printify tee sample of your strongest design (15 min)
9. Draft welcome email 1 of 3 (30 min)
10. Make today's first Portfolio Evidence Log entry — screenshot the empty store (5 min)

**First dashboard to build:** the **Dashboard tab** itself — even mostly empty. The morning habit precedes the data.

**First automation to build:** Printify → Shopify native sync (zero code, immediate leverage). First *scripted* automation: `validate_json_records.py` — it protects everything downstream.

**First product drop structure to test:** "**Vol. 1: five one-of-one designs, tee + poster each.**" One collection, one drop email, one reveal video per design across two weeks, one Spark Ad on the organic winner. Measure which *design* wins, not which product type — designs are your real inventory.

---
*End of document. Revise thresholds, cadences, and scope in Decision_Log.md as reality reports back.*
