import click
import logging
import pdb
from dependencies import injector, injector_assisted
from models import Instance, LabelingTask
from persistence import InstanceCollection, LabelingTaskCollection
from services import EditSessionSelector
from mediawiki import (MediaWikiIntegration,
                       MediaWikiApi,
                       BadRevisionIdException,
                       MediaWikiApiResourceInaccessible)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig()

def get_command():
    @click.command()
    def load_labeling_diffs():
        api_integration = injector.get(MediaWikiIntegration)
        collection = injector.get(LabelingTaskCollection)
        
        try:
            loaded_items = 0
            
            for item in collection.query_all():
                if item.cached_diff is not None:
                    continue
                
                logger.debug("querying item {}-{}".format(item.rev_from, item.rev_to))
                diff = api_integration.load_diff_for_labeling_task(item)
                item.cached_diff = diff
                loaded_items += 1
            
        except KeyboardInterrupt:
            logger.error("caught keyboard event")
            pass

        if click.confirm("Do you want to save {} diffs".format(loaded_items)):
            collection.save()
            logger.info("Saved")
    
    return load_labeling_diffs

