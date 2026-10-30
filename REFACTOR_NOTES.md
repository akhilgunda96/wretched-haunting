# Readability refactor

Applied after the proposed changes were reviewed and approved. The existing Streamlit interface, database schema, review states, configured rules, evidence fields and error messages were retained. The existing Store class and file structure remain in place. No framework, new application class or runtime dependency was added.

## 1. engine.py: remove the temporary Span class

Previously, percentage checks searched a sentence substring, calculated its offset in the complete text and constructed an object with start(), end() and group() methods. That object only imitated a regular-expression match.

The refactor compiles the same percentage pattern once per analysis and searches the original text between each sentence's start and end positions. Python supplies a real match with positions in the original text. The finding helper uses that match directly. The sentence expression, percentage expression, finding order, rule conditions and evidence text are unchanged.

How to explain it: “Searching the original text gives us the correct positions automatically, so we do not need a class just to calculate offsets.”

The existing local finding helper is named add_finding rather than add. Validator names such as profile, source, source_ids and field_name describe the data being checked. Long validation expressions now span readable lines; their order and short-circuit behaviour remain unchanged.

## 2. store.py: make the review query explicit

list_reviews now constructs its query and parameters in separate statements. It adds the creator ownership filter only for creators, then applies the same ordering by update time and review ID. SQL values are still bound parameters.

Database connection variables are named connection. Retrieved records use review, revision, finding, findings or profile_row as appropriate. Compound statements were expanded, making transaction handling and permission checks easier to follow.

How to explain it: “The query shows the access rule directly: creators see their own reviews; the other authorised roles see the workspace reviews.”

Existing public Store method names and parameter names such as rid, pid and expected were retained to avoid changing callers that may use keyword arguments. Database columns, saved JSON keys, password hashing and workflow permissions were not changed.

## 3. profiles_ui.py: remove an unused argument

populated(rows, field) became remove_empty_rows(rows). The field argument was unused, so all three callers now pass only the editor rows. DataFrames still have missing cells normalised to empty strings; list inputs keep their existing handling. Entirely blank rows are removed, while partially completed rows still reach the existing validation.

Profile, profile_id, selected_profile, source and rule replace abbreviated names. Metric columns are named after their content. The editable profile is deep-copied when the form is submitted rather than on every display rerun; the copy still preserves unedited profile fields.

How to explain it: “The helper removes only completely empty rows. Incomplete rules still need to be checked, so we do not silently discard them.”

## 4. app.py: clearer screen variables

The shared action wrapper is named run_action, with action as its callable argument. It retains the same success message, return values and exception handling. Its profile-screen callback was updated to match.

Key local renames include:

| Previous | Current |
| --- | --- |
| u | current_user |
| rid | review_id |
| r / v in the review screen | review / latest_revision |
| fs / f | findings / finding |
| open_fs | open_findings |
| a / b / c for tabs | content_tab / decisions_tab / history_tab |
| ok | succeeded |
| pw | password |
| e / rev | event / revision |

The PDF page variable is pdf_page, distinguishing it from a brand profile. Unused engine imports were removed. The content-channel selector remains visible; only its unused Python assignment was removed. Imports were grouped before the Streamlit setup call; set_page_config remains the first executed Streamlit call.

How to explain it: “The names tell us whether we are working with the complete review, its latest saved revision or one finding. The data and screen actions are the same.”

## 5. Consistent formatting

The four affected application modules were formatted with Black, preserving the existing string-quote style. Semicolon-separated statements and one-line branches were expanded. Long calls, dictionaries and conditions use consistent indentation. The visual theme, demo brands and existing tests were not reformatted as part of the application cleanup.

Comments explaining profile snapshots, one-time brand setup, text offsets and uncertainty were retained. No new explanatory comments were added for self-evident assignments or loops. Black was a development tool for this refactor; it is not required to run the app.

## Verification

- All 33 existing tests passed after installing the existing requirements, including all seven Streamlit screen tests; none were skipped.
- Two additional regression tests cover percentage positions in the original text and blank versus partially completed profile-editor rows.
- The final suite passed all 35 tests with no skips.
- A one-off comparison against the pre-refactor engine covered 822 input/profile combinations: fictional brand samples, missing energy evidence, decimal and Unicode percentages, sentence boundaries, unrelated discounts, qualifications and multiple claims. Every finding field except the generated UUID matched. Applicable suggestion outputs also matched.

These checks provide evidence of preserved behaviour; they are not an exhaustive proof for every possible input. No new browser visual inspection was performed for this code-only refactor.

Run the tests from the project folder:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

See refactor_changes.patch for the exact before-and-after source changes. No database migration is needed. Keep the existing data folder when replacing the application files.
