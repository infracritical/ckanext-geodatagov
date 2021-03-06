import os
from nose.plugins.skip import SkipTest
from nose.tools import assert_in, assert_true, assert_equal
import ckan.model as model
import ckan.plugins as p

if p.toolkit.check_ckan_version(min_version='2.8'):
    import ckan.tests.factories as factories
    import ckan.tests.helpers as helpers
    

class TestSpatialField:

    @classmethod
    def setup_class(cls):
        if not p.toolkit.check_ckan_version(min_version='2.8'):
            raise SkipTest('Feature for CKAN 2.8')
        helpers.reset_db()
        cls.user = factories.Sysadmin(name='spatial_user')

    def test_numeric_spatial_transformation(self):

        old_geo = '10.0,0.0,15.0,5.0'

        context = {'user': self.user['name'], 'ignore_auth':True}
        pkg = {
            'title': 'Spatial num',
            'name': 'spatial-num',
            'extras': [
                {'key': 'spatial', 'value': old_geo}
                ]
        }
        dataset = p.toolkit.get_action('package_create')(context, pkg)

        expected_spatial = '{"type": "Polygon", "coordinates": [[[10.0, 0.0], [10.0, 5.0], [15.0, 5.0], [15.0, 0.0], [10.0, 0.0]]]}'
    
        spatial_extra_exists = False
        for extra in dataset['extras']:
            if extra['key'] == 'spatial':
                spatial_extra_exists = True
                assert_equal(extra['value'], expected_spatial)

        assert_true(spatial_extra_exists)

        result = helpers.call_action(
            'package_search',
            extras={'ext_bbox': '9,-1,16,4'})

        assert_equal(result['count'], 1)
        assert_equal(result['results'][0]['id'], dataset['id'])

    def test_string_spatial_transformation(self):

        old_geo = 'California'
        # require locations table to be installed

        context = {'user': self.user['name'], 'ignore_auth':True}
        pkg = {
            'title': 'Spatial String',
            'name': 'spatial-str',
            'extras': [
                {'key': 'spatial', 'value': old_geo}
                ]
        }
        dataset = p.toolkit.get_action('package_create')(context, pkg)

        expected_spatial = '{"type":"Polygon","coordinates":[[[-124.3926,32.5358],[-124.3926,42.0022],[-114.1252,42.0022],[-114.1252,32.5358],[-124.3926,32.5358]]]}'
        spatial_extra_exists = False
        for extra in dataset['extras']:
            if extra['key'] == 'spatial':
                spatial_extra_exists = True
                assert_equal(extra['value'], expected_spatial)

        assert_true(spatial_extra_exists)

        result = helpers.call_action(
            'package_search',
            extras={'ext_bbox': '-125,31,-113,43'})

        assert_equal(result['count'], 1)
        assert_equal(result['results'][0]['id'], dataset['id'])
