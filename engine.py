"""Deterministic checks: only configured evidence is cited; never execute input."""

import re
import uuid

SAMPLE = 'Meet EcoVolt, the best energy saver! Get 50% savings on every electricity bill. Guaranteed results. Buy now!!!'
DEFAULT_PROFILE = {
    'name': 'EcoVolt',
    'description': 'Fictional energy technology brand for the TECHCIRCUIT Hackathon demo.',
    'sources': [
        {
            'id': 'VOICE-01',
            'title': 'Voice and style',
            'text': 'Use calm, clear language. Avoid repeated exclamation marks.',
        },
        {
            'id': 'TERM-01',
            'title': 'Approved product name',
            'text': 'Write EcoVolt, not Eco Volt or Eco-Volt.',
        },
        {
            'id': 'CLAIM-01',
            'title': 'Approved energy claim',
            'text': 'Up to 15% energy savings under specified laboratory conditions.',
        },
        {
            'id': 'CLAIM-02',
            'title': 'Promotional language',
            'text': 'Avoid guaranteed results and unsupported best-in-market claims.',
        },
    ],
    'terms': [
        {'term': 'Eco Volt', 'replacement': 'EcoVolt', 'source_id': 'TERM-01'},
        {'term': 'Eco-Volt', 'replacement': 'EcoVolt', 'source_id': 'TERM-01'},
    ],
    'phrases': [
        {
            'phrase': 'guaranteed results',
            'replacement': 'Results may vary',
            'source_id': 'CLAIM-02',
            'severity': 'High',
        },
        {
            'phrase': 'the best',
            'replacement': 'an energy-saving',
            'source_id': 'CLAIM-02',
            'severity': 'Medium',
        },
    ],
    'energy_claim': {
        'source_id': 'CLAIM-01',
        'max_percent': 15,
        'approved_wording': 'up to 15% energy savings under specified laboratory conditions',
    },
    'punctuation_source_id': 'VOICE-01',
    'semantic_checks': [
        {
            'topic': 'Energy savings and electricity costs',
            'source_id': 'CLAIM-01',
            'indicators': [
                'energy savings', 'save electricity', 'lower electricity bills',
                'reduce power costs', 'cut household power costs',
                'lower energy costs', 'use less electricity', 'reduce energy use',
                'smaller electricity bills', 'cut power consumption',
            ],
            'required_terms': ['up to', 'laboratory conditions'],
            'severity': 'High',
        },
    ],
}


def validate_profile(profile):
    if (
        not isinstance(profile, dict)
        or not isinstance(profile.get('name'), str)
        or not profile['name'].strip()
    ):
        raise ValueError('A brand name is required.')
    sources = profile.get('sources', [])
    if not isinstance(sources, list) or not sources:
        raise ValueError('Add at least one approved source.')
    if any(
        not isinstance(source, dict)
        or not all(
            isinstance(source.get(field_name), str) and source[field_name].strip()
            for field_name in ('id', 'title', 'text')
        )
        for source in sources
    ):
        raise ValueError('Each source needs an id, title and text.')
    source_ids = [source['id'] for source in sources]
    if len(set(source_ids)) != len(source_ids):
        raise ValueError('Source IDs must be unique.')
    for key, field in [('terms', 'term'), ('phrases', 'phrase')]:
        if not isinstance(profile.get(key, []), list):
            raise ValueError(key + ' must be a list.')
        for rule in profile.get(key, []):
            if (
                not isinstance(rule, dict)
                or not isinstance(rule.get(field), str)
                or not rule[field].strip()
                or not isinstance(rule.get('replacement'), str)
            ):
                raise ValueError(
                    'Rules need a non-empty match and a replacement string.'
                )
            if rule.get('source_id') not in source_ids:
                raise ValueError('Every rule must reference an existing source ID.')
            if key == 'phrases' and rule.get('severity', 'Medium') not in (
                'Low',
                'Medium',
                'High',
            ):
                raise ValueError('Invalid severity.')
    claim = profile.get('energy_claim')
    if claim is not None:
        if (
            not isinstance(claim, dict)
            or claim.get('source_id') not in source_ids
            or not isinstance(claim.get('max_percent'), (int, float))
            or isinstance(claim.get('max_percent'), bool)
            or not 0 <= claim['max_percent'] <= 100
            or not isinstance(claim.get('approved_wording'), str)
            or not claim['approved_wording'].strip()
        ):
            raise ValueError(
                'Energy claim needs a valid source, maximum percent (0–100), and approved wording.'
            )
    if (
        profile.get('punctuation_source_id')
        and profile['punctuation_source_id'] not in source_ids
    ):
        raise ValueError('Invalid punctuation source.')
    semantic_checks = profile.get('semantic_checks', [])
    if not isinstance(semantic_checks, list):
        raise ValueError('semantic_checks must be a list.')
    for check in semantic_checks:
        if (
            not isinstance(check, dict)
            or not isinstance(check.get('topic'), str)
            or not check['topic'].strip()
            or check.get('source_id') not in source_ids
            or not isinstance(check.get('indicators'), list)
            or not check['indicators']
            or any(not isinstance(item, str) or not item.strip() for item in check['indicators'])
            or not isinstance(check.get('required_terms', []), list)
            or any(not isinstance(item, str) or not item.strip() for item in check.get('required_terms', []))
            or check.get('severity', 'Medium') not in ('Low', 'Medium', 'High')
        ):
            raise ValueError('Each semantic check needs a topic, valid source ID, indicators, and valid severity.')
    return profile



