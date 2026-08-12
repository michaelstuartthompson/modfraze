# 🚀 Viral Merch Pipeline

Automated pipeline for identifying viral trends and converting them into print-on-demand merchandise with intelligent ad management.

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Workflows](#workflows)
- [API Costs](#api-costs)
- [Roadmap](#roadmap)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREFECT ORCHESTRATION                         │
│              (Scheduled Workflows + Monitoring)                  │
└──────────────────┬──────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌────────────┐
│ TREND   │  │ DESIGN   │  │ COMMERCE & │
│ MONITOR │─>│ PIPELINE │─>│ AD MGMT    │
└─────────┘  └──────────┘  └────────────┘
    │              │              │
    ▼              ▼              ▼
[Trends DB]   [Designs DB]  [Campaigns DB]
```

### Pipeline Stages

1. **Trend Detection** (Every 4 hours)
   - Scrape Reddit, TikTok, Twitter
   - Calculate virality scores
   - Store top trends in database

2. **Design Generation** (Every 6 hours)
   - Generate designs for high-scoring trends using DALL-E 3
   - Create product mockups
   - Queue for human approval

3. **Human Approval** (Continuous)
   - Streamlit dashboard for design review
   - Approve, reject, or request regeneration
   - Add feedback notes

4. **Product Creation** (On approval)
   - Upload designs to Printify
   - Create Shopify product listings
   - Generate product descriptions

5. **Ad Management** (Every 6 hours)
   - Launch Meta Ads campaigns
   - Monitor performance metrics
   - Auto-kill low performers (CTR < 0.5%, 12+ hours)
   - Auto-boost winners (CTR > 2%)

## ✨ Features

- **Multi-Platform Trend Monitoring**
  - Reddit via PRAW
  - TikTok via Apify
  - Twitter via Apify
  - Extensible for Instagram, Facebook

- **AI-Powered Design Generation**
  - DALL-E 3 integration
  - Customizable prompts and styles
  - Design variations for A/B testing

- **Human-in-the-Loop Workflow**
  - Streamlit approval dashboard
  - Design review and feedback
  - Quality control before production

- **E-Commerce Automation**
  - Shopify API integration
  - Printify POD fulfillment
  - Automated product listing

- **Intelligent Ad Management**
  - Meta Ads API integration
  - Performance-based optimization
  - Auto-kill underperformers
  - Auto-boost high performers

- **Workflow Orchestration**
  - Prefect Cloud scheduling
  - Error handling and retries
  - Monitoring and alerts

## 📦 Prerequisites

- Python 3.9+
- Shopify store
- Printify account
- Meta Business Manager account
- OpenAI API key
- Apify account (for TikTok/Twitter)

## 🔧 Installation

### 1. Clone and Setup

```bash
# Clone repository
git clone <your-repo-url>
cd viral-merch-pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env  # or your preferred editor
```

### 3. Initialize Database

```bash
# Create database tables
python db/database.py
```

### 4. Verify Setup

```bash
# Test trend scraping
python pipeline/ingest_tiktok.py

# Test design generation (requires trends in DB)
python pipeline/generate_designs.py top 1

# Test database
python pipeline/read_trends.py
```

## ⚙️ Configuration

### Required API Keys

See `.env.example` for all required environment variables.

**Priority 1 (MVP):**
- `OPENAI_API_KEY` - DALL-E design generation
- `APIFY_API_KEY` - TikTok/Twitter scraping
- `SHOPIFY_SHOP_NAME` + `SHOPIFY_ACCESS_TOKEN`
- `PRINTIFY_API_KEY` + `PRINTIFY_SHOP_ID`

**Priority 2 (Full Automation):**
- `META_ACCESS_TOKEN` + `META_AD_ACCOUNT_ID` + `META_PAGE_ID`

**Optional:**
- `SENDGRID_API_KEY` - Email notifications
- `SLACK_WEBHOOK_URL` - Slack notifications
- `PREFECT_API_KEY` - Prefect Cloud scheduling

### Obtaining API Keys

#### OpenAI
1. Sign up at https://platform.openai.com
2. Navigate to API keys
3. Create new secret key
4. Add to `.env` as `OPENAI_API_KEY`

#### Apify
1. Sign up at https://apify.com
2. Go to Settings > Integrations
3. Copy API token
4. Add to `.env` as `APIFY_API_KEY`

#### Shopify
1. In Shopify admin: Apps > Develop apps
2. Create app
3. Configure Admin API scopes (products, inventory)
4. Install app and copy access token
5. Add shop name and token to `.env`

#### Printify
1. Sign up at https://printify.com
2. Settings > Connections > API
3. Generate API key
4. Get shop ID from account URL
5. Add both to `.env`

#### Meta Ads
1. Create Meta Business account
2. Create Facebook Page
3. Create ad account
4. Generate access token (Settings > Business integrations)
5. Add all IDs to `.env`

## 🚀 Usage

### Running Individual Components

```bash
# Scrape trends
python pipeline/ingest_tiktok.py

# Generate designs for top 5 trends
python pipeline/generate_designs.py top 5

# Start approval dashboard
streamlit run ui/approval_dashboard.py

# Monitor campaigns
python pipeline/manage_campaigns.py monitor
```

### Running Orchestrated Workflows

```bash
# Run full daily pipeline once
python workflows/prefect_flows.py run daily

# Run individual flows
python workflows/prefect_flows.py run trends
python workflows/prefect_flows.py run designs
python workflows/prefect_flows.py run campaigns

# Deploy to Prefect Cloud (automated scheduling)
python workflows/prefect_flows.py deploy
```

### Approval Dashboard

```bash
# Start Streamlit dashboard
streamlit run ui/approval_dashboard.py

# Open browser to http://localhost:8501
# Review pending designs
# Approve/reject/regenerate
```

## 📁 Project Structure

```
viral-merch-pipeline/
├── db/                          # Database layer
│   ├── models.py                # SQLAlchemy models
│   ├── database.py              # DB connection
│   └── __init__.py
├── schemas/                     # Data schemas
│   ├── trend.py                 # Trend signal schema
│   ├── design.py                # Design schemas
│   ├── product.py               # Product schemas
│   └── __init__.py
├── tools/                       # API clients
│   ├── dalle_client.py          # DALL-E 3 wrapper
│   ├── shopify_client.py        # Shopify API
│   ├── printify_client.py       # Printify API
│   ├── meta_ads_client.py       # Meta Ads API
│   ├── tiktok_adapter.py        # TikTok scraper (Apify)
│   └── __init__.py
├── pipeline/                    # Pipeline modules
│   ├── ingest_tiktok.py         # TikTok trend scraping
│   ├── ingest_one_demo.py       # Demo data insertion
│   ├── generate_designs.py      # Design generation
│   ├── manage_campaigns.py      # Campaign management
│   ├── read_trends.py           # View trends utility
│   ├── run_daily.py             # Daily orchestration
│   └── __init__.py
├── workflows/                   # Prefect workflows
│   ├── prefect_flows.py         # Flow definitions
│   └── __init__.py
├── ui/                          # User interfaces
│   ├── approval_dashboard.py    # Streamlit approval UI
│   └── __init__.py
├── generated_designs/           # Output directory for designs
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🔄 Workflows

### Trend Detection Flow
- **Schedule:** Every 4 hours
- **Tasks:**
  1. Scrape TikTok trending videos
  2. Scrape Reddit hot posts
  3. Scrape Twitter trending tweets
  4. Calculate virality scores
  5. Store in database

### Design Generation Flow
- **Schedule:** Every 6 hours
- **Tasks:**
  1. Query top trends (virality > 0.6)
  2. Generate DALL-E designs
  3. Create mockups
  4. Store with pending approval status
  5. Send notification

### Campaign Monitoring Flow
- **Schedule:** Every 6 hours
- **Tasks:**
  1. Sync metrics from Meta Ads API
  2. Check performance thresholds
  3. Kill campaigns with CTR < 0.5% after 12h
  4. Boost campaigns with CTR > 2%
  5. Log decisions

### Daily Master Flow
- **Schedule:** 8am daily
- **Tasks:**
  1. Run trend detection
  2. Run design generation
  3. Run campaign monitoring
  4. Send daily summary

## 💰 API Costs

### Monthly Budget Breakdown

**Social Monitoring ($35/month):**
- Apify TikTok: $15
- Apify Twitter: $20
- Reddit PRAW: Free

**Design Generation ($3-5/month):**
- DALL-E 3: $0.04/image
- 75-100 designs/month = $3-4

**E-Commerce (Free):**
- Shopify API: Included
- Printify API: Free (pay per product sold)

**Ads Platform (Free):**
- Meta Ads API: Free

**Total: ~$38-40/month** (excluding ad spend)

**Ad Spend Budget:** $100-150/month (recommended starting point)

## 🗺️ Roadmap

### Phase 1: MVP (Weeks 1-3) ✅
- [x] Database schema
- [x] DALL-E design generation
- [x] Streamlit approval UI
- [x] Shopify integration
- [x] Basic Prefect workflows

### Phase 2: Multi-Platform (Weeks 4-6)
- [ ] Complete TikTok scraper
- [ ] Add Twitter scraper
- [ ] Add Instagram scraper
- [ ] Unified trend scoring
- [ ] Scheduled automation

### Phase 3: Ad Automation (Weeks 7-10)
- [ ] Meta Ads campaign creation
- [ ] Performance monitoring
- [ ] Auto-kill logic
- [ ] Auto-boost logic
- [ ] Budget management

### Phase 4: Optimization (Weeks 11+)
- [ ] A/B testing framework
- [ ] Historical performance analysis
- [ ] Design style learning
- [ ] Multi-product expansion
- [ ] Revenue analytics

## 🤝 Contributing

This is a personal learning project, but suggestions and feedback are welcome!

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Anthropic Claude for architecture guidance
- OpenAI for DALL-E 3
- Prefect for workflow orchestration
- Streamlit for rapid UI development

---

**Built with ❤️ as a learning project and portfolio piece**
