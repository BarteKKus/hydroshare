"""This test file contains tests that are common to both model program and model instance aggregations"""

import os

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from rest_framework.exceptions import ValidationError as RF_ValidationError

from hs_core import hydroshare
from hs_core.hydroshare import add_file_to_resource, ResourceFile
from hs_core.views.utils import move_or_rename_file_or_folder
from hs_file_types.models import ModelProgramLogicalFile, ModelInstanceLogicalFile, FileSetLogicalFile
from hs_file_types.models import ModelProgramResourceFileType as MPResFileType


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_file_1(composite_resource, aggr_cls, mock_irods):
    """test that we can create a model program aggregation from a single file that exists at root"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    upload_folder = ''
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(
        res, file_to_upload, folder=upload_folder, check_target_folder=True
    )
    assert res.files.count() == 1
    # create model program aggregation
    assert aggr_cls.objects.count() == 0
    # set file to model program aggregation type
    aggr_cls.set_file_type(res, user, res_file.id)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has no folder
    assert not res_file.file_folder
    assert aggr_cls.objects.count() == 1
    mp_aggregation = aggr_cls.objects.first()
    assert mp_aggregation.files.count() == 1
    assert mp_aggregation.dataset_name == 'generic_file'
    if isinstance(mp_aggregation, ModelProgramLogicalFile):
        assert mp_aggregation.model_program_type == 'Unknown Model Program'
    else:
        assert mp_aggregation.model_instance_type == 'Unknown Model Instance'


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_file_2(composite_resource, aggr_cls, mock_irods):
    """test that we can create a model program aggregation from a single file that exists in a folder"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(
        res, file_to_upload, folder=new_folder, check_target_folder=True
    )
    assert res.files.count() == 1
    # create model program aggregation
    assert aggr_cls.objects.count() == 0
    # set file to model program aggregation type
    aggr_cls.set_file_type(res, user, res_file.id)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == new_folder
    assert aggr_cls.objects.count() == 1
    mp_or_mi_aggregation = aggr_cls.objects.first()
    assert mp_or_mi_aggregation.files.count() == 1
    assert mp_or_mi_aggregation.dataset_name == 'generic_file'


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_file_3(composite_resource, aggr_cls, mock_irods):
    """test that we can create a model program aggregation from a file that exists in a folder that represents
    a fileset aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    fs_folder = 'fs_folder'
    ResourceFile.create_folder(res, fs_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=fs_folder, check_target_folder=True)
    assert res.files.count() == 1
    # create fileset aggregation
    assert FileSetLogicalFile.objects.count() == 0
    # set folder to fileset aggregation type
    FileSetLogicalFile.set_file_type(res, user, folder_path=fs_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == fs_folder
    assert FileSetLogicalFile.objects.count() == 1
    fs_aggregation = FileSetLogicalFile.objects.first()
    assert fs_aggregation.files.count() == 1
    # set the res file to model program aggregation
    aggr_cls.set_file_type(res, user, file_id=res_file.id)
    assert aggr_cls.objects.count() == 1
    mp__or_mi_aggregation = aggr_cls.objects.first()
    assert mp__or_mi_aggregation.files.count() == 1
    # fileset aggregation should not be associated with any resource files
    assert fs_aggregation.files.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_folder(composite_resource, aggr_cls, mock_irods):
    """test that we can create a model program aggregation from a folder that contains a resource file"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=new_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == new_folder
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    assert mp_mi_aggregation.folder == new_folder
    assert mp_mi_aggregation.dataset_name == new_folder
    if isinstance(mp_mi_aggregation, ModelProgramLogicalFile):
        assert mp_mi_aggregation.model_program_type == 'Unknown Model Program'
    else:
        assert mp_mi_aggregation.model_instance_type == 'Unknown Model Instance'


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_folder_inside_fileset(composite_resource, aggr_cls, mock_irods):
    """test that we can create a model program/instance aggregation from a folder that contains a resource file from within a
    folder that represents a fileset aggregation"""

    res, user = composite_resource
    # create fileset aggregation
    file_path = 'pytest/assets/logan.vrt'
    fs_folder = 'fileset_folder'
    ResourceFile.create_folder(res, fs_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=fs_folder, check_target_folder=True)
    # set folder to fileset logical file type (aggregation)
    FileSetLogicalFile.set_file_type(res, user, folder_path=fs_folder)
    assert FileSetLogicalFile.objects.count() == 1
    fs_aggregation = FileSetLogicalFile.objects.first()
    assert fs_aggregation.files.count() == 1

    file_path = 'pytest/assets/generic_file.txt'
    mp_folder = 'mp_folder'
    mp_folder_path = '{0}/{1}'.format(fs_folder, mp_folder)
    ResourceFile.create_folder(res, mp_folder_path)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mp_folder_path, check_target_folder=True)
    assert res.files.count() == 2
    # fileset now should have 2 resource files
    assert fs_aggregation.files.count() == 2
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=mp_folder_path)
    # fileset now should have only one res file
    assert fs_aggregation.files.count() == 1
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    assert mp_mi_aggregation.folder == mp_folder_path
    assert mp_mi_aggregation.dataset_name == mp_folder


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_folder', ['', 'mp_mi_folder'])
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_move_aggregation_to_fileset(composite_resource, aggr_folder, aggr_cls, mock_irods):
    """test that we can move a model program/instance aggregation into a folder that represents a
    fileset aggregation"""

    res, user = composite_resource
    # create fileset aggregation
    file_path = 'pytest/assets/logan.vrt'
    new_folder = 'fileset_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    # set folder to fileset logical file type (aggregation)
    FileSetLogicalFile.set_file_type(res, user, folder_path=new_folder)
    assert FileSetLogicalFile.objects.count() == 1
    fs_aggregation = FileSetLogicalFile.objects.first()
    assert fs_aggregation.files.count() == 1
    # create model program/instance aggregation
    if aggr_folder:
        ResourceFile.create_folder(res, aggr_folder)

    generic_file_name = 'generic_file.txt'
    file_path = 'pytest/assets/{}'.format(generic_file_name)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(res, file_to_upload, folder=aggr_folder, check_target_folder=True)
    if not aggr_folder:
        # create model program/instance aggregation from file
        aggr_cls.set_file_type(res, user, res_file.id)
    else:
        # create model program/instance aggregation from folder
        aggr_cls.set_file_type(res, user, folder_path=aggr_folder)

    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    # move the mp aggregation into the folder that represents fileset aggregation
    if not aggr_folder:
        # moving the file based model program/instance aggregation
        src_path = 'data/contents/{}'.format(generic_file_name)
        tgt_path = 'data/contents/{0}/{1}'.format(new_folder, generic_file_name)
    else:
        # moving the folder based model program/instance aggregation
        src_path = 'data/contents/{}'.format(aggr_folder)
        tgt_path = 'data/contents/{0}/{1}'.format(new_folder, aggr_folder)

    move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)
    assert FileSetLogicalFile.objects.count() == 1
    assert aggr_cls.objects.count() == 1
    assert fs_aggregation.files.count() == 1
    assert mp_mi_aggregation.files.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_upload_file_to_aggregation_folder(composite_resource, aggr_cls, mock_irods):
    """test that when we upload a file to a model program/instance aggregation folder that file becomes part of the
    aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_or_mi_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    assert res.files.count() == 1
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=new_folder)
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    assert mp_mi_aggregation.folder == new_folder
    assert mp_mi_aggregation.dataset_name == new_folder
    # add another file to the model program/instance aggregation folder
    file_path = 'pytest/assets/logan.vrt'
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))
    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    assert res.files.count() == 2
    # both files should be part of the aggregation
    for res_file in res.files.all():
        assert res_file.has_logical_file

    assert mp_mi_aggregation.files.count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_upload_file_to_aggregation_sub_folder(composite_resource, aggr_cls, mock_irods):
    """test that when we upload a file to a model program/instance aggregation sub folder that file becomes part of the
    model program/instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    assert res.files.count() == 1
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=new_folder)
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    assert mp_mi_aggregation.folder == new_folder
    assert mp_mi_aggregation.dataset_name == new_folder
    # add another file to the model program/instance aggregation sub folder
    file_path = 'pytest/assets/logan.vrt'
    new_sub_folder = '{}/mp_mi_sub_folder'.format(new_folder)
    ResourceFile.create_folder(res, new_sub_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))
    add_file_to_resource(res, file_to_upload, folder=new_sub_folder, check_target_folder=True)
    assert res.files.count() == 2
    # both files should be part of the aggregation
    for res_file in res.files.all():
        assert res_file.has_logical_file
    assert mp_mi_aggregation.files.count() == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_folder_failure_1(composite_resource, aggr_cls, mock_irods):
    """test that we can't create a model program/instance aggregation from a folder that does not contain any
    resource file"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder='', check_target_folder=True)
    assert res.files.count() == 1
    # create model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # setting folder to model program/instance aggregation type should fail
    with pytest.raises(ValidationError):
        aggr_cls.set_file_type(resource=res, user=user, folder_path=new_folder)

    res_file = res.files.first()
    # file has no logical file
    assert not res_file.has_logical_file
    # file has no folder
    assert not res_file.file_folder
    # no model program/instance logical file object was created
    assert aggr_cls.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_folder_failure_2(composite_resource, aggr_cls, mock_irods):
    """test that we can't create a model program/instance aggregation from a folder that contains a
    sub-folder representing  a fileset aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    parent_mp_mi_folder = 'mp_mi_folder'
    child_fs_folder = '{}/fs_folder'.format(parent_mp_mi_folder)
    ResourceFile.create_folder(res, parent_mp_mi_folder)
    ResourceFile.create_folder(res, child_fs_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=parent_mp_mi_folder, check_target_folder=True)
    file_path = 'pytest/assets/logan.vrt'
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=child_fs_folder, check_target_folder=True)
    assert res.files.count() == 2
    assert FileSetLogicalFile.objects.count() == 0
    FileSetLogicalFile.set_file_type(res, user, folder_path=child_fs_folder)
    assert FileSetLogicalFile.objects.count() == 1
    fs_aggr = FileSetLogicalFile.objects.first()
    assert fs_aggr.folder == child_fs_folder
    # create model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # setting the folder 'parent_mp_mi_folder' to model program/instance aggregation type should fail
    with pytest.raises(ValidationError):
        aggr_cls.set_file_type(resource=res, user=user, folder_path=parent_mp_mi_folder)

    # no model program/instance logical file object was created
    assert aggr_cls.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_aggregation_from_folder_failure_3(composite_resource, aggr_cls, mock_irods):
    """test that we can't create a model program/instance aggregation from a folder that is a sub folder of a folder
    representing a model program/instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    parent_mp_mi_folder = 'mp_mi_folder'
    child_mp_mi_folder = '{}/child_folder'.format(parent_mp_mi_folder)
    ResourceFile.create_folder(res, parent_mp_mi_folder)
    ResourceFile.create_folder(res, child_mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=parent_mp_mi_folder, check_target_folder=True)
    file_path = 'pytest/assets/logan.vrt'
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=child_mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 2

    # create model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # setting the folder 'parent_mp_mi_folder' to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=parent_mp_mi_folder)

    # one model program/instance logical file object should have been created
    assert aggr_cls.objects.count() == 1
    # setting the folder 'child_mp_mi_folder' to model program/instance aggregation type should fail
    with pytest.raises(ValidationError):
        aggr_cls.set_file_type(resource=res, user=user, folder_path=child_mp_mi_folder)
    assert aggr_cls.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_create_fileset_from_folder_failure(composite_resource, aggr_cls, mock_irods):
    """test that we can't create a fileset aggregation from a folder that is a sub folder of a folder
    representing a model program/instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    parent_mp_mi_folder = 'mp_mi_folder'
    child_mp_mi_folder = '{}/child_folder'.format(parent_mp_mi_folder)
    ResourceFile.create_folder(res, parent_mp_mi_folder)
    ResourceFile.create_folder(res, child_mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=parent_mp_mi_folder, check_target_folder=True)
    file_path = 'pytest/assets/logan.vrt'
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=child_mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 2

    # create model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # setting the folder 'parent_mp_mi_folder' to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=parent_mp_mi_folder)

    # one model program/instance logical file object should have been created
    assert aggr_cls.objects.count() == 1
    # setting the folder 'child_mp_mi_folder' to fileset aggregation type should fail
    with pytest.raises(ValidationError):
        FileSetLogicalFile.set_file_type(resource=res, user=user, folder_path=child_mp_mi_folder)
    assert FileSetLogicalFile.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_delete_aggregation_res_file_1(composite_resource, aggr_cls, mock_irods):
    """ test when we delete a resource file from which we have created a model program/instance aggregation
    the aggregation gets deleted"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    upload_folder = ''
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(
        res, file_to_upload, folder=upload_folder, check_target_folder=True
    )
    assert res.files.count() == 1
    # create model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set file to model program/instance aggregation type
    aggr_cls.set_file_type(res, user, res_file.id)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has no folder
    assert not res_file.file_folder
    assert aggr_cls.objects.count() == 1
    # delete resource file
    hydroshare.delete_resource_file(res.short_id, res_file.id, user)
    assert res.files.count() == 0
    # aggregation object should have been deleted
    assert aggr_cls.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_delete_aggregation_res_file_2(composite_resource, aggr_cls, mock_irods):
    """ test when we delete a resource file that belongs to a folder based model program/instance aggregation
    the aggregation doesn't get deleted"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    new_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, new_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=new_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=new_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == new_folder
    assert aggr_cls.objects.count() == 1
    # delete resource file
    hydroshare.delete_resource_file(res.short_id, res_file.id, user)
    assert res.files.count() == 0
    # aggregation object should still exist
    assert aggr_cls.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('move_type', ['file', 'folder'])