# Small synonym groups improve recall without adding a paid model or network dependency.
# Matching remains explainable and deterministic; it is not a general-purpose language model.
_SYNONYM_GROUPS = (
    {'energy', 'electricity', 'power'},
    {'save', 'savings', 'saving', 'reduce', 'reduced', 'reduces', 'cut', 'cuts', 'lower', 'lowering', 'decrease', 'decreases'},
    {'bill', 'bills', 'cost', 'costs', 'expense', 'expenses', 'price', 'prices'},
    {'use', 'usage', 'consumption', 'consume', 'consumes'},
    {'sustainable', 'sustainability', 'eco-friendly', 'environmental', 'environmentally', 'planet', 'green', 'footprint', 'impact'},
    {'best', 'leading', 'number-one', 'top', 'greatest', 'ultimate'},
    {'guarantee', 'guaranteed', 'promise', 'promised', 'certain', 'always'},
)
_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)?", re.I)


def _concept_tokens(text):
    tokens = {token.lower() for token in _TOKEN_RE.findall(text)}
    concepts = set(tokens)
    for group in _SYNONYM_GROUPS:
        if tokens & group:
            concepts.update(group)
    # Common paraphrase forms that are not simple word variants.
    if re.search(r'\b(in half|half as much|by half)\b', text, re.I):
        concepts.update({'50%', 'savings', 'reduce', 'costs'})
    if re.search(r'\b(kinder to the planet|better for the planet|good for the planet)\b', text, re.I):
        concepts.update({'sustainable', 'environmental', 'impact'})
    return concepts


def retrieve_guidance(text, profile, preferred_source_id=None, limit=3):
    """Return approved sources ranked by synonym-aware token relevance."""
    sources = {source['id']: source for source in profile.get('sources', [])}
    query_tokens = _concept_tokens(text)
    ranked = []
    for source in sources.values():
        source_tokens = _concept_tokens(source['title'] + ' ' + source['text'])
        overlap = query_tokens & source_tokens
        # Normalize by query size so long sentences do not swamp the score.
        score = len(overlap) / max(1, len(query_tokens))
        if source['id'] == preferred_source_id:
            score += 1.0
        if score > 0:
            ranked.append((score, source))
    ranked.sort(key=lambda item: (-item[0], item[1]['id']))
    return [
        {'source_id': source['id'], 'title': source['title'], 'text': source['text']}
        for _, source in ranked[:limit]
    ]


