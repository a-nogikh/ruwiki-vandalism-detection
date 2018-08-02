import click
import random
from mediawiki import MediaWikiIntegration, MediaWikiApi
from persistence.instance_collection import InstanceCollection

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

        
def get_command():
    @click.command()
    @click.argument('collection', 'collection_name', type=str, help="Collection name")
    @click.argument('rev_start', type=int, help="# of earliest revision of the range")
    @click.argument('rev_end', type=int, help="# of newest revision of the range")
    @click.argument('count', type=int, help="count of revisions to add")
    @click.option('--include-bots/--exclude-bots', default=False)
    @click.option('--include-guests/--exclude-guests', default=True)
    def gen_raw_dataset(collection_name, rev_start, rev_end, count):
        # TODO: ask for YES/NO!!!

        api = MediaWikiApi()
        api_integration = MediaWikiIntegration(api)
        collection = InstanceCollection(collection_name)

        used_revisions = set()
        for x in collection.query_all():
            used_revisions.insert(x.revision_id)

        id_generator = random_id_generator(used_revisions, rev_start, rev_end)
            
        found_revisions = 0
        while found_revisions <= count:
            rev_id = next(id_generator)
            instance = api_integration.load_single_revision_instance(rev_id)

            # process
            
            
        # TODO: ask on Ctrl+Z whether  to save
        pass
    
    return gen_raw_dataset
