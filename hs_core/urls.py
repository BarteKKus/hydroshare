from django.conf.urls import patterns, url
from hs_core import views

urlpatterns = patterns('',

    # resource API
     url(r'^resourceTypes/$', views.resource_rest_api.ResourceTypes.as_view(),
        name='list_resource_types'),

    url(r'^resourceList/$', views.resource_rest_api.ResourceList.as_view(),
        name='list_resources'),

    url(r'^resource/$', views.resource_rest_api.ResourceCreate.as_view(),
        name='create_resource'),

    url(r'^resource/(?P<pk>[A-z0-9]+)/$', views.resource_rest_api.ResourceReadUpdateDelete.as_view(),
        name='get_update_delete_resource'),

    url(r'^resource/accessRules/(?P<pk>[A-z0-9]+)/$', views.resource_rest_api.AccessRulesUpdate.as_view(),
        name='update_access_rules'),

    url(r'^sysmeta/(?P<pk>[A-z0-9]+)/$', views.resource_rest_api.SystemMetadataRetrieve.as_view(),
        name='get_system_metadata'),

    url(r'^scimeta/(?P<pk>[A-z0-9]+)/$', views.resource_rest_api.ScienceMetadataRetrieveUpdate.as_view(),
        name='get_update_science_metadata'),

    url(r'^resource/(?P<pk>[A-z0-9]+)/files/$', views.resource_rest_api.ResourceFileCRUD.as_view(),
        name='add_resource_file'),

    url(r'^resource/(?P<pk>[A-z0-9]+)/files/(?P<filename>[^/]+)/$',
        views.resource_rest_api.ResourceFileCRUD.as_view(), name='get_update_delete_resource_file'),

    url(r'^resource/(?P<pk>[A-z0-9]+)/file_list/$', views.resource_rest_api.ResourceFileList.as_view(),
        name='get_resource_file_list'),

    url(r'^userInfo/$',
        views.user_rest_api.UserInfo.as_view(), name='get_logged_in_user_info'),

    # internal API

    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/add-file-to-resource/$', views.add_file_to_resource),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/(?P<element_name>[A-z]+)/add-metadata/$', views.add_metadata_element),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/(?P<element_name>[A-z]+)/(?P<element_id>[A-z0-9]+)/update-metadata/$',
        views.update_metadata_element),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/(?P<element_name>[A-z]+)/(?P<element_id>[A-z0-9]+)/delete-metadata/$',
        views.delete_metadata_element),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/update-key-value-metadata/$',
        views.update_key_value_metadata),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/delete-resource-file/(?P<f>[0-9]+)/$', views.delete_file),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/delete-resource/$', views.delete_resource),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/create-new-version-resource/$', views.create_new_version_resource),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/rep-res-bag-to-irods-user-zone/$', views.rep_res_bag_to_irods_user_zone),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/set-resource-flag/$', views.set_resource_flag),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/share-resource-with-user/(?P<privilege>[a-z]+)/(?P<user_id>[0-9]+)/$',
        views.share_resource_with_user),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/unshare-resource-with-user/(?P<user_id>[0-9]+)/$',
        views.unshare_resource_with_user),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/share-resource-with-group/(?P<privilege>[a-z]+)/(?P<group_id>[0-9]+)/$',
        views.share_resource_with_group, name='share_resource_with_group'),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/unshare-resource-with-group/(?P<group_id>[0-9]+)/$',
        views.unshare_resource_with_group, name='unshare_resource_with_group'),
    url(r'^_internal/create-user-group/$', views.create_user_group, name='create_user_group'),
    url(r'^_internal/update-user-group/(?P<group_id>[0-9]+)$', views.update_user_group, name='update_user_group'),
    url(r'^_internal/share-group-with-user/(?P<group_id>[0-9]+)/(?P<user_id>[0-9]+)/(?P<privilege>[a-z]+)/$',
        views.share_group_with_user, name='share_group_with_user'),
    url(r'^_internal/unshare-group-with-user/(?P<group_id>[0-9]+)/(?P<user_id>[0-9]+)/$',
        views.unshare_group_with_user, name='unshare_group_with_user'),
    url(r'^_internal/make-group-membership-request/(?P<group_id>[0-9]+)/(?P<user_id>[0-9]+)/$',
        views.make_group_membership_request, name='make_group_membership_request'),
    url(r'^_internal/make-group-membership-request/(?P<group_id>[0-9]+)/$',
        views.make_group_membership_request, name='make_group_membership_request'),
    url(r'^_internal/act-on-group-membership-request/(?P<membership_request_id>[0-9]+)/(?P<action>[a-z]+)/$',
        views.act_on_group_membership_request, name='act_on_group_membership_request'),
    url(r'^_internal/group_membership/(?P<token>[-\w]+)/(?P<uidb36>[-\w]+)/(?P<membership_request_id>[0-9]+)/', views.group_membership,
        name='group_membership'),
    url(r'^_internal/get-user-data/(?P<user_id>[0-9]+)$', views.get_user_data, name='get_user_data'),
    url(r'^_internal/(?P<shortkey>[A-z0-9]+)/publish/$', views.publish),
    url(r'^_internal/create-resource/$', views.create_resource_select_resource_type),
    url(r'^_internal/create-resource/do/$', views.create_resource),
    url(r'^_internal/verify-account/$', views.verify_account),
    url(r'^_internal/resend_verification_email/$', views.resend_verification_email),
    url(r'^_internal/(?P<resource_type>[A-z]+)/supported-file-types/$',
        views.get_supported_file_types_for_resource_type),
    url(r'^_internal/(?P<resource_type>[A-z]+)/allow-multiple-file/$',
        views.is_multiple_file_upload_allowed),
    url(r'^_internal/search/autocomplete/', "hs_core.views.autocomplete.autocomplete"),

)
