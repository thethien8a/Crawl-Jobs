# LinkedIn Collection Plan (Public Jobs Panel)

## 🎯 Goal
- Collect job data from LinkedIn Jobs search results without login by clicking each job in the left list and extracting details from the right-side panel.
- Integrate into existing pipeline (dedup/upsert) with `source_site = 'linkedin.com'`.

## 🔍 Source
- Listing URL example: https://www.linkedin.com/jobs/search?keywords=Data%20Analyst&location=Vietnam
- Behavior: When clicking a job on the left list, a detail panel appears on the right with Job Description, Requirements, company, location, etc.

## 🏗️ Architecture
- Spider: `linkedin_spider.py` (uses Selenium for dynamic interactions)
- Mode: Single page with iterative clicks; light pagination (Next button) for N pages
- Output: `JobItem` → existing `SQLServerPipeline` (dedup by `(source_site, job_url)`, upsert w/ `updated_at`)

## 📦 Data Mapping → JobItem
- job_title: panel header (e.g., h2/h3 in top card)
- company_name: link/text near title
- salary: likely absent; leave empty or infer if present
- location: text near org (e.g., "Ho Chi Minh City, Vietnam")
- job_type / experience_level / job_position / job_industry / education_level: best-effort, may be empty
- job_description: text from right panel (section "Job Description" and below)
- requirements: section "Requirements" if present (fallback: part of description)
- benefits: section "Benefits" if present
- job_deadline: N/A (empty)
- job_url: from left list anchor (href) or current URL if navigates
- source_site: `linkedin.com`
- search_keyword: input keyword
- scraped_at: ISO timestamp

## 🧭 Selectors (baseline, may need adjustment)
- Left list items: list of anchors with job titles (e.g., `main ul li a[href*="/jobs/view/"]`)
- Right panel title: `main h2` or heading within top card
- Right panel description blocks: strong/text blocks after "Job Description"; gather following text nodes
- Fallback: collect all text under the right panel content container

## 🦾 Anti-bot & Stability
- Delays: random 2–5s between clicks
- Scroll: ensure the list is scrolled to load more items
- User-Agent: use mobile/desktop UA already set in settings; consider rotating if rate-limited
- Headless: enable; set viewport size large enough (e.g., 1366x900)
- Retries: if panel fails, retry clicking once; if still fails, skip item

## 🔁 Pagination Strategy
- Look for `a[rel="next"]` or a next-button; click and repeat up to `_max_pages` (e.g., 3–5)
- Safeguard against infinite loops by tracking current page index

## 🔌 Integration Steps
1) Create `CrawlJob/spiders/linkedin_spider.py` using Selenium (or enable `SeleniumMiddleware` only for this spider)
2) Implement: open search URL, wait for list, iterate items:
   - get anchor href for `job_url`
   - click item → wait panel updated → extract fields
   - yield `JobItem`
3) Pagination up to `_max_pages`
4) Wire into `run_spider.py` choices (`linkedin`, `all`)
5) Update `README.md` with usage examples and notes (dynamic site, best-effort)

## ✅ Acceptance Criteria
- Crawl ≥ 50 jobs/keyword (subject to availability)
- Majority of items contain title, company, location, and description text
- No duplicates across repeated runs due to pipeline dedup/upsert

## 🧪 Testing Plan
- Manual run with `--keyword "Data Analyst"` and verify items persisted
- Re-run immediately to confirm upsert (no duplicate rows)
- Spot-check description text quality and encoding

## ⚠️ Legal & TOS
- Use only public pages; respect LinkedIn’s Terms of Service and robots policies
- Introduce delays and avoid aggressive crawling; consider consent and compliance requirements

## ⏱️ Timeline (est.)
- Spider (Selenium) & wiring: 1.5–2 hours
- README docs and basic tuning: 30–45 minutes
- Stabilization (selectors/anti-bot tweaks): iterative as needed

## 📌 Notes
- LinkedIn UI changes frequently; encapsulate selectors in helper methods and provide fallbacks
- If content requires login, skip gracefully and continue
