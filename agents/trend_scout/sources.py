"""
sources.py -- one adapter per platform. Each returns list[Signal].

DESIGN RULE
-----------
Adapters are dumb pipes. They fetch and normalize. They never judge,
never rank, never call an LLM. If a source is down, the adapter returns
[] and logs -- it does NOT crash the run. A trend scout that dies because
Reddit rate-limited you is a trend scout you stop running.

Only the stdlib is used so this runs anywhere with zero install.
"""

from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from signals import Signal

UA = "ModFraze-TrendScout/0.1 (personal research; contact michaelstuartthompson1@gmail.com)"
TIMEOUT = 20
_CTX = ssl.create_default_context()


def _get(url: str, headers: dict | None = None) -> str | None:
    hdrs = {"User-Agent": UA}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=_CTX) as r:
            return r.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as e:
        print(f"  [warn] {url.split('/')[2]} unavailable: {e}")
        return None


# ---------------------------------------------------------------------------
# FREE, NO API KEY
# ---------------------------------------------------------------------------

def google_trends(geo: str = "US") -> list[Signal]:
    """Google's daily trending searches, published as a public RSS feed."""
    raw = _get(f"https://trends.google.com/trending/rss?geo={geo}")
    if not raw:
        return []
    out: list[Signal] = []
    try:
        root = ET.fromstring(raw)
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            if not title:
                continue
            traffic = (item.findtext("{https://trends.google.com/trending/rss}approx_traffic") or "0")
            out.append(Signal(
                platform="google_trends",
                text=title,
                url=(item.findtext("link") or "").strip(),
                score=float("".join(c for c in traffic if c.isdigit()) or 0),
                meta={"approx_traffic": traffic},
            ))
    except ET.ParseError as e:
        print(f"  [warn] google_trends parse failed: {e}")
    return out


def hackernews(pages: int = 2) -> list[Signal]:
    """HN via the free Algolia index. Early signal for tools and tech memes."""
    out: list[Signal] = []
    for page in range(pages):
        raw = _get(
            "https://hn.algolia.com/api/v1/search_by_date"
            f"?tags=story&hitsPerPage=100&page={page}"
        )
        if not raw:
            break
        for hit in json.loads(raw).get("hits", []):
            if not hit.get("title"):
                continue
            out.append(Signal(
                platform="hackernews",
                text=hit["title"],
                url=f"https://news.ycombinator.com/item?id={hit['objectID']}",
                score=float(hit.get("points") or 0),
            ))
    return out


def web_news(extra_queries: list[str] | None = None) -> list[Signal]:
    """
    Google News RSS. No key, no signup, no rate limit worth worrying about.

    Two kinds of feed are pulled, for two different reasons:

    1. TOPIC feeds -- broad coverage of what the press is talking about at all.
    2. TREND-COVERAGE searches -- queries like "tiktok trend" or "gen z slang".
       TikTok and Instagram are closed to us by policy, but what happens there
       gets *written about* within days. This is a lagging, second-hand view of
       those platforms. It is not a substitute for them and should not be
       mistaken for one -- by the time a phrase is in a headline it is later in
       its life than the 2-8 week pre-peak window we want. Treat it as a
       backstop, not a source.

    Everything returns platform="web_news" -- deliberately ONE platform, even
    though it spans many outlets. Cross-platform breadth is the core signal in
    scoring.py, and letting one adapter masquerade as several would inflate the
    exact number the whole system is built to trust.
    """
    base = "https://news.google.com/rss"
    tail = "hl=en-US&gl=US&ceid=US:en"

    topics = ["TECHNOLOGY", "BUSINESS", "ENTERTAINMENT"]
    queries = extra_queries or [
        "tiktok trend", "viral phrase", "gen z slang",
        "internet trend", "goes viral", "new aesthetic",
    ]

    feeds = [f"{base}/headlines/section/topic/{t}?{tail}" for t in topics]
    feeds += [
        f"{base}/search?q={urllib.parse.quote(q)}%20when%3A7d&{tail}"
        for q in queries
    ]

    out: list[Signal] = []
    seen: set[str] = set()

    for url in feeds:
        raw = _get(url)
        if not raw:
            continue
        try:
            root = ET.fromstring(raw)
        except ET.ParseError as e:
            print(f"  [warn] web_news parse failed: {e}")
            continue

        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            if not title:
                continue

            # Google appends " - Publisher" to every headline. Left in, outlet
            # names become high-frequency terms and drown the actual signal.
            source_el = item.find("source")
            outlet = (source_el.text or "").strip() if source_el is not None else ""
            if outlet and title.endswith(f" - {outlet}"):
                title = title[: -len(outlet) - 3].strip()
            elif " - " in title:
                title = title.rsplit(" - ", 1)[0].strip()

            key = title.lower()
            if not title or key in seen:
                continue
            seen.add(key)

            out.append(Signal(
                platform="web_news",
                text=title,
                url=(item.findtext("link") or "").strip(),
                # RSS gives no popularity number. 0.0 is honest; scoring.py
                # weights by cross-platform breadth anyway, and a fake score
                # here would quietly outrank sources that report a real one.
                score=0.0,
                meta={"outlet": outlet, "published": item.findtext("pubDate") or ""},
            ))

    return out


