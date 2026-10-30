"""Readable brand guidance and role-aware profile forms."""

import copy
import json

import pandas as pd
import streamlit as st

from engine import DEFAULT_PROFILE
from theme import hero, section, evidence


def show_profile(profile):
    st.subheader(profile['name'])
    if profile.get('description'):
        st.text(profile['description'])
    sources_column, terms_column, phrases_column = st.columns(3)
    sources_column.metric('Approved sources', len(profile['sources']))
    terms_column.metric('Terminology rules', len(profile.get('terms', [])))
    phrases_column.metric('Language rules', len(profile.get('phrases', [])))
    section('Voice & approved guidance', 'The evidence used during a review')
    for source in profile['sources']:
        st.write('**' + source['title'] + '**')
        evidence(source['text'], source['id'])
    section('Approved terminology', 'Use consistent names across every channel')
    terms = profile.get('terms', [])
    if terms:
        st.dataframe(
            [
                {
                    'Avoid': rule['term'],
                    'Use instead': rule['replacement'],
                    'Source': rule['source_id'],
                }
                for rule in terms
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info('No terminology rules configured.')
    section('Promotional wording', 'Focused corrections for configured phrases')
    phrases = profile.get('phrases', [])
    if phrases:
        st.dataframe(
            [
                {
                    'Avoid': rule['phrase'],
                    'Suggested wording': rule['replacement'],
                    'Severity': rule.get('severity', 'Medium'),
                    'Source': rule['source_id'],
                }
                for rule in phrases
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info('No promotional phrase rules configured.')
    section('Approved energy claim')
    claim = profile.get('energy_claim')
    if claim:
        st.write(f"Maximum supported savings: **{claim['max_percent']:g}%**")
        evidence(claim['approved_wording'], claim['source_id'])
        st.caption(
            'The full wording and conditions matter. A percentage alone is not sufficient evidence.'
        )
    else:
        st.info(
            'No energy-savings claim is configured. Recognised energy claims are labelled unverified.'
        )
    if profile.get('punctuation_source_id'):
        st.caption(
            'Tone check enabled: repeated exclamation marks · Source '
            + profile['punctuation_source_id']
        )


def remove_empty_rows(rows):
    # Ignore completely empty rows added by the editor; partially filled rows must pass validation.
    if hasattr(rows, 'to_dict'):
        rows = rows.fillna('').to_dict('records')
    return [
        dict(row)
        for row in rows
        if any(value is not None and str(value).strip() for value in row.values())
    ]


def edit_profile(db, actor, profile, profile_id, run_action):
    with st.form('edit_profile_' + str(profile_id), border=True):
        section('Brand details')
        name = st.text_input(
            'Brand name',
            value=profile['name'] if profile_id else '',
            placeholder='Your brand name',
            max_chars=120,
        )
        description = st.text_area(
            'Brand description',
            value=profile.get('description', '') if profile_id else '',
            max_chars=1500,
        )
        section(
            'Approved sources', 'Add, edit or delete rows. Source IDs must be unique.'
        )
        st.caption(
            'Each source needs an ID, title and approved text. When changing IDs, update the rule references below before saving.'
        )
        sources = st.data_editor(
            pd.DataFrame(profile['sources'], columns=['id', 'title', 'text']),
            num_rows='dynamic',
            hide_index=True,
            use_container_width=True,
            key=f'sources_{profile_id}',
            column_config={
                'id': st.column_config.TextColumn('Source ID', required=True),
                'title': st.column_config.TextColumn('Title', required=True),
                'text': st.column_config.TextColumn(
                    'Approved text', required=True, width='large'
                ),
            },
        )
        section('Terminology rules', 'For example: Eco Volt → EcoVolt')
        terms = st.data_editor(
            pd.DataFrame(
                profile.get('terms', []), columns=['term', 'replacement', 'source_id']
            ),
            num_rows='dynamic',
            hide_index=True,
            use_container_width=True,
            key=f'terms_{profile_id}',
            column_order=['term', 'replacement', 'source_id'],
            column_config={
                'term': st.column_config.TextColumn('Avoid', required=True),
                'replacement': st.column_config.TextColumn(
                    'Use instead', required=True
                ),
                'source_id': st.column_config.TextColumn('Source ID', required=True),
            },
        )
        section('Promotional wording')
        phrases = st.data_editor(
            pd.DataFrame(
                profile.get('phrases', []),
                columns=['phrase', 'replacement', 'source_id', 'severity'],
            ).fillna({'severity': 'Medium'}),
            num_rows='dynamic',
            hide_index=True,
            use_container_width=True,
            key=f'phrases_{profile_id}',
            column_order=['phrase', 'replacement', 'source_id', 'severity'],
            column_config={
                'phrase': st.column_config.TextColumn('Avoid', required=True),
                'replacement': st.column_config.TextColumn(
                    'Suggested wording', required=True
                ),
                'source_id': st.column_config.TextColumn('Source ID', required=True),
                'severity': st.column_config.SelectboxColumn(
                    'Severity',
                    options=['Low', 'Medium', 'High'],
                    required=True,
                    default='Medium',
                ),
            },
        )
        section('Energy-savings claim')
        claim = profile.get('energy_claim') or {}
        enabled = st.checkbox(
            'Enable the energy-savings claim check', value=bool(claim)
        )
        st.caption('The fields below are used only when this check is enabled.')
        maximum = st.number_input(
            'Maximum supported savings (%)',
            min_value=0.0,
            max_value=100.0,
            value=float(claim.get('max_percent', 15)),
            step=0.5,
        )
        wording = st.text_area(
            'Approved claim wording',
            value=claim.get('approved_wording', ''),
            placeholder='Include all approved conditions and qualifications.',
        )
        claim_source = st.text_input(
            'Claim source ID',
            value=claim.get('source_id', ''),
            help='Must match an ID in Approved sources.',
        )
        section('Source-grounded semantic checks', 'Catch paraphrased claims, not just exact phrases')
        semantic_checks = st.data_editor(
            pd.DataFrame([
                {
                    'topic': check.get('topic', ''),
                    'source_id': check.get('source_id', ''),
                    'indicators': ', '.join(check.get('indicators', [])),
                    'required_terms': ', '.join(check.get('required_terms', [])),
                    'severity': check.get('severity', 'Medium'),
                }
                for check in profile.get('semantic_checks', [])
            ], columns=['topic', 'source_id', 'indicators', 'required_terms', 'severity']),
            num_rows='dynamic',
            hide_index=True,
            use_container_width=True,
            key=f'semantic_checks_{profile_id}',
            column_config={
                'topic': st.column_config.TextColumn('Claim topic', required=True),
                'source_id': st.column_config.TextColumn('Approved source ID', required=True),
                'indicators': st.column_config.TextColumn('Paraphrase indicators (comma-separated)', required=True, width='large'),
                'required_terms': st.column_config.TextColumn('Required context (comma-separated)'),
                'severity': st.column_config.SelectboxColumn('Severity', options=['Low', 'Medium', 'High'], required=True, default='Medium'),
            },
        )
        st.caption('Use indicators such as “lower electricity bills, cut power costs, use less energy”. The source ID must exist in Approved sources. Matching is deterministic and explainable; every finding still needs human review.')
        section('Tone checks')
        tone = st.checkbox(
            'Flag repeated exclamation marks',
            value=bool(profile.get('punctuation_source_id')),
        )
        tone_source = st.text_input(
            'Tone source ID',
            value=profile.get('punctuation_source_id', ''),
            help='Must match an ID in Approved sources.',
        )
        submitted = st.form_submit_button('Save brand profile', type='primary')
    if submitted:
        updated = copy.deepcopy(profile)
        updated.update(
            name=name.strip(),
            description=description.strip(),
            sources=remove_empty_rows(sources),
            terms=remove_empty_rows(terms),
            phrases=remove_empty_rows(phrases),
            semantic_checks=[
                {
                    'topic': str(row.get('topic', '')).strip(),
                    'source_id': str(row.get('source_id', '')).strip(),
                    'indicators': [part.strip() for part in str(row.get('indicators', '')).split(',') if part.strip()],
                    'required_terms': [part.strip() for part in str(row.get('required_terms', '')).split(',') if part.strip()],
                    'severity': str(row.get('severity', 'Medium')).strip() or 'Medium',
                }
                for row in remove_empty_rows(semantic_checks)
            ],
        )
        if enabled:
            updated['energy_claim'] = {
                'max_percent': maximum,
                'approved_wording': wording.strip(),
                'source_id': claim_source.strip(),
            }
        else:
            updated.pop('energy_claim', None)
        if tone:
            updated['punctuation_source_id'] = tone_source.strip()
        else:
            updated.pop('punctuation_source_id', None)
        _, succeeded = run_action(db.save_profile, actor, updated, profile_id)
        if succeeded:
            st.session_state['profile_saved'] = True
            st.rerun()


def render_profiles(db, user, run_action):
    hero(
        'THE SOURCE OF CONSISTENCY',
        'One brand. Clear guidance.',
        'Keep approved facts, terminology, and voice rules together so every content review starts from the same foundation.',
    )
    can_edit = user['role'] in ('manager', 'admin')
    st.caption(
        'Existing reviews retain their original guidance snapshot. Start a new review to use profile updates.'
    )
    profiles = db.profiles(user['username'])
    ids = [selected_profile['id'] for selected_profile in profiles]
    if can_edit:
        ids.append('new')
    if not ids:
        st.info('No brand profiles yet. Ask a manager to create one.')
        return
    selected = st.selectbox(
        'Brand profile',
        ids,
        format_func=lambda profile_id: (
            '＋ Create brand profile'
            if profile_id == 'new'
            else next(
                selected_profile['name']
                for selected_profile in profiles
                if selected_profile['id'] == profile_id
            )
        ),
        key='brand_profile_selection',
    )
    selected_profile = next(
        (
            selected_profile
            for selected_profile in profiles
            if selected_profile['id'] == selected
        ),
        None,
    )
    profile = (
        json.loads(selected_profile['body'])
        if selected_profile
        else copy.deepcopy(DEFAULT_PROFILE)
    )
    if st.session_state.pop('profile_saved', False):
        st.success(
            'Brand profile saved. Select it above to view the approved guidance.'
        )
    if selected_profile:
        st.caption(
            f"Profile version {selected_profile['version']} · {'View and manage guidance' if can_edit else 'Read-only access'}"
        )
        show_profile(profile)
        st.download_button(
            'Download brand profile',
            json.dumps(profile, indent=2),
            file_name='brand-profile.json',
            mime='application/json',
        )
        if can_edit:
            with st.expander('Edit brand profile', expanded=False):
                edit_profile(
                    db, user['username'], profile, selected_profile['id'], run_action
                )
    else:
        st.info(
            'Start with the fictional EcoVolt example below. Replace its sources and rules with your own approved guidance before saving.'
        )
        edit_profile(db, user['username'], profile, None, run_action)
