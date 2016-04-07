from django.contrib.auth.models import User
from django.db import models, transaction

from mezzanine.pages.page_processors import processor_for

from hs_core.models import BaseResource, ResourceManager, resource_processor

class CollectionResource(BaseResource):
    objects = ResourceManager('CollectionResource')

    class Meta:
        proxy = True
        verbose_name = 'Collection Resource'

    @classmethod
    def get_supported_upload_file_types(cls):
        # no file types are supported
        return ()

    @classmethod
    def can_have_multiple_files(cls):
        # resource can't have any files
        return False

    @property
    def can_be_public_or_discoverable(self):
        return self.metadata.has_all_required_elements() and (self.resources.count() > 0)

    @property
    def deleted_resources(self):
        return CollectionDeletedResource.objects.filter(collection=self)

    @property
    def has_resources(self):
        return self.resources.count() > 0

    @property
    def are_all_contained_resources_published(self):
        for res in self.resources.all():
            if not res.raccess.published:
                return False
        return True


processor_for(CollectionResource)(resource_processor)


class CollectionDeletedResource(models.Model):
    resource_title = models.TextField(null=False, blank=False)
    deleted_by = models.ForeignKey(User)
    date_deleted = models.DateTimeField(auto_now_add=True)
    collection = models.ForeignKey(BaseResource)
    resource_id = models.CharField(max_length=32)
    resource_type = models.CharField(max_length=50)


import receivers