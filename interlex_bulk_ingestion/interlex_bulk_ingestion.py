""" 
Bulk ingestion via CSV file or Google Sheets. 

Usage:
    interlex-bulk-ingest [-h | --help]
    interlex-bulk-ingest [-v | --version]
    interlex-bulk-ingest (-c|--csv) [-p|--production] <csv-in> <csv-out>
    interlex-bulk-ingest (-g|--gsheet) [-p|--production] <gsheet-name> <sheet-name>

Options:
    -h --help           Display this help message
    -v --version        Current version of file
    -c --csv            Use CSV   
    -g --gsheet         Use Google Sheets 
    -p --production     Ingest into production. Default is test3

Examples for Testing:
    interlex-bulk-ingest -c in.csv out.csv
    interlex-bulk-ingest -g <gsheets name> <sheet name>

Examples for Production:
    interlex-bulk-ingest -c -p in.csv out.csv
    interlex-bulk-ingest -g -p <gsheets name> <sheet name>

Sheet Example:
    ---------------------------------------------------------------------------------------------------------------------------------------------------------
    | label | type | synonyms                | definition                             | comment                  | superclass  | curie          | preferred |
    ---------------------------------------------------------------------------------------------------------------------------------------------------------
    | Brain | term | Synganglion, Encephalon | The part of the central nervous system | Does not include retina. | ILX:0108124 | UBERON:0000062 | T         |
    |       |      |                         | contained within the cranium,          |                          |             |                |           |
    |       |      |                         | comprising the forebrain, midbrain,    |                          |             |                |           | 
    |       |      |                         | hindbrain, and metencephalon           |                          |             |                |           | 
    ---------------------------------------------------------------------------------------------------------------------------------------------------------            
  
Sheet Header Description:  
    ---------------------------------------------------------------------------------------
    |          label  |  Entities preferred name.                                         |
    ---------------------------------------------------------------------------------------
    |           type  |  Entity type from the following:                                  |
    |                 |          "term"  -  general entity type                           |
    |                 |       "TermSet"  -  term to act as a set of general entity types  |
    |                 |           "pde"  -  personal data element                         |
    |                 |           "cde"  -  common data element                           |
    |                 |    "annotation"  -  entity to connect 1 entity to a value         |
    |                 |                     EX. anntation "hasNarrowSynonym" where        |
    |                 |                         "nail" -> "hasNarrowSynonym" -> "claw"    |
    |                 |  "relationship"  -  entity to connect to 2 other entities         |
    |                 |                     EX. relationship "Is part of"                 |
    |                 |                         "Forebrain" -> "Is part of" -> "Brain"    |
    ---------------------------------------------------------------------------------------
    |       synonyms  |  Alternative names for the Entities label.                        |
    ---------------------------------------------------------------------------------------
    |     definition  |  Detailed description of what this entity represents.             |
    ---------------------------------------------------------------------------------------
    |        comment  |  Important curation notes.                                        |
    ---------------------------------------------------------------------------------------
    |     superclass  |  Current entity the child element of the this superclass.         |      
    ---------------------------------------------------------------------------------------
    |          curie  |  Existing Curie from external source or ontology.                 |   
    ---------------------------------------------------------------------------------------
    |      preferred  |  T/F if curie provided should be preferred ID.                    |
    ---------------------------------------------------------------------------------------                                          
"""
from IPython import embed
from typing import Union, List, Dict

from docopt import docopt
from ontquery.interlex import interlex_client
import pandas as pd

from .pathing import pathing

VERSION = '0.1.2'


