import click
import logging
import pdb
from dependencies import injector, injector_assisted
from models import Instance, LabelingTask
from persistence import InstanceCollection, LabelingTaskCollection
from services import EditSessionSelector


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

def get_command():
    @click.command()
    @click.option('--from-collection', 'collection_name', type=str, prompt=True, help="Collection name to take items from")
    def gen_labeling_tasks(collection_name):
        collection = injector_assisted(InstanceCollection).build(name=collection_name)
        labeling_collection = injector.get(LabelingTaskCollection)
        
        try:
            saved_items = 0
            
            for item in collection.query_all():
                rev_before = EditSessionSelector.find_revision_before_session(item.revisions)
                rev_last = item.revisions.get_last_revision()

                task = LabelingTask(
                    rev_from=rev_before.rev_id,
                    rev_to=rev_last.rev_id,
                    tags=[],
                    labeled_at=None,
                    cached_diff=None,
                    cached_title=item.page.title,
                    cached_username=str(rev_last.user)
                    )
                labeling_collection.insert(task)

                saved_items += 1
            
        except KeyboardInterrupt:
            logger.error("caught keyboard event")
            pass

        if click.confirm("Do you want to save {} new instances".format(saved_items)):
            labeling_collection.save()
            logger.info("Saved")
    
    return gen_labeling_tasks

