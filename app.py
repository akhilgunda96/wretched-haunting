import hashlib
import json
import sqlite3
from collections import Counter
from io import BytesIO

import streamlit as st

from engine import apply_suggestion
from store import Store, ROLES
from brands import BRAND_SAMPLES
from demo import seed as seed_demo

from theme import (
    inject_styles,
    brand,
    hero,
    section,
    recent_reviews,
    evidence,
    status_badge,
    showcase,
    dashboard_header,
    stats,
    findings_panel,
    brands_panel,
)

st.set_page_config(page_title='BrandShield AI', page_icon='🛡️', layout='wide')
inject_styles()
db = Store()


def run_action(action, *args):
    try:
        result = action(*args)
        st.session_state['flash'] = 'Saved successfully.'
        return result, True
    except (ValueError, PermissionError, sqlite3.IntegrityError) as exc:
        st.error(str(exc))
        return None, False


brand()
# This project is packaged as a local hackathon demo. Initialise fictional demo
# accounts only when the selected database has no users; never overwrite accounts.
if not db.has_users():
    seed_demo()
    db = Store()
if 'user' not in st.session_state:
    intro, signin = st.columns([1.4, 1], gap='large')
    with intro:
        showcase()
        section('A clearer path to better content')
        st.write('01  —  Choose your brand’s approved guidance')
        st.write('02  —  Review findings and refine your draft')
        st.write('03  —  Get a separate reviewer’s approval')
    with signin:
        st.subheader('Your workspace awaits.')
        st.caption('Sign in to keep your brand moving forward.')
        st.info('Demo credentials — as requested by the hackathon organisers, these are displayed here on the website UI for judges and evaluators.\n\nCreator: `creator` · Reviewer: `reviewer` · Manager: `manager`\n\nPassword for all three accounts: `BrandShield!2026`')
        with st.form('login'):
            username = st.text_input('Username', placeholder='Enter your username')
            password = st.text_input(
                'Password', type='password', placeholder='Enter your password'
            )
            if st.form_submit_button(
                'Sign in', type='primary', use_container_width=True
            ):
                user = db.authenticate(username, password)
                if user:
                    st.session_state['user'] = user
                    st.rerun()
                else:
                    st.error('Invalid username or password.')
    st.stop()
current_user = st.session_state['user']
actor = current_user['username']
with st.sidebar:
    st.markdown(
        '<div class="bs-side-name">BrandShield AI</div><div class="bs-side-label">BRAND GOVERNANCE WORKSPACE</div>',
        unsafe_allow_html=True,
    )
    st.write(current_user['name'])
    st.caption(current_user['role'].upper())
    unread_count = sum(not item['is_read'] for item in db.notifications(actor))
    st.caption(f"{unread_count} unread notification(s)")
    choices = ['Overview', 'Reviews', 'Visual review', 'Notifications']
    if current_user['role'] in ('creator', 'admin'):
        choices.append('New review')
    choices.append('Brand profiles')
    if current_user['role'] == 'admin':
        choices.extend(['Users', 'Organisations'])
    page = st.radio('Workspace', choices, key='workspace_page')
    st.divider()
    st.caption('Rule-based MVP · No external AI processing')
    if st.button('Sign out'):
        st.session_state.clear()
        st.rerun()
if st.session_state.pop('flash', None):
    st.success('Saved successfully.')
reviews = db.list_reviews(actor)
if page == 'Overview':
    dashboard_header(current_user['name'])
    stats(reviews)

    def navigate(target):
        st.session_state['workspace_page'] = target

    activity, insights = st.columns([1.5, 1], gap='large')
    with activity:
        section('Review workspace', 'Your latest drafts and decisions')
        actions = st.columns(2)
        if current_user['role'] in ('creator', 'admin'):
            actions[0].button(
                '＋ Start a review',
                type='primary',
                use_container_width=True,
                on_click=navigate,
                args=('New review',),
            )
        else:
            actions[0].button(
                'Open review queue →',
                type='primary',
                use_container_width=True,
                on_click=navigate,
                args=('Reviews',),
            )
        actions[1].button(
            'Browse brand profiles',
            use_container_width=True,
            on_click=navigate,
            args=('Brand profiles',),
        )
        recent_reviews(reviews)
    with insights:
        section('At a glance', 'Guidance & review patterns')
        counts = Counter()
        dismissed = Counter()
        for review in reviews:
            findings = db.detail(actor, review['id'])['revisions'][0]['findings']
            counts.update(finding['type'] for finding in findings)
            dismissed.update(
                finding['type']
                for finding in findings
                if finding['status'] == 'Dismissed'
            )
        findings_panel(counts, dismissed)
        profiles = db.profiles(actor)
        brands_panel(
            [{**profile, 'body': json.loads(profile['body'])} for profile in profiles]
        )
        st.caption(
            'Patterns use latest revisions of visible reviews, not measured accuracy or time savings.'
        )
