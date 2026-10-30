import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from engine import analyse, DEFAULT_PROFILE
from brands import SECOND_PROFILE, SECOND_SAMPLE
from store import Store

class TwoBrandTests(unittest.TestCase):
    def test_novawear_uses_own_evidence(self):
        findings=analyse(SECOND_SAMPLE,SECOND_PROFILE)
        self.assertEqual(len(findings),6)
        self.assertTrue(all(f['source_id'].startswith('NW-') for f in findings))
        self.assertTrue(any(f['affected']=='Nova Wear' for f in findings))
        self.assertEqual(analyse('NovaWear everyday essentials. Explore the collection.',SECOND_PROFILE),[])
    def test_rules_are_separate(self):
        self.assertEqual(analyse(SECOND_SAMPLE.replace('!!!','.'),DEFAULT_PROFILE),[])
        self.assertEqual(analyse('Eco Volt',SECOND_PROFILE),[])
    def test_seeding_is_once_and_preserves_edits(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'brands.db'; db=Store(path)
            self.assertEqual({p['name'] for p in db.profiles()},{'EcoVolt','NovaWear'})
            db.bootstrap('administrator!pass')
            nova=next(p for p in db.profiles() if p['name']=='NovaWear')
            edited=copy.deepcopy(SECOND_PROFILE); edited['description']='Our custom guidance'
            db.save_profile('admin',edited,nova['id'])
            reopened=Store(path)
            self.assertEqual(len(reopened.profiles()),2)
            current=next(p for p in reopened.profiles() if p['name']=='NovaWear')
            self.assertEqual(json.loads(current['body'])['description'],'Our custom guidance')
    def test_existing_installation_upgrade(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'old.db'; db=Store(path)
            with db.db() as c:
                c.execute("DELETE FROM profiles WHERE name='NovaWear'")
                c.execute('DROP TABLE migrations')
            db=Store(path)
            self.assertEqual(len(db.profiles()),2)
            self.assertEqual(next(p for p in db.profiles() if p['name']=='EcoVolt')['version'],1)
    def test_semantic_review_migration_preserves_existing_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'older.db'; db=Store(path)
            with db.db() as c:
                row=c.execute("SELECT id,body FROM profiles WHERE name='EcoVolt'").fetchone()
                body=json.loads(row['body']); body.pop('semantic_checks',None)
                body['description']='Keep my existing description'
                c.execute('UPDATE profiles SET body=? WHERE id=?',(json.dumps(body),row['id']))
                c.execute("DELETE FROM migrations WHERE key='semantic-review-v1'")
            reopened=Store(path)
            body=json.loads(next(p for p in reopened.profiles() if p['name']=='EcoVolt')['body'])
            self.assertEqual(body['description'],'Keep my existing description')
            self.assertEqual(body['semantic_checks'][0]['source_id'],'CLAIM-01')
if __name__=='__main__': unittest.main()
