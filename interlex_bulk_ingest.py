""" 
Bulk ingestion via CSV file or Google Sheets. 

CSV input - ingestion will need an output CSV path 
Google Sheets - ingestion will update the sheet give automatically

Usage:
    interlex-bulk-ingest [-h | --help]
    interlex-bulk-ingest [-v | --version]
    interlex-bulk-ingest (-c|--csv) <csv-in> <csv-out>
    interlex-bulk-ingest (-g|--gsheet) <gsheet-name> <sheet-name>

Options:
    -h --help           Display this help message
    -v --version        Current version of file
    -c --csv            Use CSV   
    -g --gsheet         Use Google Sheets 

Example:
    interlex-bulk-ingest -c in.csv out.csv
    interlex-bulk-ingest -g <gsheets name> <sheet name>

Output:
    CSV - ingestion will need an output path for resulting CSV. 
    Google Sheets - ingestion will update the sheet given automatically.

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
from docopt import docopt
VERSION = '0.1.0'

if __name__ == '__main__':
    doc = docopt(__doc__, version=VERSION) 
    print(doc)      