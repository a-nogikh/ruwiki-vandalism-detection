from ...types import serializable, Timestamp
from .contributor import Contributor
#import pyximport; pyximport.install()
from .util import consume_tags
import datetime
import mw.xml_dump.element_iterator


class Revision(serializable.Type):
    """
    Revision meta data.
    """
    __slots__ = ('id', 'timestamp', 'contributor', 'minor', 'comment')

    TAG_MAP = {
        'id': lambda e: int(e.text),
        'timestamp': lambda e: e.text,#Timestamp(e.text),
        'contributor': lambda e: Contributor.from_element(e),
        'minor': lambda e: True,
        'comment': lambda e: e.text,#Comment.from_element(e)
    }

    def __init__(self, id, timestamp, contributor=None, minor=None,
                 comment=None):
        self.id = id #none_or(id, int)
        """
        Revision ID : `int`
        """

        if timestamp is not None:
            self.timestamp = datetime.datetime(
                int(timestamp[0:4]),
                int(timestamp[5:7]),
                int(timestamp[8:10]),
                int(timestamp[11:13]),
                int(timestamp[14:16]),
                int(timestamp[17:19]),
                0,
                datetime.timezone.utc
            ) # type: datetime.datetime
        else:
            self.timestamp = None # type: datetime.datetime

        self.contributor = None or contributor #none_or(contributor, Contributor.deserialize)
        """
        Contributor meta data : :class:`~mw.xml_dump.Contributor` | `None`
        """

        self.minor = minor #none_or(minor, bool)
        """
        Is revision a minor change? : `bool`
        """

        self.comment = comment #none_or(comment, Comment)
        """
        Comment left with revision : :class:`~mw.xml_dump.Comment` (behaves like `str`, with additional members)
        """

        self.reverted_by = None
        self.reverts_till = None
        self.cancelled_by = None
        self.cancels = None
        self.next = None
        self.prev = None

    @classmethod
    def from_element(cls, element):
        values = consume_tags(cls.TAG_MAP, element)

        return cls(
            values.get('id'),
            values.get('timestamp'),
            values.get('contributor'),
            values.get('minor') is not None,
            values.get('comment'),
        #    values.get('parentid')
        )
