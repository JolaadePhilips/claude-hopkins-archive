#!/usr/bin/env python3
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data' / 'archive.json'

RULES = [
    (r'\bfree\b|free trial|free test|sample', 'Sampling', 'free trial or sampling'),
    (r'coupon|clip this|present this', 'Coupon testing', 'coupon-led response'),
    (r'guarantee|guaranteed|warrant|refund|money back', 'Risk reversal', 'risk reversal'),
    (r'steriliz|purity|pure|filtered|filtering|process|hours|required to make', 'Process proof', 'process detail'),
    (r'doctor|physician|expert|engineer|dealer signs|authority', 'Authority', 'borrowed authority'),
    (r'million|thousand|nations|people use|most popular|every street', 'Social proof', 'social proof'),
    (r'compare|rivals|better than|mistakes|versus| vs\.? ', 'Comparison', 'comparison'),
    (r'why\b|because\b|how\b|reason', 'Reason-why', 'reason-why explanation'),
    (r'\$\s?\d|\d+\s*cents?|\d+%|\d+ hours|\d+ days', 'Specificity', 'specific numbers'),
    (r'test\b|try\b|see for yourself|feel\b|run your tongue', 'Demonstration', 'self-demonstration'),
]

OFFER_PATTERNS = [r'[^\n]{0,90}\bfree\b[^\n]{0,120}', r'[^\n]{0,90}\bcoupon\b[^\n]{0,120}', r'[^\n]{0,90}\btry\b[^\n]{0,120}', r'[^\n]{0,90}\bsend\b[^\n]{0,120}']
PROOF_PATTERNS = [r'[^\n]{0,100}\bsteriliz\w*\b[^\n]{0,140}', r'[^\n]{0,100}\bfiltered?\b[^\n]{0,140}', r'[^\n]{0,100}\btested?\b[^\n]{0,140}', r'[^\n]{0,100}\b\d+\s*(?:hours|days|people|men|women|million|thousand)\b[^\n]{0,140}']


def tidy(s, limit=260):
    s = re.sub(r'\s+', ' ', s or '').strip(' -—|')
    return s[:limit].strip()


def first_match(text, patterns):
    for pattern in patterns:
        m = re.search(pattern, text, re.I)
        if m:
            return tidy(m.group(0))
    return None


def enrich(ad):
    text = ad.get('ocrExcerpt') or ''
    lower = text.lower()
    principles, angles = [], []
    for pattern, principle, angle in RULES:
        if re.search(pattern, lower, re.I):
            if principle not in principles:
                principles.append(principle)
            if angle not in angles:
                angles.append(angle)

    headline = ad.get('headline') or 'Archive advertisement'
    brand = ad.get('brand') or 'Unclassified'
    location = f"volume {ad.get('sourceVolume')}, page {ad.get('sourcePage')}"
    angle_text = ', '.join(angles[:3]) if angles else 'a direct-response execution whose exact selling angle still needs a manual read'

    offer = first_match(text, OFFER_PATTERNS)
    proof = first_match(text, PROOF_PATTERNS)

    ad['principles'] = principles[:6]
    ad['hook'] = (f"OCR suggests {angle_text}." if angles else 'Selling angle not safely inferred from OCR yet.')
    ad['offer'] = offer or 'No offer is safely extractable from the OCR; inspect the original scan.'
    ad['proof'] = proof or 'No proof line is safely extractable from the OCR; inspect the original scan.'
    ad['context'] = (
        f"This {brand} execution is preserved in the Claude Hopkins collection at {location}. "
        f"The OCR reads the lead as “{headline}”. The automated first pass detects {angle_text}."
    )
    if principles:
        ad['whyItWorks'] = (
            f"As a swipe, the useful thing to study is how the execution combines {', '.join(principles[:3])}. "
            "The image remains the primary evidence; this commentary is deliberately marked provisional until the ad is hand-checked."
        )
    else:
        ad['whyItWorks'] = (
            "This scan is included because it belongs to the source Hopkins collection. Its exact persuasion pattern has not yet been safely classified, so the original ad is left to speak first."
        )
    ad['publication'] = f"Original publication not independently verified · archive {location}"
    ad['creditLine'] = (
        f"Historical advertisement from Claude Hopkins Collection, {location}. "
        "Scan collection credited to CopyLegends / Matt Bockenstette public-domain vault. Additional campaign/date sources, where available, are listed below."
    )
    ad['sourceStatus'] = 'Exact scan provenance · OCR-assisted context'
    ad['analysisConfidence'] = 'auto'
    return ad


def main():
    if not MANIFEST.exists():
        raise SystemExit('archive.json not found')
    ads = json.loads(MANIFEST.read_text(encoding='utf-8'))
    if not isinstance(ads, list):
        raise SystemExit('archive.json is not a list')
    ads = [enrich(ad) for ad in ads]
    MANIFEST.write_text(json.dumps(ads, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'enriched {len(ads)} archive records')

if __name__ == '__main__':
    main()
