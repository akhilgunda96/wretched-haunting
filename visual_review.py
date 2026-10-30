"""Local, explainable visual checks for promotional images."""
from __future__ import annotations

from collections import Counter
from io import BytesIO
import math

import cv2
import numpy as np
from PIL import Image, ImageOps
import pytesseract
from pytesseract import Output

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_SIDE = 3000


def _open_image(data: bytes) -> Image.Image:
    if not data:
        raise ValueError('Upload an image to review.')
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError('Image limit: 8 MB.')
    try:
        image = Image.open(BytesIO(data))
        image = ImageOps.exif_transpose(image).convert('RGBA')
        background = Image.new('RGBA', image.size, (255, 255, 255, 255))
        image = Image.alpha_composite(background, image).convert('RGB')
    except Exception as exc:
        raise ValueError('The uploaded file is not a supported image.') from exc
    if image.width > MAX_IMAGE_SIDE or image.height > MAX_IMAGE_SIDE:
        raise ValueError('Image dimensions must be 3000 × 3000 pixels or smaller.')
    return image


def parse_palette(value: str) -> list[tuple[int, int, int]]:
    """Parse comma-separated hex colours, e.g. #123456, #F5F5F5."""
    colors = []
    for item in (value or '').split(','):
        item = item.strip().lstrip('#')
        if not item:
            continue
        if len(item) != 6 or any(char not in '0123456789abcdefABCDEF' for char in item):
            raise ValueError('Enter brand colours as six-digit hex values, e.g. #123456, #FFFFFF.')
        colors.append(tuple(int(item[index:index + 2], 16) for index in (0, 2, 4)))
    if not colors:
        raise ValueError('Add at least one approved brand colour.')
    return colors


def _rgb_distance(first, second) -> float:
    return math.sqrt(sum((int(a) - int(b)) ** 2 for a, b in zip(first, second)))


def _luminance(rgb) -> float:
    values = []
    for channel in rgb:
        channel = channel / 255
        values.append(channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4)
    return 0.2126 * values[0] + 0.7152 * values[1] + 0.0722 * values[2]