elif page == 'New review':
    hero(
        'CREATE / CHECK / REFINE',
        'Make every message on-brand.',
        'Choose a brand profile, add your draft, and turn configured guidance into clear, actionable findings.',
    )
    section('Prepare your draft', 'Select your approved guidance and content')
    profiles = db.profiles(actor)
    profile = st.selectbox(
        'Brand profile',
        profiles,
        format_func=lambda profile: f"{profile['name']} · v{profile['version']}",
    )
    title = st.text_input(
        'Review title', max_chars=180, placeholder='October energy campaign'
    )
    st.selectbox(
        'Content channel', ['Social post', 'Advertisement', 'Landing page', 'Other']
    )
    st.caption(
        'Channel is descriptive context. The configured checks are the same across channels.'
    )
    upload = st.file_uploader(
        'Import a .txt, .md or text-based .pdf file', type=['txt', 'md', 'pdf']
    )
    if upload and st.button('Import text'):
        try:
            if upload.size > 5 * 1024 * 1024:
                raise ValueError('Upload limit: 5 MB.')
            if upload.name.lower().endswith('.pdf'):
                from pypdf import PdfReader

                reader = PdfReader(BytesIO(upload.getvalue()))
                if len(reader.pages) > 50:
                    raise ValueError('PDF limit: 50 pages.')
                text = '\n'.join(
                    pdf_page.extract_text() or '' for pdf_page in reader.pages
                )
            else:
                text = upload.getvalue().decode('utf-8-sig')
            if not text.strip():
                raise ValueError(
                    'No extractable text. Scanned PDFs need OCR, which is outside this MVP.'
                )
            if len(text) > 50000:
                raise ValueError('Content exceeds 50,000 characters.')
            st.session_state['new_content'] = text
            st.rerun()
        except Exception as exc:
            st.error(f'Import failed: {exc}')
    if profile['name'] in BRAND_SAMPLES and st.button('Load fictional example'):
        st.session_state['new_content'] = BRAND_SAMPLES[profile['name']]
        st.rerun()
    text = st.text_area('Content', key='new_content', height=230, max_chars=50000)
    if st.button('Analyse & save draft', type='primary'):
        review_id, succeeded = run_action(db.create, actor, title, text, profile['id'])
        if succeeded:
            st.session_state['selected_review'] = review_id
            st.success(
                f'Review #{review_id} created. Open Reviews to inspect the findings.'
            )
