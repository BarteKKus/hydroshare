from django.test import TestCase
from django.contrib.auth.models import Group

from hs_access_control.models import PrivilegeCodes

from hs_core import hydroshare
from hs_core.testing import MockIRODSTestCaseMixin

from hs_access_control.tests.utilities import global_reset
from hs_core.hydroshare.features import Features
from rest_framework import status
import socket
from django.test import Client
from datetime import timedelta, datetime


class TestFeatures(MockIRODSTestCaseMixin, TestCase):

    def setUp(self):
        super(TestFeatures, self).setUp()
        global_reset()
        self.hostname = socket.gethostname()
        self.resource_url = "/resource/{res_id}/"
        self.client = Client(HTTP_USER_AGENT='Mozilla/5.0')  # fake use of a real browser
        self.group, _ = Group.objects.get_or_create(name='Hydroshare Author')
        self.end_date = datetime.now() + timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=2)
        self.admin = hydroshare.create_account(
            'admin@gmail.com',
            username='admin',
            first_name='administrator',
            last_name='couch',
            superuser=True,
            groups=[]
        )

        self.cat = hydroshare.create_account(
            'cat@gmail.com',
            username='cat',
            password='foobar',
            first_name='not a dog',
            last_name='last_name_cat',
            superuser=False,
            groups=[]
        )

        self.cats = self.cat.uaccess.create_group(
            title='cats', description="We are the cats")

        self.posts = hydroshare.create_resource(
            resource_type='GenericResource',
            owner=self.cat,
            title='all about scratching posts',
            metadata=[],
        )
        self.cat.uaccess.share_resource_with_group(self.posts, self.cats, PrivilegeCodes.VIEW)

        self.dog = hydroshare.create_account(
            'dog@gmail.com',
            username='dog',
            password='barfoo',
            first_name='not a cat',
            last_name='last_name_dog',
            superuser=False,
            groups=[]
        )

        self.dogs = self.dog.uaccess.create_group(
            title='dogs', description="We are the dogs")

        self.bones = hydroshare.create_resource(
            resource_type='GenericResource',
            owner=self.dog,
            title='all about bones',
            metadata=[],
        )

        self.squirrel = hydroshare.create_account(
            'squirrel@gmail.com',
            username='squirrel',
            first_name='first_name_squirrel',
            last_name='last_name_squirrel',
            superuser=False,
            groups=[]
        )

        self.pinecorns = hydroshare.create_resource(
            resource_type='GenericResource',
            owner=self.squirrel,
            title='all about pinecorns',
            metadata=[],
        )

        self.dog.uaccess.share_resource_with_group(self.bones, self.dogs, PrivilegeCodes.VIEW)

        self.cat.uaccess.share_resource_with_user(self.posts, self.squirrel, PrivilegeCodes.CHANGE)

        self.cat.uaccess.share_group_with_user(self.cats, self.squirrel, PrivilegeCodes.CHANGE)
        self.client.login(username='dog', password='barfoo')

    def test_resource_owner(self):
        records = Features.resource_owners()
        self.assertEqual(len(records), 3)
        test = [(self.cat.username, self.posts.short_id),
                (self.dog.username, self.bones.short_id),
                (self.squirrel.username, self.pinecorns.short_id)]
        self.assertCountEqual(test, records)

    def test_group_onwer(self):
        records = Features.group_owners()
        self.assertEqual(len(records), 2)
        test = [(self.cat.username, self.cats.name), (self.dog.username, self.dogs.name)]
        self.assertCountEqual(test, records)

    def test_resource_editors(self):
        records = Features.resource_editors()
        self.assertEqual(len(records), 4)
        test = [(self.cat.username, self.posts.short_id),
                (self.dog.username, self.bones.short_id),
                (self.squirrel.username, self.pinecorns.short_id),
                (self.squirrel.username, self.posts.short_id)]
        self.assertCountEqual(test, records)

    def test_group_editors(self):
        records = Features.group_editors()
        self.assertEqual(len(records), 3)
        test = [(self.cat.username, self.cats.name),
                (self.dog.username, self.dogs.name),
                (self.squirrel.username, self.cats.name)]
        self.assertCountEqual(test, records)

    def test_resource_viewers(self):
        response = self.client.get(self.resource_url.format(res_id=self.bones.short_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        records = Features.resource_viewers(self.start_date, self.end_date)
        test = {}
        test[self.bones.short_id] = [self.dog.username]
        self.assertEqual(len(records), 1)
        self.assertCountEqual(records[self.bones.short_id], test[self.bones.short_id])

    def test_visited_resources(self):
        response = self.client.get(self.resource_url.format(res_id=self.bones.short_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        records = Features.visited_resources(self.start_date, self.end_date)
        test = {}
        test[self.dog.username] = [self.bones.short_id]
        self.assertEqual(len(records), 1)
        self.assertCountEqual(records[self.dog.username], test[self.dog.username])