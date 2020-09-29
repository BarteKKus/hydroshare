import pytest
import json


@pytest.mark.django_db
def test_search_term_found_in_title(admin_client, public_resource_with_metadata):
    """
    Test of direct URL querystring for a search
    Test valid JSON response
    Test index response
    Test title match in search
    """
    search_term = public_resource_with_metadata.title
    djangoresponse = admin_client.get('/discoverapi/?q={}'.format(search_term), follow=True)
    response = json.loads(djangoresponse.content.decode("utf-8"))
    resources = response['resources']
    assert djangoresponse.status_code == 200
    assert search_term in json.loads(resources)[0]['title']


@pytest.mark.django_db
def test_bad_filter_json_format(admin_client, public_resource_with_metadata):
    """
    Test 400 status code
    Test malformed JSON handled with descriptive message to client
    Test filter attribute parsed and triggered
    """
    query_filter = {'malformed': 'json'}
    djangoresponse = admin_client.get('/discoverapi/?filter={}'.format(query_filter), follow=True)
    response = json.loads(djangoresponse.content.decode("utf-8"))
    assert djangoresponse.status_code == 400
    assert "Filter JSON parsing error" in response['message']


@pytest.mark.django_db
def test_filter_by_atribute(admin_client, public_resource_with_metadata, private_resource_with_metadata):
    """
    Test passing some but not all filter attributes
    Test filter by attribute
    """
    query_filter = {"availability": ["public"]}
    djangoresponse = admin_client.get('/discoverapi/?filter={}'.format(json.dumps(query_filter)), follow=True)
    response = json.loads(djangoresponse.content.decode("utf-8"))
    short_ids = [x['short_id'] for x in json.loads(response['resources'])]
    assert djangoresponse.status_code == 200
    assert public_resource_with_metadata.short_id in short_ids
    assert private_resource_with_metadata.short_id not in short_ids


@pytest.mark.django_db
def test_filter_by_bad_date(admin_client, public_resource_with_metadata):
    """
    Test passing malformed date string
    """
    query_filter = {"date": ["2019-11-01", "bad-date"]}
    djangoresponse = admin_client.get('/discoverapi/?filter={}'.format(json.dumps(query_filter)), follow=True)
    response = json.loads(djangoresponse.content.decode("utf-8"))
    assert djangoresponse.status_code == 400
    assert "date parsing error" in response['message']


@pytest.mark.django_db
def test_filter_by_missing_date(admin_client, public_resource_with_metadata):
    """
    Test passing malformed date array/list
    """
    query_filter = {"date": ["2019-11-01"]}
    djangoresponse = admin_client.get('/discoverapi/?filter={}'.format(json.dumps(query_filter)), follow=True)
    response = json.loads(djangoresponse.content.decode("utf-8"))
    assert djangoresponse.status_code == 400
    assert "date parsing error" in response['message']
