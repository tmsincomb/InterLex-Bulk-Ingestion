import unittest
import sys

from ontquery.interlex import interlex_client
import pandas as pd
import pytest

sys.path.insert(1, '../interlex_bulk_ingestion')
from interlex_bulk_ingest import IngestCSV, Schema, IngestGSheet, Validity


SCHEMA = Schema()


ENTITY = {            
    'label': 'brain',
    'type': 'term',
    'definition': 'Part of the central nervous system',
    'comment': 'Cannot live without it',
    'superclass': 'ILX:0108124', 
    'synonyms': 'Encephalon, Cerebro',
    'curie': 'UBERON:12345',
    'preferred': True
}
DF = pd.DataFrame([ENTITY])


class TestSchema:

    def setup_class(self):
        self.schema = Schema()

    def test_check_header(self):
        header = ['label', 'type', 'synonyms', 'definition', 'comment', 'superclass', 'curie', 'preferred']
        # Expected
        assert self.schema.check_header(header) == None
        # Null
        with pytest.raises(self.schema.MissingHeaders, match=str(sorted(header))):
            self.schema.check_header([])    
        # Missing
        with pytest.raises(self.schema.MissingHeaders, match=str(['superclass', 'curie', 'preferred'])):
            self.schema.check_header(header[:-3])    
        # Extra
        with pytest.raises(self.schema.ExtraHeaders , match=str(['extra_column'])):
            self.schema.check_header(header + ['extra_column'])


class TestValidity:

    def setup_class(self):
        self.validity = Validity(interlex_client().ilx_cli)

    def test_check_curie_prefix(self):
        # Prefix does exist
        real_curie = 'UBERON:0000955'
        assert self.validity.check_curie_prefix(real_curie) == None
        # Prefix does not exist
        fake_curie = 'FAKE:123'
        error = self.validity.prefix_doesnt_exist.format(curie=fake_curie)
        assert self.validity.check_curie_prefix(fake_curie) == error

    def test_check_curie_existence(self):
        # Curie does exist
        real_curie = 'UBERON:0000955'
        error = self.validity.curie_already_exists.format(curie=real_curie, ilx_id='ilx_0101431')  # todo this test will fail once this api is fixed
        assert self.validity.check_curie_existence(real_curie) == error
        # Curie does not exist
        fake_curie = 'UBERON:FakeID'
        assert self.validity.check_curie_existence(fake_curie) == None

    def test_check_label_duplicate(self):
        label = 'Brain'
        uid = '32290'
        error = self.validity.label_already_exists.format(label=label, ilx_id='ilx_0101431')
        assert self.validity.check_label_duplicate(label, uid=uid) == error
        fake_label = 'FAKELABEL'
        assert self.validity.check_label_duplicate(fake_label, uid=uid) == None

    def test_check_synonym_duplicates(self):
        uid = '32290'
        synonyms = ['FAKEID', 'Brain']
        error = self.validity.synonym_already_exists.format(synonym='Brain', ilx_id='ilx_0101431')
        assert self.validity.check_synonym_duplicates(synonyms, uid=uid) == error

    def test_check_superclass(self):
        real_superclass = 'ILX:0101431'
        assert self.validity.check_superclass(real_superclass) == None
        real_superclass = 'UBERON:0000955'
        assert self.validity.check_superclass(real_superclass) == None
        fake_superclass_prefix = 'FAKEPREFIX:0101431'
        error = self.validity.prefix_doesnt_exist.format(curie=fake_superclass_prefix)
        assert self.validity.check_superclass(fake_superclass_prefix) == error
        fake_superclass_id = 'ILX:FakeId'
        error = self.validity.superclass_doesnt_exist.format(superclass=fake_superclass_id)
        assert self.validity.check_superclass(fake_superclass_id) == error        
        fake_superclass_id = 'UBERON:FakeID'
        error = self.validity.superclass_doesnt_exist.format(superclass=fake_superclass_id)
        assert self.validity.check_superclass(fake_superclass_id) == error     