def test_move_model_program_aggr_into_model_instance_aggr_folder(composite_resource, move_type, mock_irods):
    """ test that we can move a file that is part of a file based model program aggregation or a
    folder that represents a model program aggregation into a another folder that represents
    a model instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    mi_folder = 'mi_folder'
    ResourceFile.create_folder(res, mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mi_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model instance aggregation
    assert ModelInstanceLogicalFile.objects.count() == 0
    # set folder to model instance aggregation type
    ModelInstanceLogicalFile.set_file_type(resource=res, user=user, folder_path=mi_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == mi_folder
    assert ModelInstanceLogicalFile.objects.count() == 1
    # create a model program aggregation
    mp_file_name = 'logan.vrt'
    if move_type == 'file':
        # based on a single file
        mp_folder = ''
    else:
        # based on a folder
        mp_folder = 'mp_folder'
        ResourceFile.create_folder(res, mp_folder)

    file_path = 'pytest/assets/{}'.format(mp_file_name)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(res, file_to_upload, folder=mp_folder, check_target_folder=True)

    if move_type == 'file':
        # set file to model program logical file type (aggregation)
        ModelProgramLogicalFile.set_file_type(res, user, res_file.id)
    else:
        # set mp_folder to model program logical file type (aggregation)
        ModelProgramLogicalFile.set_file_type(res, user, folder_path=mp_folder)

    # there should be now 1 instance of model program aggregation
    assert ModelProgramLogicalFile.objects.count() == 1
    assert res_file.file_folder == mp_folder
    # move model program aggregation into model instance aggregation folder
    if move_type == 'file':
        # moving the logan.vrt file into the mi_folder should be successful
        src_path = 'data/contents/{}'.format(mp_file_name)
        tgt_path = 'data/contents/{}/{}'.format(mi_folder, mp_file_name)
    else:
        # moving the mp_folder into the mi_folder should be successful
        src_path = 'data/contents/{}'.format(mp_folder)
        tgt_path = 'data/contents/{}/{}'.format(mi_folder, mp_folder)

    move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
@pytest.mark.parametrize('move_type', ['file', 'folder'])
def test_move_model_aggr_into_model_aggr_folder_failure(composite_resource, aggr_cls, move_type, mock_irods):
    """ test that we can't move a file that is part of a file based model program/instance aggregation or a
    folder that represents a model program/model instance into a another folder that represents
    a model program/instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    mp_mi_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=mp_mi_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == mp_mi_folder
    assert aggr_cls.objects.count() == 1
    # create a model program/instance aggregation
    mp_mi_file_name = 'logan.vrt'
    if move_type == 'file':
        # based on a single file
        folder = ''
    else:
        folder = 'mp_mi_folder_2'
        ResourceFile.create_folder(res, folder)

    file_path = 'pytest/assets/{}'.format(mp_mi_file_name)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    res_file = add_file_to_resource(res, file_to_upload, folder=folder, check_target_folder=True)
    if move_type == 'file':
        # set file to model program/instance logical file type (aggregation)
        aggr_cls.set_file_type(res, user, res_file.id)
    else:
        # set mp_mi_folder_2 to model program/instance logical file type (aggregation)
        aggr_cls.set_file_type(res, user, folder_path=folder)

    # there should be now 2 instances of model program/instance aggregation
    assert aggr_cls.objects.count() == 2
    if move_type == 'file':
        # moving the logan.vrt file into the mp_mi_folder should fail
        src_path = 'data/contents/{}'.format(mp_mi_file_name)
        tgt_path = 'data/contents/{}/{}'.format(mp_mi_folder, mp_mi_file_name)
    else:
        # moving the mp_mi_folder_2 into the mp_mi_folder should fail
        src_path = 'data/contents/{}'.format(folder)
        tgt_path = 'data/contents/{}/{}'.format(mp_mi_folder, folder)

    print(">> src_path:{}".format(src_path))
    print(">> tgt_path:{}".format(tgt_path))
    with pytest.raises(RF_ValidationError):
        move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_move_fileset_into_model_aggr_folder_failure(composite_resource, aggr_cls, mock_irods):
    """ test that we can't move a folder that represents a fileset into a folder that represents a
    model program/instance aggregation"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    fs_folder = 'fs_folder'
    ResourceFile.create_folder(res, fs_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))
    add_file_to_resource(res, file_to_upload, folder=fs_folder, check_target_folder=True)

    FileSetLogicalFile.set_file_type(res, user, folder_path=fs_folder)
    assert FileSetLogicalFile.objects.count() == 1

    # create model program/instance aggregation from a folder
    mp_mi_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, mp_mi_folder)
    mp_mi_file_name = 'logan.vrt'
    file_path = 'pytest/assets/{}'.format(mp_mi_file_name)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 2
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=mp_mi_folder)
    assert aggr_cls.objects.count() == 1
    aggr_obj = aggr_cls.objects.first()
    # model program/instance aggr has folder
    assert aggr_obj.folder == mp_mi_folder
    # move fileset folder into model program/instance folder - which should fail
    src_path = 'data/contents/{}'.format(fs_folder)
    tgt_path = 'data/contents/{}/{}'.format(mp_mi_folder, fs_folder)

    with pytest.raises(RF_ValidationError):
        move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_move_model_aggregation_file_1(composite_resource, aggr_cls, mock_irods):
    """ test that we can move a file that is part of a model program/instance aggregation folder to a normal folder"""

    res, user = composite_resource
    generic_file_name = 'generic_file.txt'
    file_path = 'pytest/assets/{}'.format(generic_file_name)
    mp_mi_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=mp_mi_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == mp_mi_folder
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    if aggr_cls == ModelProgramLogicalFile:
        # set the res file as one of the model program file types
        mp_mi_aggregation.set_res_file_as_mp_file_type(res_file=res_file, mp_file_type='documentation')
        assert MPResFileType.objects.count() == 1

    # moving the generic file to into another folder
    another_folder = 'another_folder'
    ResourceFile.create_folder(res, another_folder)
    src_path = 'data/contents/{}/{}'.format(mp_mi_folder, generic_file_name)
    tgt_path = 'data/contents/{}/{}'.format(another_folder, generic_file_name)
    move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)
    assert aggr_cls.objects.count() == 1
    # model program/instance aggregation should not have any resource files
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 0
    res_file = res.files.first()
    # res file is no more part of any logical file
    assert not res_file.has_logical_file
    if aggr_cls == ModelProgramLogicalFile:
        # model program res file type object should have been deleted
        assert MPResFileType.objects.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_move_model_aggregation_file_2(composite_resource, aggr_cls, mock_irods):
    """ test that we can move a file that is part of a model program/instance aggregation folder to a sub folder of the
    aggregation folder"""

    res, user = composite_resource
    generic_file_name = 'generic_file.txt'
    file_path = 'pytest/assets/{}'.format(generic_file_name)
    parent_mp_mi_folder = 'parent_mp_mi_folder'
    ResourceFile.create_folder(res, parent_mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=parent_mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=parent_mp_mi_folder)
    res_file = res.files.first()
    assert res_file.has_logical_file
    # file has folder
    assert res_file.file_folder == parent_mp_mi_folder
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1

    # set the res file as one of the model program file types
    if aggr_cls == ModelProgramLogicalFile:
        mp_mi_aggregation.set_res_file_as_mp_file_type(res_file=res_file, mp_file_type='documentation')
        assert MPResFileType.objects.count() == 1

    # moving the generic file to into the child folder
    child_mp_mi_folder = '{}/child_mp_mi_folder'.format(parent_mp_mi_folder)
    ResourceFile.create_folder(res, child_mp_mi_folder)
    src_path = 'data/contents/{}/{}'.format(parent_mp_mi_folder, generic_file_name)
    tgt_path = 'data/contents/{}/{}'.format(child_mp_mi_folder, generic_file_name)
    move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)
    assert aggr_cls.objects.count() == 1
    # model program/instance aggregation should have one resource file
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.files.count() == 1
    res_file = res.files.first()
    # res file part of logical file
    assert res_file.has_logical_file
    # model program res file type object should not have been deleted
    if aggr_cls == ModelProgramLogicalFile:
        assert MPResFileType.objects.count() == 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize('aggr_cls', [ModelProgramLogicalFile, ModelInstanceLogicalFile])
def test_rename_model_aggregation_folder(composite_resource, aggr_cls, mock_irods):
    """ test that we can rename a model program/instance aggregation folder"""

    res, user = composite_resource
    file_path = 'pytest/assets/generic_file.txt'
    mp_mi_folder = 'mp_mi_folder'
    ResourceFile.create_folder(res, mp_mi_folder)
    file_to_upload = UploadedFile(file=open(file_path, 'rb'),
                                  name=os.path.basename(file_path))

    add_file_to_resource(res, file_to_upload, folder=mp_mi_folder, check_target_folder=True)
    assert res.files.count() == 1
    # at this point there should not be any model program/instance aggregation
    assert aggr_cls.objects.count() == 0
    # set folder to model program/instance aggregation type
    aggr_cls.set_file_type(resource=res, user=user, folder_path=mp_mi_folder)
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.folder == mp_mi_folder
    # rename the model program/instance aggregation folder
    mp_mi_folder_rename = 'mp_mi_folder_1'
    src_path = 'data/contents/{}'.format(mp_mi_folder)
    tgt_path = 'data/contents/{}'.format(mp_mi_folder_rename)
    move_or_rename_file_or_folder(user, res.short_id, src_path, tgt_path)
    assert aggr_cls.objects.count() == 1
    mp_mi_aggregation = aggr_cls.objects.first()
    assert mp_mi_aggregation.folder == mp_mi_folder_rename
