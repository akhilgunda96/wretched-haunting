from io import BytesIO
from pathlib import Path
import sys
import unittest

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from visual_review import contrast_ratio, parse_palette, review_image


def image_bytes(image):
    stream = BytesIO()
    image.save(stream, format='PNG')
    return stream.getvalue()


class VisualReviewTests(unittest.TestCase):
    def test_parse_palette(self):
        self.assertEqual(parse_palette('#000000, #FFFFFF'), [(0, 0, 0), (255, 255, 255)])

    def test_invalid_palette_rejected(self):
        with self.assertRaises(ValueError):
            parse_palette('green')

    def test_contrast_ratio_black_white(self):
        self.assertAlmostEqual(contrast_ratio((0, 0, 0), (255, 255, 255)), 21.0, places=1)

    def test_invalid_image_rejected(self):
        with self.assertRaises(ValueError):
            review_image(b'not an image', '#000000, #FFFFFF')

    def test_image_review_returns_region_data(self):
        image = Image.new('RGB', (640, 220), '#FFFFFF')
        draw = ImageDraw.Draw(image)
        draw.text((30, 70), 'SALE 50% OFF', fill='#BBBBBB', stroke_width=0)
        result = review_image(image_bytes(image), '#176B45, #FFFFFF')
        self.assertIn('extracted_text', result)
        self.assertIn('findings', result)
        self.assertTrue(all('region' in finding and 'explanation' in finding for finding in result['findings']))

    def test_logo_asset_check_reports_match(self):
        logo = Image.new('RGB', (120, 50), '#FFFFFF')
        draw = ImageDraw.Draw(logo)
        draw.rectangle((5, 5, 40, 40), fill='#176B45')
        draw.text((48, 15), 'BRAND', fill='#000000')
        promo = Image.new('RGB', (500, 300), '#EEEEEE')
        promo.paste(logo, (40, 35))
        result = review_image(image_bytes(promo), '#176B45, #FFFFFF', image_bytes(logo))
        self.assertIsNotNone(result['logo'])
        self.assertTrue(result['logo']['found'])


if __name__ == '__main__':
    unittest.main()