elif page == 'Reviews':
    section('Content reviews', 'From first draft to final decision')
    status = st.selectbox(
        'Filter status',
        ['All', 'Draft', 'Pending review', 'Changes requested', 'Approved'],
    )
    shown = [
        review for review in reviews if status == 'All' or review['status'] == status
    ]
    if not shown:
        st.info('No reviews match this filter.')
        st.stop()
    ids = [review['id'] for review in shown]
    preferred = st.session_state.get('selected_review', ids[0])
    review_id = st.selectbox(
        'Select review',
        ids,
        index=ids.index(preferred) if preferred in ids else 0,
        format_func=lambda id: next(
            f"#{id} · {review['title']} · {review['status']}"
            for review in shown
            if review['id'] == id
        ),
    )
    review = db.detail(actor, review_id)
    latest_revision = review['revisions'][0]
    st.subheader(review['title'])
    st.markdown(status_badge(review['status']), unsafe_allow_html=True)
    st.caption(f"Organisation workspace ID: {review['organization_id']} · Assigned reviewer: {review.get('assigned_to') or 'Unassigned'}")
    if current_user['role'] in ('reviewer', 'manager', 'admin'):
        reviewer_options = db.reviewers(actor)
        if reviewer_options:
            reviewer_names = [item['username'] for item in reviewer_options]
            current_assignment = review.get('assigned_to')
            default_index = reviewer_names.index(current_assignment) if current_assignment in reviewer_names else 0
            with st.form(f'assign_review_{review_id}'):
                assignee = st.selectbox('Assign reviewer', reviewer_names, index=default_index)
                if st.form_submit_button('Save assignment'):
                    _, succeeded = run_action(db.assign_review, actor, review_id, assignee)
                    if succeeded:
                        st.rerun()
    st.caption(
        f"{review['status']} · Revision {review['version']} · Created by {review['creator']} · {latest_revision['profile']['name']}"
    )
    editable = review['creator'] == actor and review['status'] in (
        'Draft',
        'Changes requested',
    )
    content_tab, decisions_tab, history_tab = st.tabs(
        ['Content & findings', 'Comments & decisions', 'Revision history']
    )
    with content_tab:
        left, right = st.columns([1.1, 1])
        with left:
            content = st.text_area(
                'Current content',
                latest_revision['content'],
                height=350,
                disabled=not editable,
                key=f"edit_{review_id}_{review['version']}",
            )
            st.caption(
                'Apply a focused correction or edit here, then save to run all checks again. New revisions reset finding decisions.'
            )
            if editable and st.button('Save revision & reanalyse', type='primary'):
                _, succeeded = run_action(
                    db.revise, actor, review_id, content, review['version']
                )
                if succeeded:
                    st.rerun()
            st.download_button(
                'Download review report',
                json.dumps(review, indent=2),
                file_name=f'brandshield-review-{review_id}.json',
                mime='application/json',
            )
        with right:
            open_findings = [
                finding
                for finding in latest_revision['findings']
                if finding['status'] == 'Open'
            ]
            st.write(
                f"**{len(open_findings)} open findings** · {len(latest_revision['findings'])} total"
            )
            st.caption(
                'Checks combine configured rules with synonym-aware, source-grounded review of selected claim topics. This deterministic matching can miss context or nuance; human review is always required.'
            )
            if not latest_revision['findings']:
                st.success(
                    'No configured-rule findings. Human review is still required.'
                )
            for finding in latest_revision['findings']:
                with st.expander(
                    f"{finding['severity']} · {finding['type']} · {finding['status']}",
                    expanded=finding['status'] == 'Open',
                ):
                    st.code(finding['affected'], language=None)
                    st.write(finding['explanation'])
                    st.caption(f"Source: {finding['source_id'] or 'Unverified'}")
                    evidence(finding['evidence'], finding['source_id'])
                    related_sources = [
                        source for source in finding.get('related_sources', [])
                        if source.get('source_id') != finding.get('source_id')
                    ]
                    if related_sources:
                        with st.expander('Other relevant approved guidance'):
                            for source in related_sources:
                                evidence(source['text'], source['source_id'])
                    if finding['suggestion'] is not None:
                        st.write('Suggested replacement:')
                        st.code(finding['suggestion'], language=None)
                        if (
                            editable
                            and finding['status'] == 'Open'
                            and st.button(
                                'Apply & reanalyse', key='apply' + finding['id']
                            )
                        ):
                            if content != latest_revision['content']:
                                st.warning(
                                    'Save your unsaved edits before applying a suggestion.'
                                )
                            else:
                                try:
                                    revised = apply_suggestion(
                                        latest_revision['content'], finding
                                    )
                                    _, succeeded = run_action(
                                        db.revise,
                                        actor,
                                        review_id,
                                        revised,
                                        review['version'],
                                    )
                                    if succeeded:
                                        st.rerun()
                                except ValueError as exc:
                                    st.error(str(exc))
                    else:
                        st.caption(
                            'Manual revision required. Review the approved wording and revise the whole claim where needed.'
                        )
                    if editable:
                        note = st.text_input(
                            'Decision reason', key='reason' + finding['id']
                        )
                        decision = (
                            'Dismissed' if finding['status'] == 'Open' else 'Open'
                        )
                        if st.button(
                            (
                                'Dismiss finding'
                                if decision == 'Dismissed'
                                else 'Reopen finding'
                            ),
                            key='decision' + finding['id'],
                        ):
                            _, succeeded = run_action(
                                db.finding_decision,
                                actor,
                                review_id,
                                finding['id'],
                                decision,
                                note,
                                review['version'],
                            )
                            if succeeded:
                                st.rerun()
    with decisions_tab:
        st.subheader('Human approval')
        st.caption(
            'Open findings remain visible to the reviewer. Approval is an explicit human decision, and self-approval is blocked.'
        )
        note = st.text_area(
            'Comment or decision explanation', max_chars=5000, key=f'note{review_id}'
        )
        if st.button('Add comment'):
            _, succeeded = run_action(db.comment, actor, review_id, note)
            if succeeded:
                st.rerun()
        if editable and st.button('Request approval', type='primary'):
            _, succeeded = run_action(
                db.transition, actor, review_id, 'Submit', note, review['version']
            )
            if succeeded:
                st.rerun()
        if (
            current_user['role'] in ('reviewer', 'manager', 'admin')
            and actor != review['creator']
            and review['status'] == 'Pending review'
        ):
            for action in ['Approve', 'Request changes']:
                if st.button(action):
                    _, succeeded = run_action(
                        db.transition, actor, review_id, action, note, review['version']
                    )
                    if succeeded:
                        st.rerun()
        for event in review['events']:
            st.write(
                f"**{event['action']}** · {event['actor']} · v{event['version']} · {event['created']} UTC"
            )
            st.text(event['note'])
    with history_tab:
        st.caption(
            'Each revision retains its own content, findings and approved-source snapshot.'
        )
        for revision in review['revisions']:
            with st.expander(
                f"Revision {revision['version']} · {revision['actor']} · {revision['created']} UTC"
            ):
                st.text(revision['content'])
                st.json(revision['findings'])
                st.json(revision['profile'])