class Schema:

    class MissingHeaders(Exception):
        """Missing headers."""

    class ExtraHeaders(Exception):
        """Extra headers."""

    columns = ['label', 'type', 'synonyms', 'definition', 'comment', 'superclass', 'curie', 'preferred']
    duplicate_error = 'Label [{label}] already exists from User [{user}] where InterLex ID is [{ilx_id}]'

    def check_header(self, columns: list) -> None:
        """
        Checks if header has extra column(s) or missing column(s).

        Args:
            columns (list): InterLex entity fields

        Raises:
            self.ExtraHeaders: Additional headers will break code
            self.MissingHeaders: Missing headers will potentially break code
        """
        extra_columns = set(columns) - set(self.columns)
        if extra_columns:
            raise self.ExtraHeaders(str(sorted(extra_columns)))
        missing_columns = set(self.columns) - set(columns)
        if missing_columns:
            raise self.MissingHeaders(str(sorted(missing_columns)))

class Validity:

    prefix_doesnt_exist = 'Curie {curie} does not have a prefix that exists in InterLex.'
    curie_already_exists = 'Curie {curie} already exists with InterLex ID {ilx_id}'
    superclass_doesnt_exist = 'Superclass {superclass} does not exist in InterLex.'
    label_already_exists = 'Label {label} already exists with InterLex ID {ilx_id}'
    synonym_already_exists = 'Synonym {synonym} already exists in InterLex with ID {ilx_id}'

    def __init__(self, ilx_cli):
        self.ilx_cli = ilx_cli
        self.prefix2namespace = {d['prefix']: d['namespace'] 
                                 for d in self.ilx_cli._get('curies/catalog').json()['data'] 
                                 if d['prefix']}

    def check_curie_prefix(self, curie: str) -> None:
        """
        Checks InterLex curie catalog for known prefixes so we can expand it into a proper iri.

        Args:
            curie (str): iri prefix concatenated to an id with a colon i.e. pr

        Returns:
            None: If prefix exists.
            str: If prefix not not exists.
        """
        try:
            prefix, _id = curie.rsplit(':', 1)
            namespace = self.prefix2namespace[prefix]
        except:
            return self.prefix_doesnt_exist.format(curie=curie)  
    
    def check_curie_existence(self, curies: list) -> None:
        """
        If the curie exists this check fails.

        Args:
            curies (list): Existing Ids for the entity in the prefix:id format.

        Returns:
            None: If curie doesn't exist.
            str: If curie does exist.
        """
        for curie in curies.split(','):
            curie = curie.strip()
            error = self.check_curie_prefix(curie)
            if error: 
                return error
            result = self.ilx_cli.get_entity_from_curie(curie)
            if result['ilx']: 
                return self.curie_already_exists.format(curie=curie, ilx_id=result['ilx'])
    
    def check_superclass(self, superclass: str) -> None:
        """
        If superclass does not exist this check fails.

        Args:
            superclass (str): Parent of current entity in it's prefix:id format.

        Returns:
            None: If superclass exists.
            str: If superclass doesn't exist.
        """
        if any([superclass.startswith(prefix) for prefix in ['ILX:', 'TMP:', 'ilx_', 'tmp_']]):
            result = self.ilx_cli.get_entity(superclass)
        else:
            error = self.check_curie_prefix(superclass)
            if error:
                return error
            result = self.ilx_cli.get_entity_from_curie(superclass)
        if not result['ilx']:
            return self.superclass_doesnt_exist.format(superclass=superclass)

    def check_label_duplicate(self, label: str, uid: str = None) -> None:
        """
        If label already exists from the user, this check fails.

        Args:
            label (str): Entity preferred label.
            uid (str, optional): User ID. Defaults to None.

        Returns:
            None: If label doesn't exist yet.
            str: If label does exist.
        """
        result = self.ilx_cli._get('term/exists', params={'label': label, 'uid': uid or self.ilx_cli.user_id}).json()['data']
        if result:
            result = result[0]
            return self.label_already_exists.format(label=result['label'], ilx_id=result['ilx'])
        
    def check_synonym_duplicates(self, synonyms: list, uid: str = None) -> None:
        """
        If synonym already exists from the user, this check fails.

        Args:
            synonym (str): Entity alternative label.
            uid (str, optional): User ID. Defaults to None.

        Returns:
            None: If synonym doesn't exist yet.
            str: If synonym does exist.
        """
        for synonym in synonyms:
            params = {'label': synonym, 'uid': uid or self.ilx_cli.user_id}
            result = self.ilx_cli._get('term/exists', params=params).json()['data']
            if result:
                result = result[0]
                return self.synonym_already_exists.format(synonym=result['label'], ilx_id=result['ilx'])      