# ---------------------------------------------------------------------------
# PAID -- costs real money per post read. Read the cost note before editing.
# ---------------------------------------------------------------------------

# X charges per POST RETURNED, not per request. A single max_results=100 call
# costs 50 cents. There is no server-side popularity filter -- min_faves and
# min_likes are silently ignored by API v2, so you cannot ask for "only good
# posts" and you pay the same for a viral phrase and someone's reply guy.
#
# Query precision is therefore the ONLY cost control, which is why the default
# query below hunts linguistic frames rather than topics. People wrap a new
# phrase in explanation while it is still spreading -- "is the new", "everyone
# is calling it" -- and that explaining is the pre-peak window we want. A topic
# keyword would return ten times the volume at a tenth the relevance and cost
# the same per post.

X_COST_PER_POST = 0.005

X_DEFAULT_QUERY = (
    '("is the new" OR "everyone is calling it" OR "everyone\'s calling it" '
    'OR "apparently it\'s called" OR "the term for this" OR "what do you call it when") '
    "-is:retweet -is:reply -is:quote lang:en"
)


def x_search(query: str | None = None, max_posts: int | None = None) -> list[Signal]:
    """
    X recent search (last 7 days) via app-only bearer auth.

    Costs money. The cap is enforced BEFORE each request, not after, so a
    pagination bug cannot run up a bill -- the worst case is one extra page.
    Override the budget with X_MAX_POSTS in .env.
    """
    token = os.environ.get("X_BEARER_TOKEN", "").strip()
    if not token:
        print("  [skip] x: no X_BEARER_TOKEN in .env")
        return []

    try:
        cap = int(max_posts or os.environ.get("X_MAX_POSTS", "200"))
    except ValueError:
        print("  [warn] x: X_MAX_POSTS is not a number, falling back to 200")
        cap = 200
    cap = max(0, min(cap, 1000))          # 1000 = $5.00, a deliberate ceiling
    if cap == 0:
        print("  [skip] x: X_MAX_POSTS is 0")
        return []

    q = query or X_DEFAULT_QUERY
    headers = {"Authorization": f"Bearer {token}"}
    out: list[Signal] = []
    next_token = None
    fetched = 0

    while fetched < cap:
        want = min(100, cap - fetched)
        if want < 10:                      # API minimum is 10; stop rather
            break                          # than overshoot the budget

        url = (
            "https://api.x.com/2/tweets/search/recent"
            f"?query={urllib.parse.quote(q)}"
            f"&max_results={want}"
            "&tweet.fields=public_metrics,created_at,lang"
        )
        if next_token:
            url += f"&next_token={next_token}"

        raw = _get(url, headers=headers)
        if not raw:
            break                          # _get already logged the reason

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"  [warn] x: bad JSON: {e}")
            break

        if "errors" in payload and not payload.get("data"):
            detail = payload["errors"][0].get("detail") or payload["errors"][0]
            print(f"  [warn] x: {detail}")
            break

        posts = payload.get("data") or []
        if not posts:
            break

        for p in posts:
            metrics = p.get("public_metrics") or {}
            out.append(Signal(
                platform="x",
                text=p.get("text", "").replace("\n", " ").strip(),
                url=f"https://x.com/i/status/{p.get('id')}",
                score=float(metrics.get("like_count", 0)),
                meta={
                    "reposts": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "created_at": p.get("created_at", ""),
                },
            ))
        fetched += len(posts)

        next_token = (payload.get("meta") or {}).get("next_token")
        if not next_token:
            break

    if fetched:
        print(f"  [cost] x: {fetched} posts read ~ ${fetched * X_COST_PER_POST:.2f}")
    return out


