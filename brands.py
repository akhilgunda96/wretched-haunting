"""Fictional sample brands; these are illustrative, not real brand claims."""
from engine import DEFAULT_PROFILE, SAMPLE

SECOND_PROFILE = {
    'name': 'NovaWear',
    'description': 'Fictional everyday apparel brand. Friendly, clear and practical language, with no unsupported sustainability claims.',
    'sources': [
        {'id':'NW-VOICE-01','title':'Brand voice','text':'Use friendly, clear language. Avoid repeated exclamation marks and pressure-based sales wording.'},
        {'id':'NW-TERM-01','title':'Approved brand name','text':'Write NovaWear as one word, with capital N and W. Do not use Nova Wear or Nova-Wear.'},
        {'id':'NW-CLAIM-01','title':'Sustainability guidance','text':'Do not describe the collection as 100% sustainable or zero impact. No sustainability certification or environmental performance evidence is configured for this demo.'},
        {'id':'NW-COPY-01','title':'Promotional language','text':'Avoid best quality and buy now or regret it. Use practical descriptions and inviting calls to action.'}
    ],
    'terms': [
        {'term':'Nova Wear','replacement':'NovaWear','source_id':'NW-TERM-01'},
        {'term':'Nova-Wear','replacement':'NovaWear','source_id':'NW-TERM-01'}
    ],
    'phrases': [
        {'phrase':'100% sustainable','replacement':'made for everyday wear','source_id':'NW-CLAIM-01','severity':'High'},
        {'phrase':'zero impact','replacement':'an everyday wardrobe option','source_id':'NW-CLAIM-01','severity':'High'},
        {'phrase':'best quality','replacement':'everyday essentials','source_id':'NW-COPY-01','severity':'Medium'},
        {'phrase':'buy now or regret it','replacement':'Explore the collection','source_id':'NW-COPY-01','severity':'Medium'}
    ],
    'punctuation_source_id':'NW-VOICE-01',
    'semantic_checks': [
        {
            'topic': 'Environmental and sustainability claims',
            'source_id': 'NW-CLAIM-01',
            'indicators': [
                'sustainable clothing', 'kinder to the planet', 'better for the planet',
                'environmentally friendly', 'eco-friendly clothing', 'green fashion',
                'zero environmental impact', 'carbon neutral clothing',
                'no environmental footprint',
            ],
            'required_terms': [],
            'severity': 'High',
        },
    ],
}
SECOND_SAMPLE = 'Meet Nova Wear: best quality, 100% sustainable clothing with zero impact. Buy now or regret it!!!'
BRAND_SAMPLES = {DEFAULT_PROFILE['name']: SAMPLE, SECOND_PROFILE['name']: SECOND_SAMPLE}
