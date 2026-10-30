"""Regression checks for text positions and profile editor row handling."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import DEFAULT_PROFILE, analyse


class RefactorTests(unittest.TestCase):
    def test_percentages_keep_original_text_positions(self):
        cases = [
            ('Intro. 50% energy savings.', ['50%']),
            ('Énergie ⚡. 15.5% savings!', ['15.5%']),
            ('50% savings. Next: 25% savings.', ['50%', '25%']),
            ('Notice!\n50 % electricity bill savings.', ['50 %']),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                findings = analyse(text, DEFAULT_PROFILE)
                self.assertEqual(
                    [finding['affected'] for finding in findings], expected
                )
                for finding in findings:
                    start, end = finding['start'], finding['end']
                    self.assertEqual(text[start:end], finding['affected'])
                    self.assertEqual(start, text.index(finding['affected']))

    def test_empty_editor_rows_removed_but_partial_rows_preserved(self):
        try:
            import pandas as pd
            from profiles_ui import remove_empty_rows
        except ImportError:
            self.skipTest('Install requirements.txt for the profile editor check')
        rows = [
            {'id': '', 'title': None, 'text': ' '},
            {'id': 'SOURCE-01', 'title': '', 'text': ''},
        ]
        self.assertEqual(remove_empty_rows(rows), [rows[1]])
        expected = [{'id': 'SOURCE-01', 'title': '', 'text': ''}]
        self.assertEqual(remove_empty_rows(pd.DataFrame(rows)), expected)


if __name__ == '__main__':
    unittest.main()
