import logging
import os

from django.db import models

from hs_file_types.models import AbstractLogicalFile
from hs_file_types.models.base import FileTypeContext


class AbstractModelLogicalFile(AbstractLogicalFile):
    # folder path relative to {resource_id}/data/contents/ that represents this aggregation
    # folder becomes the name of the aggregation. Where folder is not set, the one file that is part
    # of this aggregation becomes the aggregation name
    folder = models.CharField(max_length=4096, null=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def get_main_file_type(cls):
        """The main file type for this aggregation - no specific main file"""
        return ".*"

    @classmethod
    def check_files_for_aggregation_type(cls, files):
        """Checks if the specified files can be used to set this aggregation type
        :param  files: a list of ResourceFile objects

        :return If the files meet the requirements of this aggregation type, then returns this
        aggregation class name, otherwise empty string.
        """
        if len(files) == 0:
            # no files
            return ""

        return cls.__name__

    @classmethod
    def get_primary_resouce_file(cls, resource_files):
        """Gets any one resource file from the list of files *resource_files* """

        return resource_files[0] if resource_files else None

    @classmethod
    def set_file_type(cls, resource, user, file_id=None, folder_path=None):
        """Makes all physical files that are in a folder (*folder_path*) part of a model program/instance
        aggregation type or a single file (*file_id*) part of this aggregation type.
        Note: parameter file_id is ignored here and a value for folder_path is required
        """

        log = logging.getLogger()
        with FileTypeContext(aggr_cls=cls, user=user, resource=resource, file_id=file_id,
                             folder_path=folder_path,
                             post_aggr_signal=None,
                             is_temp_file=False) as ft_ctx:

            if folder_path is not None:
                res_files = []
                dataset_name = folder_path
                if '/' in folder_path:
                    dataset_name = os.path.basename(folder_path)
            else:
                res_file = ft_ctx.res_file
                res_files = [res_file]
                folder_path = res_file.file_folder
                dataset_name, _ = os.path.splitext(res_file.file_name)

            # remove any previously associated logical files from the files
            # before making them part of this new logical file
            for res_file in res_files:
                if res_file.has_logical_file:
                    res_file.logical_file_content_object = None
                    res_file.save()

            # create a model program/instance logical file object
            logical_file = cls.create_aggregation(dataset_name=dataset_name,
                                                  resource=resource,
                                                  res_files=res_files,
                                                  new_files_to_upload=[],
                                                  folder_path=folder_path)

            if folder_path is not None and file_id is None:
                logical_file.folder = folder_path
                logical_file.save()
                # make all the files in the selected folder as part of the aggregation
                logical_file.add_resource_files_in_folder(resource, folder_path)
                log.info("{0} aggregation was created for folder:{1}.".format(logical_file.data_type, folder_path))
            else:
                log.info("{0} aggregation was created for file:{1}.".format(logical_file.data_type,
                                                                            res_file.storage_path))
            ft_ctx.logical_file = logical_file