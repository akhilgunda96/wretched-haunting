"""Headless Streamlit screen checks; uses isolated temporary storage."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from store import Store
try:
    from streamlit.testing.v1 import AppTest
except ImportError:
    AppTest=None

@unittest.skipUnless(AppTest,'Install requirements.txt to run Streamlit screen checks')
class ScreenTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old=os.environ.get('BRANDSHIELD_DB')
        os.environ['BRANDSHIELD_DB']=str(Path(self.tmp.name)/'ui.db')
        self.db=Store(); self.db.bootstrap('admin-password!')
        self.db.add_user('admin','creator','Creator','creator','creator-password!')
        self.db.add_user('admin','reviewer','Reviewer','reviewer','reviewer-password!')
    def tearDown(self):
        if self.old is None: os.environ.pop('BRANDSHIELD_DB',None)
        else: os.environ['BRANDSHIELD_DB']=self.old
        self.tmp.cleanup()
    def app(self,user,pw):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=15).run()
        app.text_input[0].input(user); app.text_input[1].input(pw)
        app.button[0].click().run()
        self.assertEqual(len(app.exception),0)
        return app
    def test_creator_screens_and_save(self):
        app=self.app('creator','creator-password!')
        app.sidebar.radio[0].set_value('New review').run()
        app.text_input[0].input('UI campaign')
        app.text_area[0].input('Eco Volt offers 50% energy savings!!!')
        next(b for b in app.button if b.label=='Analyse & save draft').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(self.db.list_reviews('creator')),1)
        app.sidebar.radio[0].set_value('Reviews').run()
        self.assertEqual(len(app.exception),0)
        next(b for b in app.button if b.label=='Apply & reanalyse').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(self.db.list_reviews('creator')[0]['version'],2)
        next(b for b in app.button if b.label=='Request approval').click().run()
        self.assertEqual(self.db.list_reviews('creator')[0]['status'],'Pending review')
    def test_reviewer_approval(self):
        rid=self.db.create('creator','Good campaign','Hello from EcoVolt',self.db.profiles()[0]['id'])
        self.db.transition('creator',rid,'Submit','Ready',1)
        app=self.app('reviewer','reviewer-password!')
        app.sidebar.radio[0].set_value('Reviews').run()
        next(t for t in app.text_area if t.label=='Comment or decision explanation').input('Approved against configured evidence.')
        next(b for b in app.button if b.label=='Approve').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(self.db.detail('reviewer',rid)['status'],'Approved')
    def test_admin_profile_and_users_screens(self):
        app=self.app('admin','admin-password!')
        for page in ('Brand profiles','Users','Overview'):
            app.sidebar.radio[0].set_value(page).run()
            self.assertEqual(len(app.exception),0)
    def test_reviewer_profile_is_readable_and_read_only(self):
        app=self.app('reviewer','reviewer-password!')
        app.sidebar.radio[0].set_value('Brand profiles').run()
        self.assertEqual(len(app.exception),0)
        self.assertNotIn('new',app.selectbox[0].options)
        self.assertEqual(len(app.json),0)
        self.assertFalse(any(b.label=='Save brand profile' for b in app.button))
        self.assertTrue(any('Approved energy claim' in m.value for m in app.markdown))
    def test_admin_can_create_profile_with_form(self):
        app=self.app('admin','admin-password!')
        app.sidebar.radio[0].set_value('Brand profiles').run()
        app.selectbox[0].set_value('new').run()
        self.assertEqual(len(app.exception),0)
        next(t for t in app.text_input if t.label=='Brand name').input('SolarNova')
        next(b for b in app.button if b.label=='Save brand profile').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertIn('SolarNova',[p['name'] for p in self.db.profiles()])
    def test_admin_can_edit_profile_with_form(self):
        app=self.app('admin','admin-password!')
        app.sidebar.radio[0].set_value('Brand profiles').run()
        next(t for t in app.text_input if t.label=='Brand name').input('EcoVolt Revised')
        next(b for b in app.button if b.label=='Save brand profile').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(self.db.profiles()[0]['name'],'EcoVolt Revised')
        self.assertEqual(self.db.profiles()[0]['version'],2)
    def test_dashboard_actions_navigate_to_real_screens(self):
        app=self.app('admin','admin-password!')
        self.assertTrue(any('Big ideas.' in m.value for m in app.markdown))
        next(b for b in app.button if b.label=='＋ Start a review').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(app.sidebar.radio[0].value,'New review')
        app.sidebar.radio[0].set_value('Overview').run()
        next(b for b in app.button if b.label=='Browse brand profiles').click().run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(app.sidebar.radio[0].value,'Brand profiles')
if __name__=='__main__': unittest.main()