def _indicator_matches(sentence, indicator):
    sentence_tokens = _concept_tokens(sentence)
    indicator_tokens = _concept_tokens(indicator)
    # Match when the indicator's meaningful tokens are present after synonym expansion.
    meaningful = {token for token in _TOKEN_RE.findall(indicator.lower()) if len(token) > 2}
    if not meaningful:
        return False
    expanded_meaningful = _concept_tokens(' '.join(meaningful))
    return len(sentence_tokens & expanded_meaningful) >= min(2, len(meaningful))

def analyse(text, profile):
    validate_profile(profile)
    if not isinstance(text, str) or not text.strip():
        raise ValueError('Enter content to review.')
    if len(text) > 50000:
        raise ValueError('Limit content to 50,000 characters.')
    sources = {source['id']: source for source in profile['sources']}
    findings = []

    def add_finding(
        kind, severity, match, explanation, source_id=None, suggestion=None
    ):
        findings.append(
            dict(
                id=str(uuid.uuid4()),
                type=kind,
                severity=severity,
                start=match.start(),
                end=match.end(),
                affected=match.group(),
                explanation=explanation,
                source_id=source_id,
                evidence=(
                    sources[source_id]['text']
                    if source_id
                    else 'No approved source found. Human verification required.'
                ),
                suggestion=suggestion,
                related_sources=(
                    retrieve_guidance(match.group(), profile, source_id)
                    if source_id else retrieve_guidance(match.group(), profile)
                ),
                status='Open',
            )
        )

    for rules, field, kind, severity in [
        (profile.get('terms', []), 'term', 'Terminology', 'Medium'),
        (profile.get('phrases', []), 'phrase', 'Promotional language', 'High'),
    ]:
        for rule in rules:
            for match in re.finditer(
                r'(?<!\w)' + re.escape(rule[field]) + r'(?!\w)', text, re.I
            ):
                add_finding(
                    kind,
                    rule.get('severity', severity),
                    match,
                    'This wording conflicts with the configured brand guideline.',
                    rule['source_id'],
                    rule['replacement'],
                )
    if profile.get('punctuation_source_id'):
        for match in re.finditer(r'!{2,}', text):
            add_finding(
                'Tone',
                'Low',
                match,
                'Repeated exclamation marks conflict with the approved voice.',
                profile['punctuation_source_id'],
                '!',
            )
    # Keep positions in the original text so findings highlight the correct passage.
    percentage_pattern = re.compile(r'\b\d+(?:\.\d+)?\s*%')
    for sentence in re.finditer(r'(?:[^.!?\n]|(?<=\d)\.(?=\d))+', text):
        sentence_text = sentence.group()
        if not re.search(r'\b(savings?|electricity bills?)\b', sentence_text, re.I):
            continue
        for percentage_match in percentage_pattern.finditer(
            text, sentence.start(), sentence.end()
        ):
            claim = profile.get('energy_claim')
            if not claim:
                add_finding(
                    'Unverified claim',
                    'Medium',
                    percentage_match,
                    'No structured energy-savings limit is configured. This is unverified, not proven false.',
                )
                # Retrieve context from the full sentence, not just the percentage token.
                findings[-1]['related_sources'] = retrieve_guidance(sentence_text, profile)
            elif (
                float(percentage_match.group().replace('%', '').strip())
                > claim['max_percent']
            ):
                add_finding(
                    'Claim conflict',
                    'High',
                    percentage_match,
                    'This percentage exceeds the approved energy-savings maximum. Revise the whole claim to preserve its conditions.',
                    claim['source_id'],
                )
            elif not all(
                part in sentence_text.lower()
                for part in ['up to', 'laboratory', 'conditions']
            ) or re.search(r'\b(every|guaranteed|always)\b', sentence_text, re.I):
                add_finding(
                    'Claim qualification',
                    'High',
                    percentage_match,
                    'The percentage needs the approved qualifications and must not imply guaranteed bill savings. Use the approved wording shown below.',
                    claim['source_id'],
                )
    # No evidence: tag superlatives as requiring verification rather than declaring them false.
    for match in re.finditer(
        r'\b(?:number\s*(?:one|1)|100%\s+(?:safe|effective)|clinically proven)\b',
        text,
        re.I,
    ):
        add_finding(
            'Unverified claim',
            'Medium',
            match,
            'Evidence for this statement is not configured. Ask a reviewer to verify it.',
        )

    # Source-grounded semantic checks: match configured concepts and paraphrases,
    # then attach the approved source and nearby guidance for a human to assess.
    for sentence in re.finditer(r'[^.!?\n]+(?:[.!?]+|$)', text):
        sentence_text = sentence.group().strip()
        if not sentence_text:
            continue
        leading_offset = len(sentence.group()) - len(sentence.group().lstrip())
        sentence_start = sentence.start() + leading_offset
        already_flagged = any(
            finding['start'] < sentence.end() and finding['end'] > sentence_start
            for finding in findings
        )
        if already_flagged:
            continue
        for check in profile.get('semantic_checks', []):
            if not any(_indicator_matches(sentence_text, indicator) for indicator in check['indicators']):
                continue
            # Only treat this as a claim if it asserts or promotes the topic; a source
            # mention or neutral question should not automatically become a violation.
            if not re.search(r'\b(?:save|saves|saving|savings|cut|cuts|reduce|reduces|lower|lowers|less|half|best|leading|sustainable|eco-friendly|green|planet|impact|guarantee|guaranteed|proven|zero)\b', sentence_text, re.I):
                continue
            claim = profile.get('energy_claim') if check['topic'].lower().startswith('energy') else None
            required_terms = check.get('required_terms', [])
            has_required_context = all(
                any(part in sentence_text.lower() for part in term.lower().split(' / '))
                for term in required_terms
            ) if required_terms else False
            explanation = (
                f'This wording appears to make a {check["topic"].lower()} claim using a paraphrase. '
                'The approved guidance below is relevant, but it does not by itself prove this exact wording. '
                'Check the claim, scope, conditions and evidence before approval.'
            )
            if claim and has_required_context:
                continue
            match = re.search(r'\S+', text[sentence_start:sentence.end()])
            if not match:
                continue
            # Highlight the sentence so a reviewer sees the full paraphrased claim.
            start = sentence_start
            end = start + len(sentence_text)
            class _SentenceMatch:
                def start(self): return start
                def end(self): return end
                def group(self): return text[start:end].strip()
            add_finding(
                'Semantic claim review',
                check.get('severity', 'Medium'),
                _SentenceMatch(),
                explanation,
                check['source_id'],
                None,
            )
            break

    # Claims that have no configured semantic check still get an explicit evidence gap.
    # Do not label them false: the finding asks a person to verify supporting material.
    known_topics = [
        r'\b(?:save|saves|saving|savings|cut|cuts|reduce|reduces|lower|lowers)\b.{0,50}\b(?:costs?|bills?|energy|electricity|power)\b',
        r'\b(?:clinically proven|number\s*(?:one|1)|best-in-market|guaranteed results)\b',
    ]
    for sentence in re.finditer(r'[^.!?\n]+(?:[.!?]+|$)', text):
        sentence_text = sentence.group().strip()
        if not sentence_text or any(f['start'] < sentence.end() and f['end'] > sentence.start() for f in findings):
            continue
        if any(re.search(pattern, sentence_text, re.I) for pattern in known_topics):
            related = retrieve_guidance(sentence_text, profile)
            if not related:
                start = sentence.start() + len(sentence.group()) - len(sentence.group().lstrip())
                end = start + len(sentence_text)
                class _UnverifiedMatch:
                    def start(self): return start
                    def end(self): return end
                    def group(self): return text[start:end].strip()
                add_finding(
                    'Missing evidence', 'Medium', _UnverifiedMatch(),
                    'This claim-like wording has no relevant approved source in the brand profile. Add evidence or ask a reviewer to verify it; it is not automatically false.'
                )
    return sorted(findings, key=lambda finding: finding['start'])


def apply_suggestion(text, finding):
    start, end = finding['start'], finding['end']
    if text[start:end] != finding['affected']:
        raise ValueError('Content changed. Reanalyse before applying this suggestion.')
    if finding.get('suggestion') is None:
        raise ValueError('This finding needs a manual revision.')
    return text[:start] + finding['suggestion'] + text[end:]