# ---------------------------------------------------------------------------
# FREE, BUT NEEDS AN APPROVED KEY
# ---------------------------------------------------------------------------

# Etsy is the only source here that measures MONEY rather than attention.
# Every other adapter tells you people are saying a phrase. Etsy tells you
# somebody thought the phrase was worth printing on a product -- which is a
# much stronger signal for a merch brand, and a much harsher one. A term that
# is loud on X and absent on Etsy is an opportunity. A term with 4,000 active
# listings is a market you are late to.
#
# Two different questions, so two modes:
#   etsy()              -> discovery. Newest listings, no keyword. "What are
#                          sellers printing THIS WEEK?" This is what collect()
#                          calls, because it needs a no-argument callable.
#   etsy_saturation(t)  -> confirmation. How many active listings already
#                          exist for one term. Not in SOURCES; it is meant to
#                          become an agent tool, so the model can ask "am I
#                          too late?" about a specific candidate.
#
# Auth is a plain app key in a header -- no OAuth, no user consent, because
# active public listings are not user data. Getting the key is the slow part:
# Etsy requires a Personal App application that is reviewed by a human, and
# approval has been reported to take anywhere from two days to several months.
# Apply before you need it.
#
# Etsy's API Terms of Use section 1 requires you to cache responses rather
# than re-request the same data. Running this once a day, as the scheduler
# does, is comfortably inside that. Do not put it in a loop.

ETSY_API = "https://openapi.etsy.com/v3/application/listings/active"
ETSY_PAGE = 100                 # API maximum listings per request

# RATE LIMIT -- read this before raising anything.
#
# An UNAPPROVED app gets 5 queries/second and 5 queries/DAY. Five. Per day.
# That is a smoke-test allowance, not a working budget, and it is the reason
# the request cap below defaults to 1 rather than to something sensible: one
# discovery request per run leaves four for probes and saturation checks.
#
# An approved app gets 10/second and 10,000/day, at which point 5-10 requests
# per run is comfortable. Raise ETSY_MAX_REQUESTS in .env when you're approved
# -- do NOT raise it before, or the daily collect will burn the quota at 6am
# and every later call that day fails.
ETSY_DEFAULT_MAX_REQUESTS = 1


def _etsy_key() -> str:
    return os.environ.get("ETSY_KEYSTRING", "").strip()


def _etsy_page(params: dict) -> dict | None:
    """One request. Returns the decoded payload, or None if anything failed."""
    url = f"{ETSY_API}?{urllib.parse.urlencode(params)}"
    raw = _get(url, headers={"x-api-key": _etsy_key()})
    if not raw:
        return None                       # _get already logged the reason
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"  [warn] etsy: bad JSON: {e}")
        return None


def _etsy_signal(listing: dict) -> Signal:
    """One active listing -> one Signal.

    text is the TITLE ONLY, deliberately. It is tempting to append the tags,
    but extract_terms builds n-grams across whatever you hand it, so a title
    glued to a tag list invents phrases like "mug funny" that nobody wrote.
    Tags go in meta instead, where a future saturation tool can read them
    without polluting the term counts.
    """
    price = listing.get("price") or {}
    amount, divisor = price.get("amount"), price.get("divisor") or 100
    return Signal(
        platform="etsy",
        text=(listing.get("title") or "").strip(),
        url=listing.get("url") or "",
        # Favourites, not views or sales -- it is the only demand number Etsy
        # exposes publicly, and on a NEW listing it is close to zero by
        # definition. Cross-platform breadth is doing the real work in
        # scoring.py; this is a tiebreaker, not a verdict.
        score=float(listing.get("num_favorers") or 0),
        meta={
            "listing_id": listing.get("listing_id"),
            "shop_id": listing.get("shop_id"),
            "tags": listing.get("tags") or [],
            "taxonomy_id": listing.get("taxonomy_id"),
            "created": listing.get("created_timestamp"),
            "price": round(amount / divisor, 2) if amount is not None else None,
            "currency": price.get("currency_code"),
        },
    )


