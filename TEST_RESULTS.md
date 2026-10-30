# Verification results

35 automated tests passed on 2026-10-24 using Python 3.11.

Coverage includes terminology boundaries, exact finding offsets, source validation, percentage conflicts and qualifications, missing-evidence labels, revision snapshots, SQLite persistence, creator isolation, role enforcement, self-approval prevention, stale-revision rejection, dismissal reasons, and the request-changes/resubmission/approval workflow.

Three headless Streamlit tests exercised creator screens and corrections, reviewer approval, and administrator pages. No interactive browser visual inspection or hosted deployment was performed. Real-world precision, recall, user research and time savings have not been measured.

Reproduce from the project folder: `python -m unittest discover -s tests -v`.

The visual refresh was checked with the same 25-test suite; all passed. The update adds a teal navigation theme, branded headers, recent-review cards, status badges, and styled evidence panels.

The completed Brand profiles interface passed three additional Streamlit tests: reviewers receive a readable read-only view, administrators can create a profile through the form, and profile edits persist with a new version. No browser visual inspection was performed.

Four additional tests verify NovaWear findings and evidence, separation of brand rules, idempotent profile seeding that preserves edits, and upgrade from an existing single-brand database. All 32 tests pass.

The new opening-view redesign passed the full 33-test suite. A new Streamlit test verifies that dashboard actions navigate to New review and Brand profiles. The browser could not connect to the local preview server, so visual browser QA remains unverified. No screenshot of the redesign is included.

Removed the sign-in demo/help block and the dashboard decision-help expander as requested. The full 33-test suite passed after this cleanup.

Readability refactor verification (2026-10-25): all 35 tests passed with no skips, including the seven Streamlit screen tests and two added regressions. Additionally, 822 before/after engine comparisons matched on every finding field except generated UUIDs; applicable suggestion outputs matched. See REFACTOR_NOTES.md for scope and limitations.

Header visibility fix: increased the main content top padding to 4.75rem at all three layout breakpoints so the fixed Streamlit toolbar does not overlap the app wordmark on initial load. Syntax and all three CSS declarations checked; no new browser visual verification was available.


Source-grounded semantic review update (2026-10-30): 40 tests completed with 0 failures; 32 passed and 8 Streamlit-dependent UI checks were skipped because Streamlit was not installed in the build environment. Added regressions for synonym-aware paraphrase detection, retrieved approved source evidence, brand-specific source separation, invalid semantic source IDs, missing evidence, and safe migration of existing profiles. UI browser testing and hosted deployment were not performed.

Visual content review update (2026-10-30): 46 tests completed with 0 failures; 38 passed and 8 Streamlit-dependent checks were skipped because Streamlit was not installed in the build environment. Added synthetic-image checks for palette parsing, contrast ratio, invalid image handling, OCR region data and approved-logo matching. Tesseract OCR was available in the build environment. No interactive browser visual inspection or hosted deployment was performed.