def contrast_ratio(first, second) -> float:
    light, dark = sorted((_luminance(first), _luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def _region_contrast(region: Image.Image) -> tuple[float | None, tuple[int, int, int] | None, tuple[int, int, int] | None]:
    """Estimate text/background contrast from the two most common quantized colours."""
    small = region.convert('RGB').resize((max(1, min(region.width, 160)), max(1, min(region.height, 80))))
    quantized = small.quantize(colors=8).convert('RGB')
    pixels = list(quantized.getdata())
    counts = Counter(pixels)
    if len(counts) < 2:
        return None, None, None
    background = counts.most_common(1)[0][0]
    candidates = [color for color, _ in counts.most_common() if _rgb_distance(color, background) >= 35]
    if not candidates:
        return None, background, None
    text_color = max(candidates, key=lambda color: _rgb_distance(color, background))
    return contrast_ratio(background, text_color), background, text_color


def _find_logo(image: Image.Image, logo: Image.Image) -> tuple[bool, float, tuple[int, int, int, int] | None]:
    """Search for an approved logo at several sizes using local OpenCV template matching."""
    canvas = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    template_rgb = logo.convert('RGB')
    template = cv2.cvtColor(np.array(template_rgb), cv2.COLOR_RGB2GRAY)
    image_h, image_w = canvas.shape
    logo_h, logo_w = template.shape
    if logo_w < 12 or logo_h < 12:
        return False, 0.0, None
    best_score, best_box = 0.0, None
    # Only consider plausible logo sizes; the largest template is bounded by the uploaded image.
    for scale in (0.25, 0.35, 0.5, 0.65, 0.8, 1.0, 1.25, 1.5, 2.0):
        width, height = int(logo_w * scale), int(logo_h * scale)
        if width < 12 or height < 12 or width > image_w or height > image_h:
            continue
        resized = cv2.resize(template, (width, height), interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
        if float(np.std(resized)) < 1.0:
            continue
        result = cv2.matchTemplate(canvas, resized, cv2.TM_CCOEFF_NORMED)
        _, score, _, location = cv2.minMaxLoc(result)
        if score > best_score:
            best_score = float(score)
            x, y = location
            best_box = (x, y, x + width, y + height)
    return best_score >= 0.78, best_score, best_box


def review_image(image_bytes: bytes, palette_text: str, approved_logo_bytes: bytes | None = None) -> dict:
    """Extract image text and report configured palette, contrast, and logo findings."""
    image = _open_image(image_bytes)
    palette = parse_palette(palette_text)
    findings = []
    # Report prominent saturated colours outside the configured palette, avoiding tiny noise.
    quantized = image.resize((min(240, image.width), min(240, image.height))).quantize(colors=12)
    palette_image = quantized.convert('RGB')
    counts = Counter(palette_image.getdata())
    total = max(1, sum(counts.values()))
    off_brand = []
    for color, count in counts.most_common(12):
        share = count / total
        if share < 0.08:
            continue
        saturation = max(color) - min(color)
        nearest = min(palette, key=lambda approved: _rgb_distance(color, approved))
        distance = _rgb_distance(color, nearest)
        if distance > 70 and saturation > 30:
            off_brand.append({'color': '#%02X%02X%02X' % color, 'share': round(share * 100, 1), 'nearest_approved': '#%02X%02X%02X' % nearest})
    if off_brand:
        findings.append({
            'type': 'Brand colour', 'severity': 'Medium', 'region': 'Image-wide prominent colours',
            'explanation': 'Prominent colours differ from the configured brand palette. Review the listed colours; photography and decorative backgrounds may be intentional.',
            'details': off_brand,
        })

    try:
        ocr = pytesseract.image_to_data(image, output_type=Output.DICT, config='--psm 11')
    except Exception as exc:
        raise RuntimeError('Text extraction failed. Install the Tesseract OCR engine and try again.') from exc
    extracted = []
    for index, raw_text in enumerate(ocr.get('text', [])):
        text = raw_text.strip()
        try:
            confidence = float(ocr['conf'][index])
        except (ValueError, TypeError, KeyError):
            confidence = -1
        if not text or confidence < 35:
            continue
        x, y = int(ocr['left'][index]), int(ocr['top'][index])
        w, h = int(ocr['width'][index]), int(ocr['height'][index])
        if w <= 0 or h <= 0:
            continue
        box = (x, y, min(image.width, x + w), min(image.height, y + h))
        extracted.append({'text': text, 'confidence': round(confidence, 1), 'box': box})
        ratio, background, text_color = _region_contrast(image.crop(box))
        if ratio is not None and ratio < 4.5:
            findings.append({
                'type': 'Text contrast', 'severity': 'High' if ratio < 3 else 'Medium',
                'region': f'Text region x={x}, y={y}, width={w}, height={h}',
                'text': text,
                'explanation': f'Estimated contrast is {ratio:.2f}:1, below the 4.5:1 target for normal text. Check this text region manually; the local colour estimate is approximate.',
                'contrast_ratio': round(ratio, 2),
                'estimated_background': '#%02X%02X%02X' % background if background else None,
                'estimated_text_colour': '#%02X%02X%02X' % text_color if text_color else None,
                'box': box,
            })

    logo_result = None
    if approved_logo_bytes:
        approved_logo = _open_image(approved_logo_bytes)
        found, score, box = _find_logo(image, approved_logo)
        logo_result = {'found': found, 'similarity': round(score, 3), 'box': box}
        if not found:
            findings.append({
                'type': 'Approved logo asset', 'severity': 'High', 'region': 'Logo not located in image',
                'explanation': f'The uploaded approved logo was not confidently matched in this image (best template similarity {score:.2f}; threshold 0.78). The logo may be missing, resized unusually, recoloured, or altered. Verify manually.',
                'similarity': round(score, 3),
            })
        else:
            findings.append({
                'type': 'Approved logo asset', 'severity': 'Low',
                'region': f'Logo region x={box[0]}, y={box[1]}, width={box[2]-box[0]}, height={box[3]-box[1]}',
                'explanation': f'The approved logo appears to match this region (similarity {score:.2f}). Confirm placement and clear space manually.',
                'similarity': round(score, 3), 'box': box,
            })

    return {
        'width': image.width, 'height': image.height,
        'extracted_text': extracted, 'findings': findings, 'logo': logo_result,
        'note': 'OCR, colour sampling, contrast estimation and logo template matching are automated heuristics. Review every result manually; no image is approved automatically.',
    }