def etsy(max_listings: int | None = None) -> list[Signal]:
    """
    Newest active listings, most recent first.

    Sorting by `created` rather than `score` is the whole point. Etsy's own
    relevance ranking surfaces what sells WELL, which is by definition
    established and therefore too late for us. The newest listings are sellers
    placing bets, and a phrase suddenly appearing across many new listings is
    the merch market reacting to something -- often days before it peaks.
    """
    if not _etsy_key():
        print("  [skip] etsy: no ETSY_KEYSTRING in .env")
        return []

    # The binding constraint is REQUESTS, not listings. Budget in requests and
    # derive the listing count from it, the same way x_search budgets in posts
    # -- checked before each call, so a paging bug costs one extra request at
    # worst rather than the whole day's quota.
    try:
        max_requests = int(os.environ.get(
            "ETSY_MAX_REQUESTS", str(ETSY_DEFAULT_MAX_REQUESTS)))
    except ValueError:
        print("  [warn] etsy: ETSY_MAX_REQUESTS is not a number, using 1")
        max_requests = 1
    max_requests = max(0, min(max_requests, 50))
    if max_requests == 0:
        print("  [skip] etsy: ETSY_MAX_REQUESTS is 0")
        return []

    try:
        cap = int(max_listings or os.environ.get("ETSY_MAX_LISTINGS", "100"))
    except ValueError:
        print("  [warn] etsy: ETSY_MAX_LISTINGS is not a number, using 100")
        cap = 100
    cap = min(max(0, cap), max_requests * ETSY_PAGE)
    if cap == 0:
        print("  [skip] etsy: ETSY_MAX_LISTINGS is 0")
        return []

    # Optional: restrict to categories you actually print. Find the ids at
    # /v3/application/seller-taxonomy/nodes -- they are stable integers.
    # Comma-separate them in .env, e.g. ETSY_TAXONOMY_IDS=1027,69
    #
    # Each taxonomy costs its own request, so with a 5/day quota keep this to
    # one id, or leave it blank and filter later.
    taxonomies = [t.strip() for t in
                  os.environ.get("ETSY_TAXONOMY_IDS", "").split(",") if t.strip()]

    out: list[Signal] = []
    seen: set[int] = set()
    requests_used = 0

    for taxonomy in (taxonomies or [None]):
        offset = 0
        while len(out) < cap:
            if requests_used >= max_requests:      # checked BEFORE the call
                break

            params = {
                "limit": min(ETSY_PAGE, cap - len(out)),
                "offset": offset,
                "sort_on": "created",
                "sort_order": "desc",
            }
            if taxonomy:
                params["taxonomy_id"] = taxonomy

            payload = _etsy_page(params)
            requests_used += 1
            if payload is None:
                break

            if payload.get("error"):
                print(f"  [warn] etsy: {payload['error']}")
                break

            results = payload.get("results") or []
            if not results:
                break

            for listing in results:
                lid = listing.get("listing_id")
                if lid in seen:           # offset paging can repeat rows when
                    continue              # new listings land mid-crawl
                seen.add(lid)
                sig = _etsy_signal(listing)
                if sig.text:
                    out.append(sig)

            offset += len(results)
            if len(results) < params["limit"]:
                break                     # short page = end of results

        if requests_used >= max_requests:
            break

    if requests_used:
        print(f"  [quota] etsy: {requests_used} request(s) used "
              f"(unapproved apps get 5/day)")
    return out


def etsy_saturation(term: str) -> dict:
    """
    How crowded is this term already? Intended as an agent tool, not a source.

    Returns the active listing count plus a few of the top sellers' titles,
    so the model can distinguish "nobody has made this yet" from "there are
    six thousand of these and the top one has 900 favourites."
    """
    if not _etsy_key():
        return {"term": term, "error": "no ETSY_KEYSTRING configured"}

    payload = _etsy_page({
        "keywords": term,
        "limit": 10,
        "sort_on": "score",               # here we DO want the best sellers
        "sort_order": "desc",
    })
    if payload is None:
        return {"term": term, "error": "etsy request failed"}

    results = payload.get("results") or []
    count = payload.get("count", 0)
    return {
        "term": term,
        "active_listings": count,
        "verdict": (
            "wide open -- nobody is selling this phrasing yet" if count < 25 else
            "early -- a few sellers, room to differentiate" if count < 250 else
            "competitive -- you would need a strong visual angle" if count < 2500 else
            "saturated -- this market is established, expect to be ignored"
        ),
        "top_listings": [
            {
                "title": r.get("title"),
                "favorers": r.get("num_favorers"),
                "url": r.get("url"),
            }
            for r in results[:5]
        ],
    }


