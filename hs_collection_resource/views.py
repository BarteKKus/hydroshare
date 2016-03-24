import logging

from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse, JsonResponse
from django.db import transaction

from hs_core.views.utils import authorize, ACTION_TO_AUTHORIZE
from hs_core.hydroshare.utils import user_from_id, get_resource_by_shortkey, resource_modified

logger = logging.getLogger(__name__)

# update collection
def update_collection(request, shortkey, *args, **kwargs):

    status = "success"
    msg = ""
    metadata_status = "Insufficient to make public"
    try:
        with transaction.atomic():
            collection_res_obj, is_authorized, user = authorize(request, shortkey,
                                                                needed_permission=ACTION_TO_AUTHORIZE.EDIT_RESOURCE)

            if collection_res_obj.resource_type != "CollectionResource":
                raise Exception("Resource {0} is not a collection resource.".format(shortkey))

            # get res_id list from POST
            updated_contained_res_id_list = request.POST.getlist("resource_id_list")
            # for res_id in request.POST.getlist("resource_id_list"):
            #     updated_contained_res_id_list.append(res_id)

            if len(updated_contained_res_id_list) > len(set(updated_contained_res_id_list)):
                raise Exception("Duplicate resources were found for adding to the collection")

            # check authorization for all new resources being added to the collection
            for updated_contained_res_id in updated_contained_res_id_list:
                if not collection_res_obj.resources.filter(short_id=updated_contained_res_id).exists():
                    res_to_add, _, _ = authorize(request, updated_contained_res_id,
                                                 needed_permission=ACTION_TO_AUTHORIZE.VIEW_METADATA)

                    # for now we are not allowing a collection resource to be added to another collection resource
                    if res_to_add.resource_type == "CollectionResource":
                        raise Exception("Resource {0} is a collection resource which can't be added.".format(shortkey))

            # remove all resources from the collection
            collection_res_obj.resources.clear()

            # add resources to the collection
            for updated_contained_res_id in updated_contained_res_id_list:
                updated_contained_res_obj = get_resource_by_shortkey(updated_contained_res_id)
                collection_res_obj.resources.add(updated_contained_res_obj)

            if collection_res_obj.can_be_public_or_discoverable:
                metadata_status = "Sufficient to make public"

            resource_modified(collection_res_obj, user)

    except Exception as ex:
        logger.error("update_collection: {0} ; username: {1}; collection_id: {2} ".
                         format(ex.message,
                                request.user.username if request.user.is_authenticated() else "anonymous",
                                shortkey))
        status = "error"
        msg = ex.message
    finally:
        ajax_response_data = {'status': status, 'msg': msg, 'metadata_status': metadata_status}
        return JsonResponse(ajax_response_data)


def update_collection_for_deleted_resources(request, shortkey, *args, **kwargs):
    ajax_response_data = {'status': "success"}
    try:
        collection_res, is_authorized, user = authorize(request, shortkey,
                                                        needed_permission=ACTION_TO_AUTHORIZE.EDIT_RESOURCE)

        if collection_res.resource_type != "CollectionResource":
            raise Exception("Resource {0} is not a collection resource.".format(shortkey))

        resource_modified(collection_res, user)
        # remove all logged deleted resources for the collection
        collection_res.deleted_resources.all().delete()

    except Exception as ex:
        logger.error("Failed to update collection for deleted resources.Collection resource ID: {}. "
                     "Error:{} ".format(shortkey, ex.message))

        ajax_response_data = {'status': "error", 'message': ex.message}
    finally:
        return JsonResponse(ajax_response_data)

# loop through contained resources in collection ("shortkey") to check if the target user ("user_id") has
# at least View permission over them.
def collection_member_permission(request, shortkey, user_id, *args, **kwargs):
    try:
        collection_res_obj, is_authorized, user = authorize(request, shortkey,
                                              needed_permission=ACTION_TO_AUTHORIZE.VIEW_METADATA,
                                              raises_exception=True)
        no_permission_list = []

        user_to_share_with = user_from_id(user_id)
        if collection_res_obj.resources:
            for res_in_collection in collection_res_obj.resources.all():
                if not user_to_share_with.uaccess.can_view_resource(res_in_collection) \
                    and not res_in_collection.raccess.discoverable:
                    no_permission_list.append(res_in_collection.short_id)
            status = "success"
            ajax_response_data = {'status': status, 'no_permission_list': no_permission_list}
        else:
            raise Exception("Collection element is not yet initialized.")
    except Exception as ex:
        logger.warning("collection_member_permission: %s" % (ex.message))
        ajax_response_data = {'status': "error", 'message': ex.message}
    finally:
        return JsonResponse(ajax_response_data)
