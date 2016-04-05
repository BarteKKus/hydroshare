import os
import json
import tempfile
import shutil

from lxml import etree

from rest_framework import status

from hs_core.hydroshare import resource
from .base import SciMetaTestCase


class TestScienceMetadata(SciMetaTestCase):

    def setUp(self):
        super(TestScienceMetadata, self).setUp()

        self.rtype = 'GenericResource'
        self.title = 'My Test resource'
        res = resource.create_resource(self.rtype,
                                       self.user,
                                       self.title)
        self.pid = res.short_id
        self.resources_to_delete.append(self.pid)

    def test_get_scimeta(self):
        # Get science metadata XML
        self.getScienceMetadata(self.pid)

    def test_put_scimeta_generic(self):
        # Update science metadata XML
        abstract_text = "This is an abstract"
        tmp_dir = tempfile.mkdtemp()

        try:
            # Get science metadata
            response = self.getScienceMetadata(self.pid, exhaust_stream=False)
            sci_meta_orig = os.path.join(tmp_dir, self.RESOURCE_METADATA_OLD)
            f = open(sci_meta_orig, 'w')
            for l in response.streaming_content:
                f.write(l)
            f.close()
            scimeta = etree.parse(sci_meta_orig)
            self.getAbstract(scimeta, should_exist=False)

            # Modify science metadata
            desc = scimeta.xpath('/rdf:RDF/rdf:Description[1]', namespaces=self.NS)[0]
            abs_dc_desc = etree.SubElement(desc, "{%s}description" % self.NS['dc'])
            abs_rdf_desc = etree.SubElement(abs_dc_desc, "{%s}Description" % self.NS['rdf'])
            abstract = etree.SubElement(abs_rdf_desc, "{%s}abstract" % self.NS['dcterms'])
            abstract.text = abstract_text
            # Write out to a file
            out = etree.tostring(scimeta, pretty_print=True)
            sci_meta_new = os.path.join(tmp_dir, self.RESOURCE_METADATA)
            f = open(sci_meta_new, 'w')
            f.writelines(out)
            f.close()

            #    Send updated metadata to REST API
            self.updateScimeta(self.pid, sci_meta_new)

            #    Get science metadata
            response = self.getScienceMetadata(self.pid, exhaust_stream=False)
            sci_meta_updated = os.path.join(tmp_dir, self.RESOURCE_METADATA_UPDATED)
            f = open(sci_meta_updated, 'w')
            for l in response.streaming_content:
                f.write(l)
            f.close()
            scimeta = etree.parse(sci_meta_updated)
            abstract = self.getAbstract(scimeta)
            self.assertEquals(abstract, abstract_text)

            # Make sure metadata update is idempotent
            #   Resend the previous request
            self.updateScimeta(self.pid, sci_meta_new)

            # Make sure changing the resource ID in the resource metadata causes an error
            self.updateScimetaResourceID(scimeta, 'THISISNOTARESOURCEID')
            #    Write out to a file
            out = etree.tostring(scimeta, pretty_print=True)
            f = open(sci_meta_new, 'w')
            f.writelines(out)
            f.close()

            #    Send broken metadata to REST API
            self.updateScimeta(self.pid, sci_meta_new, should_succeed=False)

        finally:
            shutil.rmtree(tmp_dir)

    def test_put_scimeta_swat_model_instance(self):
        # Update science metadata XML
        title_1 = 'Flat River SWAT Instance'
        title_2 = 'Cannon river'
        abstract_text_1 = 'This model is created for Flat River.'
        abstract_text_2 = ('This is a test to the SWAT Model Instance resource. '
                           'All the data had been obtained from real share SWAT '
                           'model from SWATShare https://mygeohub.org/groups/water-hub/swatshare. '
                           'Some of the metadata entries are assumed just used '
                           'to test the resource implementation')
        kwords_1 = ('SWAT2009', 'FlatRIver')
        kwords_2 = ('Cannon River', 'SWAT', 'SWATShare')
        model_output_1 = 'No'
        model_output_2 = 'Yes'
        model_prog_name_1 = model_prog_name_2 = 'Unspecified'
        model_prog_id_1 = model_prog_id_2 = 'None'
        tmp_dir = tempfile.mkdtemp()

        res = resource.create_resource('SWATModelInstanceResource',
                                       self.user,
                                       'Test SWAT Model Instance Resource')
        pid = res.short_id
        self.resources_to_delete.append(pid)

        try:
            # Apply metadata from saved file
            #   First update the resource ID so that it matches the ID of the
            #   newly created resource.
            scimeta = etree.parse('hs_core/tests/data/swat-resourcemetadata-1.xml')
            self.updateScimetaResourceID(scimeta, pid)
            #   Write out to a file
            out = etree.tostring(scimeta, pretty_print=True)
            sci_meta_new = os.path.join(tmp_dir, self.RESOURCE_METADATA)
            f = open(sci_meta_new, 'w')
            f.writelines(out)
            f.close()

            #   Send updated metadata to REST API
            self.updateScimeta(pid, sci_meta_new)

            #   Get science metadata
            response = self.getScienceMetadata(pid, exhaust_stream=False)
            sci_meta_updated = os.path.join(tmp_dir, self.RESOURCE_METADATA_UPDATED)
            f = open(sci_meta_updated, 'w')
            for l in response.streaming_content:
                f.write(l)
            f.close()
            scimeta = etree.parse(sci_meta_updated)
            abstract = self.getAbstract(scimeta)
            self.assertEquals(abstract, abstract_text_1)

            # Make sure metadata update is idempotent
            self.updateScimeta(pid, sci_meta_new)

            #    Get science metadata
            response = self.getScienceMetadata(pid, exhaust_stream=False)
            sci_meta_updated = os.path.join(tmp_dir, self.RESOURCE_METADATA_UPDATED)
            f = open(sci_meta_updated, 'w')
            for l in response.streaming_content:
                f.write(l)
            f.close()
            scimeta = etree.parse(sci_meta_updated)
            abstract = self.getAbstract(scimeta)
            self.assertEquals(abstract, abstract_text_1)

            # Overwrite metadata with other resource metadata
            #   First update the resource ID so that it matches the ID of the
            #   newly created resource.
            scimeta = etree.parse('hs_core/tests/data/swat-resourcemetadata-2.xml')
            self.updateScimetaResourceID(scimeta, pid)
            #   Write out to a file
            out = etree.tostring(scimeta, pretty_print=True)
            sci_meta_new = os.path.join(tmp_dir, self.RESOURCE_METADATA)
            f = open(sci_meta_new, 'w')
            f.writelines(out)
            f.close()

            #   Send updated metadata to REST API
            self.updateScimeta(pid, sci_meta_new)

            #   Get science metadata
            response = self.getScienceMetadata(pid, exhaust_stream=False)
            sci_meta_updated = os.path.join(tmp_dir, self.RESOURCE_METADATA_UPDATED)
            f = open(sci_meta_updated, 'w')
            for l in response.streaming_content:
                f.write(l)
            f.close()
            scimeta = etree.parse(sci_meta_updated)
            abstract = self.getAbstract(scimeta)
            self.assertEquals(abstract, abstract_text_2)

        finally:
            shutil.rmtree(tmp_dir)
