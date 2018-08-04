import unittest
import dateutil.parser
from mediawiki.integration import MediaWikiIntegration, MediaWikiObjectConversion, BadRevisionIdException
from datetime import datetime
from persistence.instance_collection import InstanceObjectMapper
from models import Instance, Page, Revision, Guest, RegisteredUser, User

class MediaWikiApiMock:        
    def __init__(self):
        self.query_revisions_by_ids_resp = {}
    def query_revisions_by_ids(self, page_ids: int, rvprop: list, rvlimit: int = 10):
        return self.query_revisions_by_ids_resp

SAMPLE_REVISION_REGISTERED_USER_RAW = {
    "revid": 2345,
    "parentid": 2344,
    "minor": "",
    "user": "SomeUser",
    "userid": 12345,
    "timestamp": "2007-02-17T12:00:00Z",
    "comment": "some comment"
}

SAMPLE_REVISION_REGISTERED_USER_OBJ = Revision(rev_id=2345,
                                               user=RegisteredUser(12345, "SomeUser"),
                                               timestamp=dateutil.parser.parse("2007-02-17T12:00:00Z"),
                                               comment="some comment",
                                               is_minor=True,
                                               is_reviewed=False)

SAMPLE_REVISION_GUEST_RAW = {
    "revid": 2345,
    "parentid": 2344,
    "minor": "",
    "user": "127.0.0.1",
    "anon": "",
    "timestamp": "2007-02-17T12:00:00Z",
    "comment": "some comment"
}

SAMPLE_REVISION_GUEST_OBJ = Revision(rev_id=2345,
                                     user=Guest("127.0.0.1"),
                                     timestamp=dateutil.parser.parse("2007-02-17T12:00:00Z"),
                                     comment="some comment",
                                     is_minor=True,
                                     is_reviewed=False)



class TestMediaWikiIntegration(unittest.TestCase):
    def test_registered_user_revision_conversion(self):
        rev = MediaWikiObjectConversion.convert_revision(SAMPLE_REVISION_REGISTERED_USER_RAW)
        obj = SAMPLE_REVISION_REGISTERED_USER_OBJ

        self.assertEqual(rev.rev_id, obj.rev_id, "rev_id is not equal")
        self.assertEqual(rev.user, obj.user, "user is not equal")
        self.assertEqual(rev.timestamp, obj.timestamp, "timestamp is not equal")
        self.assertEqual(rev.comment, obj.comment, "comment is not equal")
        self.assertEqual(rev.is_minor, obj.is_minor, "is_minor is not equal")
        self.assertEqual(rev.is_reviewed, obj.is_reviewed, "is_reviewed is not equal")

    def test_guest_revision_conversion(self):
        rev = MediaWikiObjectConversion.convert_revision(SAMPLE_REVISION_GUEST_RAW)
        obj = SAMPLE_REVISION_GUEST_OBJ

        self.assertEqual(rev.rev_id, obj.rev_id, "rev_id is not equal")
        self.assertEqual(rev.user, obj.user, "user is not equal")
        self.assertEqual(rev.timestamp, obj.timestamp, "timestamp is not equal")
        self.assertEqual(rev.comment, obj.comment, "comment is not equal")
        self.assertEqual(rev.is_minor, obj.is_minor, "is_minor is not equal")
        self.assertEqual(rev.is_reviewed, obj.is_reviewed, "is_reviewed is not equal")
        
        
    def test_single_revision_instance_registered(self):
        api = MediaWikiApiMock()
        integration = MediaWikiIntegration(api)
        
        api.query_revisions_by_ids_resp = {
            "pages": {
                "123": {
                    "pageid": 123,
                    "ns": 0,
                    "title": "Test title",
                    "revisions": [
                        SAMPLE_REVISION_REGISTERED_USER_RAW
                    ]
                }
            }
        }

        try:
            instance = integration.load_single_revision_instance(1)
        except BadRevisionIdException:
            self.fail("Unexpteced BadRevisionIdException")

        self.assertEqual(instance.page,
                         Page(page_id=123,
                              title="Test title",
                              ns=0),
                         "page was not parsed correctly")
        self.assertEqual(len(instance.revisions),
                         1,
                         "unexpected number of revisions")
        self.assertEqual(instance.revisions[0],
                         SAMPLE_REVISION_REGISTERED_USER_OBJ,
                         "revision was not parsed correctly")

    def test_bad_revision(self):
        api = MediaWikiApiMock()
        integration = MediaWikiIntegration(api)
        
        api.query_revisions_by_ids_resp = {
            "badrevids": {
                "12345": {
                    "revid": 12345
                }
            }
        }

        with self.assertRaises(BadRevisionIdException):
            integration.load_single_revision_instance(1)
    
        
if __name__ == '__main__':
    unittest.main()
