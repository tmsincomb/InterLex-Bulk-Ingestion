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

from docopt import docopt
from ontquery.interlex import interlex_client
import pandas as pd

from pathing import pathing

VERSION = '0.1.1'


class Schema:
    
    class Error(Exception):
        """Script could not complete."""
    
    class MissingHeader(Error):
        """Missing Header."""

    columns = ['label', 'type', 'synonyms', 'definition', 'comment', 'superclass', 'curie', 'preferred']
    error = 'Label [{label}] already exists from User [{user}] where InterLex ID is [{ilx_id}]'

    def check_ingest_header(self, df: pd.DataFrame) -> None:
        for column in df.columns:
            if column not in self.columns:
                raise ValueError(f'{column} is missing in sheet')

class IngestCSV(Schema):

    def __init__(self, csv_in: str, csv_out: str, ilx_cli):
        Schema.__init__(self)
        self.ilx_cli = ilx_cli
        self.prefix2namespace = {d['prefix']: d['namespace'] 
                                 for d in self.ilx_cli._get('curies/catalog').json()['data'] 
                                 if d['prefix']}
        self.csv_in_path = pathing(csv_in, new=False)
        self.csv_out_path = pathing(csv_out, new=False).with_suffix('.csv')
        self.csv_in_df = pd.read_csv(self.csv_in_path)
        self.check_ingest_header(self.csv_in_df)

    def check_if_duplicate(self, row):
        # curie check
        # embed()
        result = self.ilx_cli.get_entity_from_curie(row.curie)
        if result['ilx']:
            return result
        # label check 
        result = self.ilx_cli._get('term/exists', params={'label': row.label, 'uid':ilx_cli.user_id}).json()['data']
        if result:
            return result[0]
        
    def expand_synonyms(self, synonyms):
        synonyms = [syn.strip() for syn in synonyms.split(',')]
        return synonyms

    def check_curie(self, curie):
        try:
            prefix, _id = curie.rsplit(':', 1)
            namespace = self.prefix2namespace[prefix]
        except:
            return f'Curie {curie} does not have a prefix that exists in InterLex.'    
    
    def expand_curie(self, curie, preferred):
        prefix, _id = curie.rsplit(':', 1)
        namespace = self.prefix2namespace[prefix]
        existing_ids = [{
            'iri': namespace + _id,
            'curie': curie,
            'preferred': 1 if str(preferred).lower() in ['t', 'true', '1'] else 0
        }]
        return existing_ids

    def check_superclass(self, superclass):
        if any([superclass.startswith(prefix) for prefix in ['ILX:', 'TMP:', 'ilx_', 'tmp_']]):
            result = self.ilx_cli.get_entity(superclass)
        else:
            error = self.check_curie(superclass)
            if error:
                return error
            result = self.ilx_cli.get_entity_from_curie(superclass)
        if not result['ilx']:
            return f'Superclass {superclass} does not exist in InterLex.'

    def ingest_csv(self) -> None:
        df = self.csv_in_df.copy()
        df['error'] = None
        df['success'] = None
        df['InterLex Fragment'] = None
        for i, row in self.csv_in_df.iterrows():
            error = self.check_curie(row.curie)
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
                continue
            error = self.check_superclass(row.superclass)
            if error:
                df.at[i, 'error'] = error
                df.at[i, 'success'] = 'F'
                continue
            result = self.check_if_duplicate(row) 
            if result:
                df.at[i, 'error'] = self.error.format(label=result['label'], user=result['uid'], ilx_id=result['ilx'])
                df.at[i, 'success'] = 'F'
            else:
                df.at[i, 'error'] = None
                df.at[i, 'success'] = 'T'
                result = self.ilx_cli.add_entity(
                    label=row['label'],
                    type=row['type'],
                    definition=row['definition'],
                    comment=row['comment'],
                    synonyms=self.expand_synonyms(row.synonyms),
                    superclass=row['superclass'],
                    existing_ids=self.expand_curie(row.curie, row.preferred)
                )
            df.at[i, 'InterLex Fragment'] = result['ilx']
        return df

class IngestGSheet(Schema):
    pass


if __name__ == '__main__':
    doc = docopt(__doc__, version=VERSION) 
    print(doc)
    ilx_cli = interlex_client('scicrunch.org') if doc['--production'] else interlex_client()
    ilx_cli = ilx_cli.ilx_cli  # Simple InterLex API
    if doc['--csv']:
        icsv = IngestCSV(doc['<csv-in>'], doc['<csv-out>'], ilx_cli)
        df = icsv.ingest_csv()
        df.to_csv(icsv.csv_out_path, index=False)
    elif doc['--gsheet']:
        pass
