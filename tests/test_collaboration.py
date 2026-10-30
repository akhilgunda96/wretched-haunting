import json
import os
import tempfile
import unittest

from store import Store


class CollaborationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Store(os.path.join(self.tmp.name, 'brandshield.sqlite3'))
        self.db.bootstrap('LongAdminPassword!2026')

    def tearDown(self):
        self.tmp.cleanup()

    def test_organisation_isolation_and_assignment_notifications(self):
        self.db.create_organization('admin', 'North Team')
        org = next(o for o in self.db.organizations('admin') if o['name'] == 'North Team')
        org_id = org['id']
        self.db.add_user('admin', 'north_manager', 'North Manager', 'manager', 'NorthManagerPass!2026', org_id)
        self.db.add_user('admin', 'north_creator', 'North Creator', 'creator', 'NorthCreatorPass!2026', org_id)
        self.db.add_user('admin', 'north_reviewer', 'North Reviewer', 'reviewer', 'NorthReviewerPass!2026', org_id)

        profile = json.loads(self.db.profiles('admin')[0]['body'])
        profile['name'] = 'North Team Brand'
        self.db.save_profile('north_manager', profile)
        profile_row = self.db.profiles('north_manager')[0]
        rid = self.db.create('north_creator', 'North campaign', 'EcoVolt helps households save energy.', profile_row['id'])
        self.db.assign_review('north_manager', rid, 'north_reviewer')
        self.db.transition('north_creator', rid, 'Submit', 'Ready for review', 1)

        notices = self.db.notifications('north_reviewer')
        self.assertTrue(any('assigned to you' in n['message'] for n in notices))
        self.assertTrue(any('ready for your review' in n['message'] for n in notices))
        self.assertEqual(self.db.list_reviews('north_creator')[0]['organization_id'], org_id)
        self.assertEqual(self.db.list_reviews('admin'), [])
        with self.assertRaises(ValueError):
            self.db.detail('admin', rid)
        self.assertEqual(self.db.profiles('admin')[0]['name'], 'EcoVolt')

    def test_notifications_persist_after_store_reopen(self):
        self.db.create_organization('admin', 'Persist Team')
        org = next(o for o in self.db.organizations('admin') if o['name'] == 'Persist Team')
        self.db.add_user('admin', 'persist_manager', 'Persist Manager', 'manager', 'PersistManagerPass!2026', org['id'])
        reopened = Store(self.db.path)
        self.assertEqual(reopened.authenticate('persist_manager', 'PersistManagerPass!2026')['organization_id'], org['id'])
        self.assertEqual(reopened.notifications('persist_manager'), [])


if __name__ == '__main__':
    unittest.main()
