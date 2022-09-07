# ELG API for Morphological Analyzer for Latvian Language

This git repository contains
[ELG compatible](https://european-language-grid.readthedocs.io/en/stable/all/A3_API/LTInternalAPI.html)
Flask based REST API for [Morphological Analyzer for Latvian Language](https://github.com/PeterisP/morphology) – a Java library for analyzing morphology and part of speech information for Latvian words (v. 2.2.5). 
The analyzer is licensed under the
[GNU General Public Licence](https://github.com/PeterisP/morphology/blob/master/LICENSE.txt).
The software was developed by Pēteris Paikens from the University of Latvia,
Institute of Mathematics and Computer science.

You can call two endpoints: `word_analysis` and `wordforms`.
`word_analysis` takes a single word as an input and outputs all possible morphological readings of this word. Each reading is given: 
1) a morphological tag (e.g. 'ncmsa1'), whose first letter denotes the part of speech (e.g. 'n' – noun),
2) a set of features, partly depending on the part of speech: 'Pamatforma' (lemma), 'Skaitlis' (number), 'Locījums' (case), 'Dzimte' (gender), etc.

`wordforms` takes a single word as an input and outputs all morphological forms of this word, their morphological tags and features.

This ELG API was developed in EU's CEF project
[Microservices at your service](https://www.lingsoft.fi/en/microservices-at-your-service-bridging-gap-between-nlp-research-and-industry).

## Creating a JAR

Install [Maven](https://maven.apache.org/download.cgi), download the [Latvian morphology repository](https://github.com/lingsoft/Latvian_morphology) and run 

```
mvn install
```
Copy the `morphology-2.2.5-SNAPSHOT.jar` file from the `target` folder to the current project folder.

## Local development

Setup virtualenv, dependencies
```
python -m venv lvtagger-analysis-venv
source lvtagger-analysis -venv/bin/activate
python -m pip install -r requirements.txt
```

Run the development mode flask app
```
FLASK_ENV=development flask run --host 0.0.0.0 --port 8000
```

## Building the docker image

```
docker build -t lv-morph .
```

Or pull directly ready-made image `docker pull lingsoft/lv-morph:2.2.5-elg`.

## Deploying the service

```
docker run -d -p <port>:8000 --init lv-morph
```

## Example calls

```
curl -H 'Content-Type: application/json' -d '{"type": "text", "content": "roku"}' http://localhost:8000/process/word_analysis
```

```
curl -H 'Content-Type: application/json' -d '{"type": "text", "content": "rakt"}' http://localhost:8000/process/wordforms
```


### Response

#### `word_analysis`

```json
{
  "response": {
    "type": "texts",
    "texts": [
      {"role": "alternative",
       "content": "ncmsa1",
       "features": {
         "Šķirkļa_ID": "275453", 
         "Vārds": "roku", 
         "Šķirkļa_cilvēklasāmais_ID": "roks:1", 
         "Leksēmas_nr": "286145", 
         "Pamatforma": "roks", 
         "FreeText": "-a, v.; mūz.", 
         "Galotnes_nr": "4", 
         "Vārdšķira": "Lietvārds", 
         "Mija": "0", 
         "Minēšana": "Nav", 
         "Locījums": "Akuzatīvs", 
         "Dzimte": "Vīriešu", 
         "Vārdgrupas_nr": "1", 
         "Joma": "Mūzika", 
         "Deklinācija": "1"
         }
       },
      {"role": "alternative",
       "content": "ncmpg1",
       ...
       }
      ...
    ]
  }
}
```

#### `wordforms`

```json
{
  "response": {
    "type": "texts",
    "texts": [
      {"role": "alternative",
       "content": "vmnn0_1000n",
       "features": {
         "Laiks": "Nepiemīt", 
         "Konjugācija": "1", 
         "Skaitlis": "Nepiemīt", 
         "Šķirkļa_ID": "268218", 
         "Vārds": "rakt", 
         "Persona": "Nepiemīt", 
         "Darbības_vārda_tips": "Patstāvīgs darbības vārds", 
         "Šķirkļa_cilvēklasāmais_ID": "rakt:1", 
         "Atgriezeniskums": "Nē", 
         "Locīt_kā": "rakt", 
         "Leksēmas_nr": "278520", 
         "Pamatforma": "rakt", 
         "FreeText": "roku, roc, rok, pag. raku.", 
         "Galotnes_nr": "711", 
         "Noliegums": "Nē", 
         "Vārdšķira": "Darbības vārds", 
         "Mija": "0", 
         "Vārdgrupas_nr": "15", 
         "Izteiksme": "Nenoteiksme", 
         "Kārta": "Nepiemīt"
         }
       },
      {"role": "alternative",
       "content": "vmnif_11san",
       ...
       }
      ...
    ]
  }
}
```

More information about
[Latvian part-of-speech tagging](https://peteris.rocks/blog/latvian-part-of-speech-tagging/)

## Warning

Some characters (e.g. smileys) are not supported and may result into incorrect output. 
