"""Explicit opt-in fictional demo setup. Never replaces existing accounts."""
from engine import SAMPLE
from brands import SECOND_SAMPLE
from store import Store

def seed():
    db=Store()
    if db.has_users():
        raise SystemExit('Database already contains users. Demo setup stopped without changes.')
    db.bootstrap('AdminDemo!2026')
    for username,name,role in [('creator','Demo Creator','creator'),('reviewer','Demo Reviewer','reviewer'),('manager','Demo Brand Manager','manager')]:
        db.add_user('admin',username,name,role,'BrandShield!2026')
    rid=db.create('creator','October energy campaign',SAMPLE,db.profiles()[0]['id'])
    db.comment('creator',rid,'Fictional campaign sample for the hackathon walkthrough.')
    nova=next(p for p in db.profiles() if p['name']=='NovaWear')
    db.create('creator','NovaWear collection launch',SECOND_SAMPLE,nova['id'])
    print('Demo ready. See README.md for credentials.')
if __name__=='__main__': seed()