class IngestCSV(Schema, Validity):
    """
    InterLex entity ingestion through a CSV.

    Args:
        Schema ([type]): Header Check
        Validity ([type]): Entity Field Checks
    """
    def __init__(self, csv_in: str, csv_out: str, ilx_cli):
        Schema.__init__(self)
        Validity.__init__(self, ilx_cli)
        self.csv_in_path = pathing(csv_in, new=False)
        self.csv_out_path = pathing(csv_out, new=False).with_suffix('.csv')
        self.csv_in_df = pd.read_csv(self.csv_in_path)
        self.check_header(self.csv_in_df.columns)
        
    def expand_synonyms(self, synonyms: list) -> List[str]:
        """
        Makes sure synonyms delimited with a comma are counted as a list

        Args:
            synonyms (list): Alternate labels delimited by a comma

        Returns:
            list: list of synonyms
        """
        synonyms = [syn.strip() for syn in synonyms.split(',')]
        return synonyms
    
    def expand_curie(self, curie: str, preferred: str) -> list:
        """
        Expand curie to its iri to create an existing_id dictionary 

        Args:
            curie (str): Existing Ids for the entity in the prefix:id format.
            preferred (str): True if curie is preferred ID for entity.

        Returns:
            list: existing_id entry ready for server.
        """
        prefix, _id = curie.rsplit(':', 1)
        namespace = self.prefix2namespace[prefix]
        existing_ids = [{
            'iri': namespace + _id,
            'curie': curie,
            'preferred': 1 if str(preferred).lower() in ['t', 'true', '1'] else 0
        }]
        return existing_ids

    def ingest_csv(self) -> None:
        """
        Iterate through the CSV and validate each field. If no checks are raised the entity is added.

        Returns:
            pd.DataFrame: pandas dataframe to be converted back into a CSV.
        """
        df = self.csv_in_df.copy()
        df['error'] = None
        df['success'] = None
        df['InterLex Fragment'] = None
        for i, row in self.csv_in_df.iterrows():
            synonyms = self.expand_synonyms(row.synonyms)
            error = self.check_synonym_duplicates(synonyms)
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
                continue
            error = self.check_curie_existence(row.curie)
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
                continue
            error = self.check_superclass(row.superclass)
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
                continue
            error = self.check_label_duplicate(row.label) 
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
            else:
                df.at[i, 'error'] = None
                df.at[i, 'success'] = 'T'
                result = self.ilx_cli.add_entity(
                    label=row['label'],
                    type=row['type'],
                    definition=row['definition'],
                    comment=row['comment'],
                    synonyms=synonyms,
                    superclass=row['superclass'],
                    existing_ids=self.expand_curie(row.curie, row.preferred)
                )
                df.at[i, 'InterLex Fragment'] = result['ilx']
        return df


class IngestGSheet(Schema):
    pass


def main():
    doc = docopt(__doc__, version=VERSION) 
    ilx_cli = interlex_client('scicrunch.org') if doc['--production'] else interlex_client()
    ilx_cli = ilx_cli.ilx_cli  # Simple InterLex API
    if doc['--csv']:
        icsv = IngestCSV(doc['<csv-in>'], doc['<csv-out>'], ilx_cli)
        df = icsv.ingest_csv()
        df.to_csv(icsv.csv_out_path, index=False)
    elif doc['--gsheet']:
        pass

if __name__ == '__main__':
    main()
