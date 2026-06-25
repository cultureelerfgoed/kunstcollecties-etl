# Kunstcollecties ETL

```mermaid
flowchart LR;
    Adlib(Adlib API) --> ETL(Github Action) --> LDV(Linked Data Voorziening)
```

## Inhoud van deze repository
Deze ETL bestaat uit de volgende onderdelen:
- de workflows in ``` .github/workflows/ ```
- tests in ``` tests/ ```
- configuratie in ``` config/ ```
- code in ``` src/ ``` die bestaat uit:
    - een mapping in ``` src/adlibxml_to_schemaorg_mapping.py ```
    - een lijst van AdlibXML xpaths in ``` src/adlib_xpaths_py ```
    - een lijst AdlibXML elementen in ``` src/adlib_tags.py ```
    - transformatie logica in ``` src/adlib_transformer.py ```
    - harvestering logica in ``` src/harvest_service.py ``` en ``` src/adlib_harvester.py ```

## Context
- Dataset op de Linked Data Voorziening [rijkscollectie-rce](https://linkeddata.cultureelerfgoed.nl/rce/rijkscollectie-rce)
- Mapping op basis van CN model, wat een minder stricte versie van het NDE schema.org applicatieprofiel is.  
- Rechten voor afbeeldingen op Memorix basis van AdlibXML
- Limieten Github Actions en Triply API.

## Running tests
``` python -m pytest -s tests/test_adlib_transformer.py ```

## Running pipeline
``` python src/harvest_service.py --chunks '6000' ```

## Current implementation model
```mermaid
%%{init: {"flowchart": {"defaultRenderer": "elk"}} }%%
flowchart TD
classDef Literal fill:#ffffff,stroke:#000000,color:;
classDef Literal_URI fill:#ffffff,stroke:#000000,color:;
classDef Multi fill:#cccccc,stroke:#000000,color:;
classDef Multi_URI fill:#cccccc,stroke:#000000,color:;
0(["schema:CreativeWork"]) -->|schema:dateCreated| 1["xsd:string"]:::Literal
2(["schema:MediaObject"]) -->|schema:thumbnailUrl| 3["xsd:anyURI"]:::Literal
0(["schema:CreativeWork"]) -->|schema:depth| 4(["schema:QuantitativeValue"])
5(["schema:Person"]) -->|schema:deathDate| 6["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:url| 7["xsd:anyURI"]:::Literal
8(["schema:Occupation"]) -->|schema:name| 9["xsd:string"]:::Literal
5(["schema:Person"]) -->|schema:name| 10["xsd:string"]:::Literal
2(["schema:MediaObject"]) -->|schema:license| 11["xsd:anyURI"]:::Literal
0(["schema:CreativeWork"]) -->|schema:material| 12(["schema:Product"])
0(["schema:CreativeWork"]) -->|schema:genre| 13(["schema:DefinedTerm"])
0(["schema:CreativeWork"]) -->|schema:associatedMedia| 2(["schema:MediaObject"])
0(["schema:CreativeWork"]) -->|schema:description| 14["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:about| 13(["schema:DefinedTerm"])
15(["schema:PropertyValue"]) -->|schema:propertyID| 16["xsd:anyURI"]:::Literal
4(["schema:QuantitativeValue"]) -->|schema:unitText| 17["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:weight| 4(["schema:QuantitativeValue"])
5(["schema:Person"]) -->|schema:birthDate| 18["xsd:string"]:::Literal
2(["schema:MediaObject"]) -->|schema:contentUrl| 19["xsd:anyURI"]:::Literal
20(["schema:Place"]) -->|schema:sameAs| 21["xsd:anyURI"]:::Literal
13(["schema:DefinedTerm"]) -->|schema:sameAs| 22["xsd:anyURI"]:::Literal
0(["schema:CreativeWork"]) -->|schema:width| 4(["schema:QuantitativeValue"])
15(["schema:PropertyValue"]) -->|schema:value| 23["xsd:string"]:::Literal
4(["schema:QuantitativeValue"]) -->|schema:value| 24["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:size| 25["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:creator| 5(["schema:Person"])
0(["schema:CreativeWork"]) -->|schema:locationCreated| 20(["schema:Place"])
0(["schema:CreativeWork"]) -->|schema:copyrightHolder| 5(["schema:Person"])
5(["schema:Person"]) -->|schema:hasOccupation| 8(["schema:Occupation"])
0(["schema:CreativeWork"]) -->|schema:height| 4(["schema:QuantitativeValue"])
2(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 0(["schema:CreativeWork"])
4(["schema:QuantitativeValue"]) -->|schema:valueReference| 26["xsd:string"]:::Literal
0(["schema:CreativeWork"]) -->|schema:isPartOf| 27["xsd:anyURI"]:::Literal
12(["schema:Product"]) -->|schema:sameAs| 28["xsd:anyURI"]:::Literal
0(["schema:CreativeWork"]) -->|schema:identifier| 15(["schema:PropertyValue"])
0(["schema:CreativeWork"]) -->|schema:name| 29["xsd:string"]:::Literal
13(["schema:DefinedTerm"]) -->|schema:name| 30["xsd:string"]:::Literal
5(["schema:Person"]) -->|schema:sameAs| 31["xsd:anyURI"]:::Literal
8(["schema:Occupation"]) -->|schema:sameAs| 32["xsd:anyURI"]:::Literal
20(["schema:Place"]) -->|schema:name| 33["xsd:string"]:::Literal
12(["schema:Product"]) -->|schema:name| 34["xsd:string"]:::Literal
15(["schema:PropertyValue"]) -->|schema:description| 35["xsd:string"]:::Literal
```