elif page == 'Notifications':
    section('Notifications', 'Updates for reviews that need your attention')
    notices = db.notifications(actor)
    if not notices:
        st.info('No notifications yet. Assignments, comments and review decisions will appear here.')
    for notice in notices:
        with st.container(border=True):
            st.write(('🔔 ' if not notice['is_read'] else '✓ ') + notice['message'])
            st.caption(notice['created'] + ' UTC')
            if not notice['is_read'] and st.button('Mark as read', key=f"read_{notice['id']}"):
                db.mark_notification_read(actor, notice['id'])
                st.rerun()
elif page == 'Organisations':
    section('Organisation workspaces', 'Separate users, brand profiles and review records')
    with st.form('org_form', clear_on_submit=True):
        org_name = st.text_input('New organisation name')
        if st.form_submit_button('Create organisation'):
            _, succeeded = run_action(db.create_organization, actor, org_name)
            if succeeded:
                st.rerun()
    orgs = db.organizations(actor)
    st.dataframe([{'ID': org['id'], 'Organisation': org['name'], 'Created': org['created']} for org in orgs], use_container_width=True)
    st.caption('Create users for another organisation from the Users page by selecting its workspace.')
elif page == 'Visual review':
    from visual_review import review_image
    from PIL import ImageDraw

    hero(
        'VISUAL CONTENT REVIEW',
        'Check the image, not just the caption.',
        'Extract visible text, compare prominent colours with your palette, estimate text contrast, and check an uploaded approved logo asset.',
    )
    section('Set the visual rules', 'These checks are local and heuristic; a person makes the final decision.')
    palette_text = st.text_input(
        'Approved brand colours (comma-separated hex)',
        value='#176B45, #E8F5EE, #FFFFFF',
        help='Example: #176B45, #E8F5EE, #FFFFFF. Use six-digit hex colours.',
        key='visual_palette',
    )
    st.caption('Contrast target: 4.5:1 for normal text. Palette checks focus on prominent colours and may flag intentional photography.')
    section('Upload promotional image', 'PNG, JPG or WEBP · Maximum 8 MB · Maximum 3000 × 3000 pixels')
    image_upload = st.file_uploader(
        'Promotional image', type=['png', 'jpg', 'jpeg', 'webp'], key='visual_image_upload'
    )
    logo_upload = st.file_uploader(
        'Approved logo asset (optional)', type=['png', 'jpg', 'jpeg', 'webp'],
        help='Upload a clean approved logo to check whether it appears in the promotional image.',
        key='visual_logo_upload',
    )
    if image_upload:
        st.image(image_upload.getvalue(), caption='Image to review', use_container_width=True)
        if st.button('Analyse visual content', type='primary'):
            try:
                result = review_image(
                    image_upload.getvalue(), palette_text,
                    logo_upload.getvalue() if logo_upload else None,
                )
                st.session_state['visual_review_result'] = result
                st.session_state['visual_review_hash'] = hashlib.sha256(image_upload.getvalue()).hexdigest()
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
    result = st.session_state.get('visual_review_result')
    if image_upload and st.session_state.get('visual_review_hash') != hashlib.sha256(image_upload.getvalue()).hexdigest():
        result = None
    if result:
        st.divider()
        section('Extracted text', 'OCR text is listed with its approximate image region')
        if result['extracted_text']:
            annotated = Image.open(BytesIO(image_upload.getvalue())).convert('RGB') if image_upload else None
            if annotated:
                draw = ImageDraw.Draw(annotated)
                for item in result['extracted_text']:
                    draw.rectangle(item['box'], outline='#E4572E', width=3)
                st.image(annotated, caption='Detected text regions (orange boxes)', use_container_width=True)
            for item in result['extracted_text']:
                x, y, x2, y2 = item['box']
                st.write(f"**{item['text']}** — region x={x}, y={y}, width={x2-x}, height={y2-y}; OCR confidence {item['confidence']}%")
        else:
            st.warning('No readable text was extracted. Check image quality or try a higher-resolution image.')
        section('Findings', 'Each finding identifies a region and explains the configured rule')
        if not result['findings']:
            st.success('No visual-rule findings were detected. Human review is still required.')
        for index, finding in enumerate(result['findings'], start=1):
            with st.expander(f"{finding['severity']} · {finding['type']} · {finding['region']}", expanded=True):
                st.write(finding['explanation'])
                if finding.get('text'):
                    st.code(finding['text'], language=None)
                if finding.get('details'):
                    st.dataframe(finding['details'], hide_index=True, use_container_width=True)
                if finding.get('contrast_ratio') is not None:
                    st.metric('Estimated contrast ratio', f"{finding['contrast_ratio']}:1")
                if finding.get('similarity') is not None:
                    st.metric('Logo template similarity', finding['similarity'])
        st.info(result['note'])
        st.download_button(
            'Download visual review report', json.dumps(result, indent=2),
            file_name='brandshield-visual-review.json', mime='application/json',
        )
elif page == 'Brand profiles':
    from profiles_ui import render_profiles

    render_profiles(db, current_user, run_action)
elif page == 'Users':
    section('People & permissions', 'Give each teammate the right role')
    st.write(
        'Creators access their own reviews. Reviewers and managers review across the workspace. Managers configure profiles; administrators also create users.'
    )
    with st.form('user_form', clear_on_submit=True):
        name = st.text_input('Display name')
        username = st.text_input('New username')
        role = st.selectbox('Role', ROLES)
        password = st.text_input('New password (12+ characters)', type='password')
        organisations = db.organizations(actor)
        org_labels = {f"{org['name']} (ID {org['id']})": org['id'] for org in organisations}
        chosen_org = st.selectbox('Organisation workspace', list(org_labels), index=0)
        if st.form_submit_button('Create user', type='primary'):
            run_action(db.add_user, actor, username, name, role, password, org_labels[chosen_org])
st.markdown(
    '<div class="bs-footer"><span>BRANDSHIELD AI · TEAM GRUMPYBOT</span><span>TECHCIRCUIT Hackathon · Evidence first. People in control.</span></div>',
    unsafe_allow_html=True,
)
