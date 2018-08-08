import click
import itertools
import logging
import random
import time
from dependencies import injector, injector_assisted
from persistence.instance_collection import InstanceCollection
from models import Instance
from mediawiki import (MediaWikiIntegration,
                       MediaWikiApi,
                       BadRevisionIdException,
                       MediaWikiApiResourceInaccessible)


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
    @click.option('--include-bots/--exclude-bots', default=False)
    @click.option('--include-guests/--exclude-guests', default=True)
    def gen_raw_dataset(collection_name, rev_start, rev_end, count, include_bots, include_guests):
        api_integration = injector.get(MediaWikiIntegration)
        collection = injector_assisted(InstanceCollection).build(name=collection_name)

        used_revisions = set()
        for x in collection.query_all():
            used_revisions.add(x.revision_id)

        id_generator = random_id_generator(used_revisions, rev_start, rev_end)
        instance_stream = instance_generator(id_generator, api_integration)

        def validate_instance(instance: Instance) -> bool:
            # TODO implement
            return True
        
        try:
            saved_items = 0
            
            filtered_stream = filter(validate_instance, instance_stream)
            for x in itertools.islice(filtered_stream, count):
                # load more revisions into the instance!
                saved_items += 1
                collection.insert(x)
            
        except KeyboardInterrupt:
            logger.error("caught keyboard event")
            pass

        if click.confirm("Do you want to save {} new instances".format(saved_items)):
            logger.info("Saved")
    
    return gen_raw_dataset
