import unittest
import pdb
from datetime import datetime
from persistence.instance_collection import InstanceObjectMapper
from models import Instance, Page, Revision, Guest, RegisteredUser, User

def _make_revision(rev_id):
    return Revision(rev_id=rev_id,
                    user=RegisteredUser(100, "Some User"),
                    timestamp=datetime.utcnow(),
                    comment="abcd",
                    is_minor=True,
                    is_reviewed=False)

class TestInstanceObjectMapper(unittest.TestCase):
    def test_registered_user(self):
        u = RegisteredUser(1, "Test User")
        r = InstanceObjectMapper._user_to_dict(u)
        user_again = InstanceObjectMapper._user_from_dict(r)
        
        self.assertEqual(user_again, u)

    def test_registered_user_not_equal(self):
        u = RegisteredUser(1, "Test User")
        u2 = RegisteredUser(2, "Test User")
        
        r = InstanceObjectMapper._user_to_dict(u)
        user_again = InstanceObjectMapper._user_from_dict(r)
        
        self.assertNotEqual(user_again, u2)

    def test_guest(self):
        g = Guest("127.0.0.1")
        conv = InstanceObjectMapper._user_to_dict(g)
        g_again = InstanceObjectMapper._user_from_dict(conv)

        self.assertEqual(g, g_again)

    def test_revision(self):
        rev = _make_revision(1)
        r_dict = InstanceObjectMapper._revision_to_dict(rev)
        r_again = InstanceObjectMapper._revision_from_dict(r_dict)

        self.assertEqual(rev, r_again)

    def test_revision_not_equal(self):
        rev = _make_revision(1)
        rev2 = _make_revision(2)
        rev2.comment = "Some unexpected comment"
        
        r_dict = InstanceObjectMapper._revision_to_dict(rev)
        r_again = InstanceObjectMapper._revision_from_dict(r_dict)

        self.assertNotEqual(rev2, r_again)

    def test_page(self):
        pg = Page(1, "Main", 0)

        p_dict = InstanceObjectMapper._page_to_dict(pg)
        p_again = InstanceObjectMapper._page_from_dict(p_dict)

        self.assertEqual(pg, p_again)

    def test_page_not_equal(self):
        pg = Page(1, "Main", 0)
        pg2 = Page(2, "Main2", 1)
        
        p_dict = InstanceObjectMapper._page_to_dict(pg)
        p_again = InstanceObjectMapper._page_from_dict(p_dict)

        self.assertNotEqual(pg2, p_again)
        

if __name__ == '__main__':
    unittest.main()
