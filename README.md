# BrandShield AI

Explainable brand governance for the TECHCIRCUIT Hackathon — Team GRUMPYBOT.

A working Streamlit + Python + SQLite MVP based on the supplied project overview. It checks draft text against a selected brand profile, explains findings using configured approved sources, supports focused edits and comments, and routes submissions through a human approval workflow.

## Run on Windows

Install Python 3.11 or newer, extract this ZIP, and open a terminal in the `brandshield` folder.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe demo.py
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the localhost URL printed in the terminal (normally http://localhost:8501).

## Run on macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python demo.py
.venv/bin/python -m streamlit run app.py
```

On a fresh database, the app creates fictional demo accounts and sample reviews automatically so the login page is ready immediately. It never seeds demo accounts into a database that already contains users. For real deployment, replace demo credentials with managed account setup before exposing the app publicly.

## Demo sign-ins

| Username | Password | Role |
| --- | --- | --- |
| creator | BrandShield!2026 | Create, revise and submit own reviews |
| reviewer | BrandShield!2026 | Inspect reviews, comment, approve or request changes |
| manager | BrandShield!2026 | Configure profiles and review submissions |
| admin | AdminDemo!2026 | Manage users and profiles; create and review content |

These publicly documented credentials are only for a local fictional hackathon demo. Do not expose this demo configuration to the public internet. A user cannot approve their own submission, including an administrator.

## Demonstration walkthrough

1. Run `demo.py`; sign in as `creator`.
2. Open **Reviews** and select the seeded October energy campaign.
3. Inspect the claim conflict: 50% savings exceeds the configured maximum of 15%. The card shows the exact approved source, qualifications and explanation.
4. Apply focused terminology, phrasing or punctuation suggestions. Each application saves a new revision and reruns the checks. Percentage claims require manual editing of the full sentence to keep conditions intact.
5. Replace the sample with: `EcoVolt offers up to 15% energy savings under specified laboratory conditions.` Save the revision.
6. Open **Comments & decisions**, add context, and request approval.
7. Sign out and sign in as `reviewer`. Select the review, enter a decision explanation, and approve or request changes.
8. Inspect the revision history and download the JSON review report. The overview shows latest-revision category counts and dismissal totals.

An unresolved finding does not silently prevent a submission: the reviewer sees it and must explicitly decide. A clear rule-check result also still requires human review. Approved content is locked. After **Request changes**, the creator can edit and resubmit.

## Implemented scope

- Password authentication with per-user salts and PBKDF2-SHA256 hashes.
- Application-layer role checks, creator ownership checks, separate reviewer approval and state-transition checks.
- Multiple editable brand profiles, unique source IDs and rule-to-source validation.
- Case-insensitive, word-bounded terminology checks and configured promotional phrase rules.
- Tone checks for repeated exclamation marks.
- A source-grounded semantic review layer for configured claim topics, using synonym-aware indicators to catch selected paraphrases (for example, “cuts household power costs in half” against approved energy-savings guidance).
- Relevant approved guidance retrieval, source-ID validation, and explicit missing/unverified-evidence findings; findings never claim that unsupported wording is automatically false.
- Findings with severity, exact text offsets, explanation, source evidence, suggested replacement and decision state.
- Minimal-change edits, manual revisions, dismissal reasons and reopening findings.
- Text entry, UTF-8 `.txt` / `.md` import and text-based PDF extraction.
- A separate Visual review workspace that extracts visible image text with local OCR, checks prominent colours against a user-configured palette, estimates text contrast, and template-matches an uploaded approved logo asset. Findings include text or image-region coordinates and rule explanations; the final decision stays with a human reviewer.
- Durable team collaboration: reviewer assignment, in-app notifications for assignments, submissions, comments and decisions, and organisation-scoped users, brand profiles, reviews and notifications.
- Comments, draft / pending / changes-requested / approved states, revision snapshots, decision events and JSON export.
- SQLite persistence, optimistic revision checks, recurring-finding dashboard and opt-in fictional demo data.

## Visual design

The opening workspace uses a plum navigation rail, violet and lime visual accents, a compact illustrated shield header, status cards, review activity and brand insights. The sign-in screen pairs an illustrated introduction with a focused login form. The dashboard's review and brand-profile buttons navigate to the actual application screens. Finding patterns and status totals reflect stored reviews rather than decorative sample metrics.

The interface uses built-in fonts and inline SVG/CSS artwork, with no external font, image or CDN dependency. The shield animation respects reduced-motion preferences. Narrow layouts stack cards and hide decorative artwork to keep the content readable.

## Two demo brands

| Brand | Category | Example checks |
| --- | --- | --- |
| EcoVolt | Energy technology | Brand spelling, promotional wording, energy-savings percentages and qualifications |
| NovaWear | Everyday apparel | Brand spelling, unsupported sustainability wording, pressure-based sales phrases and tone |

Both brands are fictional. Choose either in **Brand profiles** or the **New review** brand selector. **Load fictional example** loads sample text for the selected brand; switching the selector alone does not replace an unsaved draft. NovaWear has no energy-savings source, so recognised energy claims remain unverified rather than borrowing EcoVolt's evidence.

Fresh demo setup includes a campaign for each brand. Existing installations gain the NovaWear profile on restart; create a review and load its example to try it. The one-time addition preserves any existing NovaWear profile and subsequent edits.

## Brand configuration

Open **Brand profiles** to read the selected brand's description, approved sources, terminology rules, promotional wording and approved energy claim. Reviewers and creators have a read-only view.

Managers and administrators can expand **Edit brand profile** or select **Create brand profile**. Fill in the name and description, then use the editable tables to add, edit or delete sources and rules. Each source needs a unique Source ID, title and approved text. Rules reference those Source IDs. If you change or remove a Source ID, update its rules before saving; invalid references are rejected.

Energy-claim and punctuation checks have their own enable switches, wording and source fields. The source-grounded semantic-check table lets managers define a claim topic, approved source ID, comma-separated paraphrase indicators, optional required context and severity. Source IDs are validated before saving. A new profile starts from the fictional EcoVolt example; replace its guidance with authorised brand content before saving. The JSON download remains available for backup and portability, but no JSON editing is required.

Existing reviews retain their original profile snapshot after profile updates; start a new review to use updated guidance. EcoVolt sources are fictional demo text, not real customer evidence. The engine flags only implemented patterns.

## Team collaboration and organisation workspaces

Administrators can open **Organisations** to create a separate workspace, then open **Users** and select that organisation when creating its users. Existing accounts and records are migrated non-destructively into **Default organisation** on startup. Each account belongs to one organisation; review lists, review details, notifications and brand profiles are scoped to that organisation. New organisations start with no profiles, so a manager in that organisation should create or configure its own brand profile before a creator starts a review.

Reviewers, managers and administrators can assign a review to a reviewer in their organisation from the review detail screen. Assignments, submitted reviews, comments and approval/change decisions create persistent in-app notifications. Open **Notifications** from the sidebar and mark items as read. Notifications are stored in SQLite, not just in the browser session.

The default database path is `data/brandshield.sqlite3`. SQLite records survive application restarts as long as the database file is retained. For hosted deployments, configure `BRANDSHIELD_DB` to a persistent disk path supplied by the host and back up that file regularly. A host with ephemeral storage can still discard the database when the instance is replaced; application code alone cannot make an ephemeral disk durable. Keep each organisation's user accounts in its own workspace and do not publish the database file.

## Visual content review

Open **Visual review** in the left navigation and upload a PNG, JPG or WEBP promotional image. Enter the approved brand palette as comma-separated six-digit hex colours (for example `#176B45, #E8F5EE, #FFFFFF`). Optionally upload a clean approved logo image to check whether it appears in the creative. The report includes extracted text, approximate OCR boxes, prominent off-palette colours, estimated contrast ratios and a logo-match result. Download the findings as JSON if needed.

Image text extraction requires the Tesseract OCR engine in addition to the Python packages. On Windows, install Tesseract OCR and ensure `tesseract.exe` is on PATH; then restart Command Prompt and run the app again. On Linux, install the `tesseract-ocr` system package. This feature uses local OCR, Pillow and OpenCV; it does not call a paid API. Contrast and colour estimates are heuristic, logo template matching can miss altered or unusually scaled assets, and photos may contain intentional off-brand colours. Review every finding manually. Upload limits are 8 MB and 3000 × 3000 pixels.

## Updating an existing installation

Stop Streamlit, replace the application files with this version, and restart it. Keep your existing `data` folder to preserve accounts, profiles and reviews. The app automatically adds the NovaWear demo profile once on startup, without overwriting existing profiles or reviews. Do not rerun `demo.py` on an existing database.

## Project layout

```text
app.py                  Streamlit screens and session login
brands.py               NovaWear profile and brand-specific demo content
profiles_ui.py          Readable brand profiles and role-aware editing forms
visual_review.py        Local OCR, palette, contrast and logo template checks
theme.py                Visual theme, cards, status badges and evidence panels
engine.py               Profile validation and deterministic finding engine
store.py                SQLite persistence, permissions and workflow
demo.py                Opt-in demo accounts and example review
requirements.txt        Runtime dependencies
.streamlit/config.toml  Theme and upload limit
tests/test_project.py   Engine, evidence, storage and permissions tests
tests/test_visual_review.py Synthetic image, OCR, contrast and logo-check tests
tests/test_collaboration.py Organisation isolation, assignments and notification persistence
tests/test_app.py       Headless Streamlit screen and workflow tests
```

## Tests

From the project folder after installing dependencies:

```bash
python -m unittest discover -s tests -v
```

Verification: 48 tests completed with 0 failures; 40 passed and 8 Streamlit-dependent checks were skipped because Streamlit is not installed in the build environment. Tests use temporary databases and synthetic images. The collaboration tests cover workspace isolation, assignment notifications and persistence across Store reinitialisation. Eight Streamlit-dependent checks are skipped when Streamlit is not installed. These are functional checks, not a claim of measured real-world accuracy or usability.

## Data and deployment

By default, the database is `data/brandshield.sqlite3` relative to the working directory. Set the `BRANDSHIELD_DB` environment variable to choose a different file. Back up the database for durable review history. Do not include populated databases in a public repository.

For Streamlit Community Cloud or a Python host, use `app.py` as the entrypoint and install `requirements.txt`. Use a host with persistent disk for retained SQLite data; ephemeral hosting may reset it. This package has not been deployed to a public service.

## Deliberate limitations

This is a hackathon MVP, not production-grade compliance software. Analysis runs locally through deterministic Python rules and synonym-aware concept matching, so no paid API, AI key or external processing is required. The semantic layer only covers configured claim topics and indicators; it is not a general-purpose language model, does not prove claims true or false, and can miss paraphrases or produce false positives. Reviewers must inspect the retrieved guidance and full context before deciding.

Scanned-PDF OCR, publishing integrations and notifications are outside this MVP. Text-review uploads are limited to 5 MB, text to 50,000 characters and PDFs to 50 pages. PDFs must have extractable text. Visual-review images are limited to 8 MB and 3000 × 3000 pixels. Uploaded image bytes are processed in memory and are not stored as review records.

For production use, add managed identity, account recovery, login throttling, more granular tenant isolation, operational audit protection, backup/retention controls and broader evaluation. Current audit events are application records, not a tamper-proof external audit system. The application never publishes submitted content.

## Team

Akhil Gunda — Team lead + Backend  
Dulam Nithin — UI + data  
Divyamsh Nagamalla — AI/rules + testing

## Code readability update

See [REFACTOR_NOTES.md](REFACTOR_NOTES.md) for the reasoning behind each significant change and `refactor_changes.patch` for the source diff. The interface and database format remain compatible with your existing installation.

## Deploy on Render

This repository includes a `Dockerfile` and `render.yaml` for a Render Docker web service. The image installs Tesseract OCR so the visual-review OCR feature has its system dependency available.

1. Push the contents of this `brandshield` folder to a GitHub repository.
2. In Render, choose **New +** → **Blueprint** and connect that repository. If Render does not detect the Blueprint automatically, create a **Web Service** using the Docker runtime and set the root directory to `brandshield` (or upload the contents of this folder to the repository root and use `.`).
3. Review the service settings and deploy.
4. After deployment, open the generated `onrender.com` URL and test sign-in and the review flows.

**Important deployment notes:** This demo includes public demo credentials. Anyone who can reach the public app may be able to sign in, so use fictional demo data only and do not upload real or sensitive content. The default Render filesystem is ephemeral; SQLite changes may be lost when the service restarts or redeploys. For durable production data, use a persistent disk or a managed database and configure it deliberately. Free services may sleep when idle.
