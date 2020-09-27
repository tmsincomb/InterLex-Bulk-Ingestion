# InterLex-Bulk-Ingestion
Ingest entities from a CSV or Google Sheet and get the same mode of input back with additional columns added to know how it went.

# Requirements
```
python==3.7+
pandas==1.1.2+
ontquery==0.2.6+
docopt==0.6.2+
```

# Installation
```bash
git clone git@github.com:tmsincomb/InterLex-Bulk-Ingestion.git
cd InterLex-Bulk-Ingestion
pip install -e .
```

# Usage
```bash
interlex-bulk-ingest [-h | --help]
interlex-bulk-ingest [-v | --version]
interlex-bulk-ingest csv <infile> <outfile>
interlex-bulk-ingest gsheet <gsheet-name> <sheet-name>
```

# Options
```
-h --help             Display this help message
-v --version          Current version of file
-c --csv              Use CSV   
-g --gsheet           Use Google Sheets 
```
# Example
```bash
interlex-bulk-ingest -c in.csv out.csv
interlex-bulk-ingest -g <gsheets name> <sheet name>
```

# Sheet Input Example
| *label* | *type* | *synonyms* | *definition* | *comment* | *superclass* | *curie* | *preferred* |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Brain | term | Synganglion, Encephalon | The part of the central nervous system contained within the cranium comprising the forebrain, midbrain, hindbrain, and metencephalon | Does not include retina. | ILX:0108124 | UBERON:0000062 | T |

# Sheet Header Description:
| *Column header* | *Description* |  
| --- | --- |
| label  |  Entities preferred name. |
| type  |  Entity type from the following:<br><li>"term" - general entity type<br><li>"TermSet" - term to act as a set of general entity types<br><li>"pde" - personal data element<br><li>"cde" - common data element<br><li>"annotation" - entity to connect 1 entity to a value <ul> EX. anntation "hasNarrowSynonym" where<br> "nail" -> "hasNarrowSynonym" -> "claw"</ul><li>"relationship" - entity to connect to 2 other entities <ul>EX. relationship "Is part of"<br>"Forebrain" -> "Is part of" -> "Brain"</ul> |
| synonyms  |  Alternative names for the Entities label.  |
| definition  |  Detailed description of what this entity represents. |
| comment  |  Important curation notes. |
| superclass  |  Current entity the child element of the this superclass. |      
| curie  |  Existing Curie from external source or ontology. |   
| preferred  |  T/F if curie provided should be preferred ID. |

# Sheet Successful Output:
    CSV - ingestion will need an output path for resulting CSV. 
    Google Sheets - ingestion will update the sheet given automatically.
| *label* | *type* | *synonyms* | *definition* | *comment* | *superclass* | *curie* | *preferred* | *InterLex Fragment* | *InterLex IRI* | *success* | *error* |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Brain | term | Synganglion, Encephalon | The part of the central nervous system contained within the cranium comprising the forebrain, midbrain, hindbrain, and metencephalon | Does not include retina. | ILX:0108124 | UBERON:0000062 | T | ILX:0101431 | http://uri.interlex.org/base/ilx_0101431 | T | |

# Sheet Failed Output:
    CSV - ingestion will need an output path for resulting CSV. 
    Google Sheets - ingestion will update the sheet given automatically.
| *label* | *type* | *synonyms* | *definition* | *comment* | *superclass* | *curie* | *preferred* | *InterLex Fragment* | *InterLex IRI* | *success* | *error* | 
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Brain | term | Synganglion, Encephalon | The part of the central nervous system contained within the cranium comprising the forebrain, midbrain, hindbrain, and metencephalon | Does not include retina. | ILX:0108124 | UBERON:0000062 | T | ILX:0101431 | http://uri.interlex.org/base/ilx_0101431 | F | Label [Brain] already added by User [Troy Sincomb] With InterLex ID [http://uri.interlex.org/base/ilx_0101431] |