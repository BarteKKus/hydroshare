from django.contrib.auth.models import User, Group
from hs_access_control.models import PrivilegeCodes, GroupAccess, GroupResourcePrivilege
from hs_core.models import BaseResource
from hs_core.search_indexes import BaseResourceIndex
from hs_tracking.models import Variable
import re


class Features(object):
    """
    Features appropriate for machine learning analysis of our databases.
    """

    @staticmethod
    def resource_owners():
        """ return (username, resource_id) tuples representing resource owners """
        records = []
        for u in User.objects.all():
            owned = BaseResource.objects.filter(r2urp__user=u,
                                                r2urp__privilege=PrivilegeCodes.OWNER)
            for r in owned:
                records.append((u.username, r.short_id,))
        return records

    @staticmethod
    def group_owners():
        """ return (username, group_name) tuples representing group ownership """
        records = []
        for u in User.objects.all():
            owned = Group.objects.filter(g2ugp__user=u,
                                         g2ugp__privilege=PrivilegeCodes.OWNER)
            for g in owned:
                records.append((u.username, g.name,))
        return records

    @staticmethod
    def resource_editors():
        """ return (username, resource_id) tuples representing resource editing privilege """
        records = []
        for u in User.objects.all():
            editable = BaseResource.objects.filter(r2urp__user=u,
                                                   r2urp__privilege__lte=PrivilegeCodes.CHANGE)
            for r in editable:
                records.append((u.username, r.short_id,))
        return records

    @staticmethod
    def group_editors():
        """ return (username, group_name) tuples representing group editing privilege """
        records = []
        for u in User.objects.all():
            editable = Group.objects.filter(g2ugp__user=u,
                                            g2ugp__privilege__lte=PrivilegeCodes.CHANGE)
            for g in editable:
                records.append((u.username, g.name,))
        return records

    @staticmethod
    def resource_viewers(fromdate, todate):
        """ map of users who viewed each resource, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('/resource/([^/]+)/')  # home page of resource
        resource_visited_by_user = {}
        for v in Variable.objects.filter(name='visit',
                                         timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                value = v.get_value()
                m = expr.search(value)  # home page of resource
                if m and m.group(1):
                    resource_id = m.group(1)
                    user_id = user.username
                    if resource_id not in resource_visited_by_user:
                        resource_visited_by_user[resource_id] = set([user_id])
                    else:
                        resource_visited_by_user[resource_id].add(user_id)
        return resource_visited_by_user

    @staticmethod
    def visited_resources(fromdate, todate):
        """ map of users who viewed each resource, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('/resource/([^/]+)/')  # home page of resource
        user_visiting_resource = {}
        for v in Variable.objects.filter(name='visit',
                                         timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                value = v.get_value()
                m = expr.search(value)  # home page of resource
                if m and m.group(1):
                    resource_id = m.group(1)
                    user_id = user.username
                    if user_id not in user_visiting_resource:
                        user_visiting_resource[user_id] = set([resource_id])
                    else:
                        user_visiting_resource[user_id].add(resource_id)
        return user_visiting_resource

    @staticmethod
    def resource_downloads(fromdate, todate):
        """ map of each resource to users who downloaded it, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('\|resource_guid=([^|]+)\|')  # resource short id
        downloads = {}
        for v in Variable.objects.filter(timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                user_id = user.username
                if v.name == 'download':
                    value = v.get_value()
                    m = expr.search(value)  # resource short id
                    if m and m.group(1):
                        resource_id = m.group(1)
                        user_id = user.username
                        if resource_id not in downloads:
                            downloads[resource_id] = set([user_id])
                        else:
                            downloads[resource_id].add(user_id)
        return downloads

    @staticmethod
    def user_downloads(fromdate, todate):
        """ map of users who viewed each resource, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('\|resource_guid=([^|]+)\|')  # resource short id
        downloads = {}
        for v in Variable.objects.filter(timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                user_id = user.username
                if v.name == 'download':
                    value = v.get_value()
                    m = expr.search(value)  # resource short id
                    if m and m.group(1):
                        resource_id = m.group(1)
                        user_id = user.username
                        if resource_id not in downloads:
                            downloads[user_id] = set([resource_id])
                        else:
                            downloads[user_id].add(resource_id)
        return downloads

    @staticmethod
    def resource_apps(fromdate, todate):
        """ map of each resources to users who launched and app on it, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('\|resourceid=([^|]+)\|')  # resource short id
        apps = {}
        for v in Variable.objects.filter(timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                user_id = user.username
                if v.name == 'app_launch':
                    value = v.get_value()
                    m = expr.search(value)  # resource short id
                    if m and m.group(1):
                        resource_id = m.group(1)
                        user_id = user.username
                        if resource_id not in apps:
                            apps[resource_id] = set([user_id])
                        else:
                            apps[resource_id].add(user_id)
        return apps

    @staticmethod
    def user_apps(fromdate, todate):
        """ map of users who lanuched an app on each resource, according to date of access
            :param fromdata(date type), the start date of the time range
            :param todate(date type), the end date of the time range
        """
        expr = re.compile('\|resourceid=([^|]+)\|')  # resource short id
        apps = {}
        for v in Variable.objects.filter(timestamp__gte=fromdate, timestamp__lte=todate):
            user = v.session.visitor.user
            if user is not None and \
               user.username != 'test' and user.username != 'demo':
                user_id = user.username
                if v.name == 'app_launch':
                    value = v.get_value()
                    m = expr.search(value)  # resource short id
                    if m and m.group(1):
                        resource_id = m.group(1)
                        user_id = user.username
                        if resource_id not in apps:
                            apps[user_id] = set([resource_id])
                        else:
                            apps[user_id].add(resource_id)
        return apps

    @staticmethod
    def user_favorites():
        """ map each user to her favorite resources"""
        favs = {}
        for u in User.objects.filter(is_active=True):
            for r in u.ulabels.favorited_resources:
                if u.username not in favs:
                    favs[u.username] = set([r.short_id])
                else:
                    favs[u.username].add(r.short_id)
        return favs

    @staticmethod
    def user_my_resources():
        """ map each user to her resoruces """
        mine = {}
        for u in User.objects.filter(is_active=True):
            for r in u.ulabels.my_resources:
                if u.username not in mine:
                    mine[u.username] = set([r.short_id])
                else:
                    mine[u.username].add(r.short_id)
        return mine

    @staticmethod
    def user_owned_groups():
        """ map each user to groups that owned by the user  """
        groups = {}
        for u in User.objects.filter(is_active=True):
            for g in u.uaccess.get_groups_with_explicit_access(PrivilegeCodes.OWNER):
                if u.username not in groups:
                    groups[u.username] = set([g.name])
                else:
                    groups[u.username].add(g.name)
        return groups

    @staticmethod
    def user_edited_groups():
        """ map each user to groups that editable by the user  """
        groups = {}
        for u in User.objects.filter(is_active=True):
            for g in u.uaccess.get_groups_with_explicit_access(PrivilegeCodes.CHANGE):
                if u.username not in groups:
                    groups[u.username] = set([g.name])
                else:
                    groups[u.username].add(g.name)
        return groups

    @staticmethod
    def user_viewed_groups():
        """ map each user to groups that viewable by the user  """
        groups = {}
        for u in User.objects.filter(is_active=True):
            for g in u.uaccess.get_groups_with_explicit_access(PrivilegeCodes.VIEW):
                if u.username not in groups:
                    groups[u.username] = set([g.name])
                else:
                    groups[u.username].add(g.name)
        return groups

    @staticmethod
    def resources_editable_via_group(g):
        """ return the set of resource ids that editable by the given group
            :param g, a Group object
        """
        output = set([])
        if GroupAccess.objects.filter(group=g).exists():
            for r in g.gaccess.get_resources_with_explicit_access(PrivilegeCodes.CHANGE):
                output.add(r.short_id)
        return output

    @staticmethod
    def resources_viewable_via_group(g):
        """ return the set of resource ids that viewable by the given group
            :param g, aGroup object
        """
        output = set([])
        if GroupAccess.objects.filter(group=g).exists():
            for r in g.gaccess.get_resources_with_explicit_access(PrivilegeCodes.VIEW):
                output.add(r.short_id)
        return output

    @staticmethod
    def explain_group(gname):
        """ return detail description of a given group
            :param gname, a group's name
        """
        g = Group.objects.get(name=gname)
        if GroupAccess.objects.filter(group=g).exists():
            return {'name': g.name,
                    'description': g.gaccess.description,
                    'purpose': g.gaccess.purpose}
        else:
            return {'name': g.name}

    @staticmethod
    def resource_features(obj):
        """ map the given resource to its features
            :param obj, a Resource object
        """
        ind = BaseResourceIndex()
        output = {}
        output['sample_medium'] = ind.prepare_sample_medium(obj)
        output['creator'] = ind.prepare_creator(obj)
        output['title'] = ind.prepare_title(obj)
        output['abstract'] = ind.prepare_abstract(obj)
        output['author_raw'] = ind.prepare_author_raw(obj)
        output['author'] = ind.prepare_author(obj)
        output['author_url'] = ind.prepare_author_url(obj)
        output['creator'] = ind.prepare_creator(obj)
        output['contributor'] = ind.prepare_contributor(obj)
        output['subject'] = ind.prepare_subject(obj)
        output['organization'] = ind.prepare_organization(obj)
        output['publisher'] = ind.prepare_publisher(obj)
        output['creator_email'] = ind.prepare_creator_email(obj)
        output['availability'] = ind.prepare_availability(obj)
        output['replaced'] = ind.prepare_replaced(obj)
        output['coverage'] = ind.prepare_coverage(obj)
        output['coverage_type'] = ind.prepare_coverage_type(obj)
        output['east'] = ind.prepare_east(obj)
        output['north'] = ind.prepare_north(obj)
        output['northlimit'] = ind.prepare_northlimit(obj)
        output['eastlimit'] = ind.prepare_eastlimit(obj)
        output['southlimit'] = ind.prepare_southlimit(obj)
        output['westlimit'] = ind.prepare_westlimit(obj)
        output['start_date'] = ind.prepare_start_date(obj)
        output['end_date'] = ind.prepare_end_date(obj)
        output['format'] = ind.prepare_format(obj)
        output['identifier'] = ind.prepare_identifier(obj)
        output['language'] = ind.prepare_language(obj)
        output['source'] = ind.prepare_source(obj)
        output['relation'] = ind.prepare_relation(obj)
        output['resource_type'] = ind.prepare_resource_type(obj)
        output['comment'] = ind.prepare_comment(obj)
        output['comments_count'] = ind.prepare_comments_count(obj)
        output['owner_login'] = ind.prepare_owner_login(obj)
        output['owner'] = ind.prepare_owner(obj)
        output['owners_count'] = ind.prepare_owners_count(obj)
        output['geometry_type'] = ind.prepare_geometry_type(obj)
        output['field_name'] = ind.prepare_field_name(obj)
        output['field_type'] = ind.prepare_field_type(obj)
        output['field_type_code'] = ind.prepare_field_type_code(obj)
        output['variable'] = ind.prepare_variable(obj)
        output['variable_type'] = ind.prepare_variable_type(obj)
        output['variable_shape'] = ind.prepare_variable_shape(obj)
        output['variable_descriptive_name'] = ind.prepare_variable_descriptive_name(obj)
        output['variable_speciation'] = ind.prepare_variable_speciation(obj)
        output['site'] = ind.prepare_site(obj)
        output['method'] = ind.prepare_method(obj)
        output['quality_level'] = ind.prepare_quality_level(obj)
        output['data_source'] = ind.prepare_data_source(obj)
        output['sample_medium'] = ind.prepare_sample_medium(obj)
        output['units'] = ind.prepare_units(obj)
        output['units_type'] = ind.prepare_units_type(obj)
        output['aggregation_statistics'] = ind.prepare_aggregation_statistics(obj)
        output['absolute_url'] = ind.prepare_absolute_url(obj)
        output['extra'] = ind.prepare_extra(obj)
        return output

    @staticmethod
    def render_abstract_phrase(field, value):
        """ helper function for resource_extended_abstract
            :param field, a specified field in a resource
            :param value, the value for the corresponding field
            return a formatted string to describe the value of the given field
        """
        output = ""
        if value is None:
            value = []
        if not isinstance(value, (tuple, list)):
            value = [value]
        for v in value:
            if v is not None and v != "" and isinstance(v, str) \
                    and field is not None and field != "":
                output = output + "{} is {}. ".format(field.encode('ascii', 'ignore'),
                                                      v.encode('ascii', 'ignore'))
        return output

    @staticmethod
    def resource_extended_abstract(obj):
        """ return (url, a formatted string) to show values for each corresponding field
            :param obj, a given Resource
        """
        ind = BaseResourceIndex()
        output = ind.prepare_abstract(obj)
        if output is None:
            output = ""
        output = output + Features.render_abstract_phrase('sample_medium',
                                                          ind.prepare_sample_medium(obj))
        output = output + Features.render_abstract_phrase('title',
                                                          ind.prepare_title(obj))
        output = output + Features.render_abstract_phrase('creator',
                                                          ind.prepare_creator(obj))
        output = output + Features.render_abstract_phrase('author',
                                                          ind.prepare_author(obj))
        output = output + Features.render_abstract_phrase('creator',
                                                          ind.prepare_creator(obj))
        output = output + Features.render_abstract_phrase('contributor',
                                                          ind.prepare_contributor(obj))
        output = output + Features.render_abstract_phrase('subject',
                                                          ind.prepare_subject(obj))
        output = output + Features.render_abstract_phrase('organization',
                                                          ind.prepare_organization(obj))
        output = output + Features.render_abstract_phrase('publisher',
                                                          ind.prepare_publisher(obj))
        output = output + Features.render_abstract_phrase('availability',
                                                          ind.prepare_availability(obj))
        output = output + Features.render_abstract_phrase('replaced',
                                                          ind.prepare_replaced(obj))
        output = output + Features.render_abstract_phrase('coverage_type',
                                                          ind.prepare_coverage_type(obj))
        output = output + Features.render_abstract_phrase('format',
                                                          ind.prepare_format(obj))
        output = output + Features.render_abstract_phrase('identifier',
                                                          ind.prepare_identifier(obj))
        output = output + Features.render_abstract_phrase('language',
                                                          ind.prepare_language(obj))
        output = output + Features.render_abstract_phrase('source',
                                                          ind.prepare_source(obj))
        output = output + Features.render_abstract_phrase('relation',
                                                          ind.prepare_relation(obj))
        output = output + Features.render_abstract_phrase('resource_type',
                                                          ind.prepare_resource_type(obj))
        output = output + Features.render_abstract_phrase('owner',
                                                          ind.prepare_owner(obj))
        output = output + Features.render_abstract_phrase('geometry_type',
                                                          ind.prepare_geometry_type(obj))
        output = output + Features.render_abstract_phrase('field_name',
                                                          ind.prepare_field_name(obj))
        output = output + Features.render_abstract_phrase('field_type',
                                                          ind.prepare_field_type(obj))
        output = output + Features.render_abstract_phrase('field_type_code',
                                                          ind.prepare_field_type_code(obj))
        output = output + Features.render_abstract_phrase('variable',
                                                          ind.prepare_variable(obj))
        output = output + Features.render_abstract_phrase('variable_type',
                                                          ind.prepare_variable_type(obj))
        output = output + Features.render_abstract_phrase('variable_shape',
                                                          ind.prepare_variable_shape(obj))
        output = output + Features.render_abstract_phrase('variable_descriptive_name',
                                                          ind.
                                                          prepare_variable_descriptive_name(obj))
        output = output + Features.render_abstract_phrase('variable_speciation',
                                                          ind.prepare_variable_speciation(obj))
        output = output + Features.render_abstract_phrase('site',
                                                          ind.prepare_site(obj))
        output = output + Features.render_abstract_phrase('method',
                                                          ind.prepare_method(obj))
        output = output + Features.render_abstract_phrase('quality_level',
                                                          ind.prepare_quality_level(obj))
        output = output + Features.render_abstract_phrase('data_source',
                                                          ind.prepare_data_source(obj))
        output = output + Features.render_abstract_phrase('sample_medium',
                                                          ind.prepare_sample_medium(obj))
        output = output + Features.render_abstract_phrase('units',
                                                          ind.prepare_units(obj))
        output = output + Features.render_abstract_phrase('units_type',
                                                          ind.prepare_units_type(obj))
        output = output + Features.render_abstract_phrase('extra',
                                                          ind.prepare_extra(obj))
        absolute_url = ind.prepare_absolute_url(obj)
        return absolute_url, output

    @staticmethod
    def group_resources(g):
        """ return resources of interest to a specific group """
        resources = []
        for p in GroupResourcePrivilege.objects.filter(group=g):
            resources.append(p.group)
        return resources
