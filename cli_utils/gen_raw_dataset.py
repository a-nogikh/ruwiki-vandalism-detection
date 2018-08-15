import click
import itertools
import logging
import random
import time
import pdb
from dependencies import injector, injector_assisted
from persistence import InstanceCollection
from models import Instance, RegisteredUser
from mediawiki import (MediaWikiIntegration,
                       MediaWikiApi,
                       BadRevisionIdException,
                       MediaWikiApiResourceInaccessible)
from services import UserGroupsFetcher


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

# Unique random number generator
def random_id_generator(exclude_ids: set,
                        rev_start: int,
                        rev_end: int):
    pushed = set()
    
    while True:
        x = random.randint(rev_start, rev_end)
        if x in exclude_ids:
            continue

        if x in pushed:
            continue

        pushed.add(x)
        yield x


def instance_generator(id_generator, api_integration: MediaWikiIntegration):
    rev_id = next(id_generator)
    while True:
        try:
            instance = api_integration.load_single_revision_instance(rev_id)
            if instance:
                logger.info("revision {} successfully retrieved".format(rev_id))                
                yield instance
                
        except MediaWikiApiResourceInaccessible:
            # sleep and retry
            logger.info("revision {}: couldn't retrieve, sleeping for 5 seconds".format(rev_id))
            time.sleep(5)
            continue
        
        except BadRevisionIdException:
            logger.info("revision {} does not exist".format(rev_id))

        # selecting next revision id
        rev_id = next(id_generator)


def get_command():
    @click.command()
    @click.option('--collection', 'collection_name', type=str, prompt=True, help="Collection name")
    @click.option('--rev_start', type=int, prompt=True, help="# of earliest revision of the range")
    @click.option('--rev_end', type=int, prompt=True, help="# of newest revision of the range")
    @click.option('--count', type=int, prompt=True, help="count of revisions to add")
    @click.option('--history-count', type=int, help='number of history revisions to load', default=15)
    @click.option('--include-bots/--exclude-bots', default=False)
    @click.option('--include-guests/--exclude-guests', default=True)
    def gen_raw_dataset(collection_name,
                        rev_start,
                        rev_end,
                        count,
                        history_count,
                        include_bots,
                        include_guests):
        api_integration = injector.get(MediaWikiIntegration)
        collection = injector_assisted(InstanceCollection).build(name=collection_name)
        groups_fetcher = injector.get(UserGroupsFetcher) # type: UserGroupsFetcher

        used_revisions = set()
        for x in collection.query_all():
            used_revisions.add(x.revision_id)

        id_generator = random_id_generator(used_revisions, rev_start, rev_end)
        instance_stream = instance_generator(id_generator, api_integration)

        def validate_instance_pre(instance: Instance) -> bool:
            nonlocal groups_fetcher

            if instance.page.ns != 0:
                logger.info("skipping namespace {}".format(instance.page.ns))
                return False
            
            revision = instance.revisions[0]
            author = revision.user
            if isinstance(author, RegisteredUser):
                groups = groups_fetcher.fetch_groups(author.user_id)

                if len(groups) > 0 or 'bot' in str(author).lower():
                    logger.info("skipping due to name ({}) or groups user groups: {}".format(author, groups))
                    return False
            else:
                pass # non-registered user
                
            return True

        def validate_instance_post(instance: Instance) -> bool:
            if len(instance.revisions) <= 1:
                logger.info("skipping initial revisions")
                return False

            return True
        
        try:
            saved_items = 0
            
            filtered_stream = filter(validate_instance_pre, instance_stream)
            for x in itertools.islice(filtered_stream, count):
                api_integration.load_revisions_into_instance(x, history_count)
                if not validate_instance_post(x):
                    continue
                
                saved_items += 1
                collection.insert(x)
            
        except KeyboardInterrupt:
            logger.error("caught keyboard event")
            pass

        if click.confirm("Do you want to save {} new instances".format(saved_items)):
            collection.save()
            logger.info("Saved")
    
    return gen_raw_dataset
