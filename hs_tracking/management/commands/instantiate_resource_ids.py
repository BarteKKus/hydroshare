"""
Instantiate resource ID's for tracking records.
"""
from django.core.management.base import BaseCommand
import re
from datetime import datetime, timedelta
from hs_tracking.models import Variable
from hs_core.hydroshare import get_resource_by_shortkey
from hs_core.models import BaseResource


RE_COMPILER = {"visit": re.compile('resource/([0-9a-f]{32})/'),
               "download": re.compile('id=([0-9a-f]{32})\|'),
               "app_launch": re.compile('id=([0-9a-f]{32})\|')}


def instantiate_timestamp_range(start, end):
    """ instantiate a range of Variable requests """
    events = 0
    ids = 0
    print("instantiating ids from -{} days to -{} days from now".format(start, end))
    for v in Variable.objects.filter(timestamp__gte=datetime.now()-timedelta(start),
                                     timestamp__lte=datetime.now()-timedelta(end)):
        events = events + 1
        value = v.get_value()
        if v.name in RE_COMPILER:
            m = RE_COMPILER[v.name].search(value)
            if (m and m.group(1)):
                resource_id = m.group(1)
                if(resource_id is not None):
                    v.last_resource_id = resource_id
                    try:
                        resource = get_resource_by_shortkey(resource_id, or_404=False)
                        v.resource = resource
                    except BaseResource.DoesNotExist:
                        pass
                    v.save()
                    # print("{} for '{}' ".format(resource_id, value))
                    ids = ids + 1
                    if ids % 1000 == 0:
                        print("{} of {}".format(ids, events))
    print("resource ids found for {} of {} events".format(ids, events))


def instantiate_resource_ids():
    """ instantiate the resource id field for older usage events """
    # This must be processed in batches because the events
    # exceed memory limits if batched all at once.
    instantiate_timestamp_range(365, 0)
    instantiate_timestamp_range(365*2, 365)
    instantiate_timestamp_range(365*3, 365*2)


class Command(BaseCommand):
    help = "Instantiate all resource id's for tracking."

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        instantiate_resource_ids()