# ---------------------------------------------------------------------------
# EXTENSION POINTS -- these need credentials you don't have yet.
# ---------------------------------------------------------------------------
# Each one is a stub with the same signature as the working adapters. When you
# get a key, fill in the body and add it to SOURCES below. Nothing else in the
# system has to change. That is the entire payoff of the Signal abstraction.
#
#   tiktok()    -> closed. Research API is academic/non-profit only and
#                  commercial use is explicitly excluded. Not a coding problem.
#   reddit()    -> removed. Self-service API registration closed in 2026 and
#                  commercial use needs written approval, which this project
#                  does not have. The adapter is in git history if that ever
#                  changes; it is not carried in the tree as dead weight.
#   amazon()    -> no free API. Movers & Shakers pages are scrapable but
#                  against ToS; consider Keepa or Jungle Scout instead.
#   instagram() -> Graph API, business account required. Low signal for
#                  emerging text trends; deprioritize.

def _not_configured(name: str):
    def _stub(*_a, **_k) -> list[Signal]:
        print(f"  [skip] {name} not configured yet")
        return []
    return _stub


tiktok = _not_configured("tiktok")
amazon = _not_configured("amazon")


# ---------------------------------------------------------------------------

SOURCES = {
    "google_trends": google_trends,
    "hackernews": hackernews,
    "web_news": web_news,
    "etsy": etsy,
    "x": x_search,
    "tiktok": tiktok,
}


def collect(names: list[str] | None = None) -> list[Signal]:
    """Run every requested adapter and return one flat list of Signals."""
    names = names or list(SOURCES)
    signals: list[Signal] = []
    for name in names:
        fn = SOURCES.get(name)
        if not fn:
            print(f"  [warn] unknown source '{name}'")
            continue
        got = fn()
        print(f"  {name:16s} {len(got):4d} signals")
        signals.extend(got)
    return signals


def demo_signals() -> list[Signal]:
    """
    Fixture data so you can watch the whole pipeline work with no network
    and no API keys. Always build one of these. It makes the system testable
    and it makes your logic bugs distinguishable from your API bugs.
    """
    fixture = [
        ("google_trends", "quiet cracking workplace", 20000),
        ("x", "Anyone else experiencing quiet cracking at their job?", 4100),
        ("x", "My manager called it quiet cracking and I lost it", 2200),
        ("hackernews", "Quiet cracking: the burnout nobody names", 180),
        ("x", "The rise of the beige flag in dating", 900),
        ("google_trends", "beige flag meaning", 50000),
        ("hackernews", "Show HN: I built a local-first note app", 240),
        ("web_news", "Show HN style launches are getting out of hand", 60),
        ("google_trends", "nfl scores", 200000),
        ("web_news", "Weekly discussion thread", 30),
        ("x", "Loud budgeting is the new quiet luxury", 7800),
        ("google_trends", "loud budgeting", 20000),
        ("hackernews", "Loud budgeting and the economics of saying no", 95),
        # Etsy rows exist so the demo shows the ASYMMETRY that makes this
        # source worth having. "loud budgeting" is already on merch -- three
        # sellers got there first. "quiet cracking" is loud everywhere else
        # and absent here. That gap is the whole thesis of the brand.
        ("etsy", "Loud Budgeting Tote Bag Funny Finance Gift", 41),
        ("etsy", "Loud Budgeting Sweatshirt Money Saving Era", 12),
        ("etsy", "Loud Budgeting Mug Broke But Honest", 3),
        ("etsy", "Beige Flag Dating Sticker Pack", 7),
    ]
    return [
        Signal(platform=p, text=t, score=float(s), url="https://example.test")
        for p, t, s in fixture
    ]
