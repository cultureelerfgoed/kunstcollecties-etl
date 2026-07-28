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
``` python -m pytest -s tests ```

## Running pipeline
``` python src/harvest_service.py --chunks '6000' ```

## Current implementation model
```mermaid
---
  config:
    nodeSpacing: 50
    rankSpacing: 250
    defaultRenderer: elk
---
flowchart TD
classDef Literal fill:#ffffff,stroke:#000000,color:;
classDef Literal_URI fill:#ffffff,stroke:#000000,color:;
classDef Multi fill:#cccccc,stroke:#000000,color:;
classDef Multi_URI fill:#cccccc,stroke:#000000,color:;
0(["schema:PropertyValue"]) -->|schema:propertyID| 1["xsd:anyURI"]:::Literal
2(["schema:Occupation"]) -->|schema:sameAs| 3["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:material| 5(["schema:Product"])
4(["schema:CreativeWork"]) -->|schema:keywords| 6(["schema:DefinedTerm"])
7(["schema:QuantitativeValue"]) -->|schema:unitText| 8["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:license| 10["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:locationCreated| 11(["schema:Place"])
4(["schema:CreativeWork"]) -->|schema:license| 12["xsd:string"]:::Literal
5(["schema:Product"]) -->|schema:name| 13["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:url| 14["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:isPartOf| 15["xsd:anyURI"]:::Literal
16(["schema:Person"]) -->|schema:birthDate| 17["xsd:string"]:::Literal
5(["schema:Product"]) -->|schema:sameAs| 18["xsd:anyURI"]:::Literal
11(["schema:Place"]) -->|schema:sameAs| 19["xsd:anyURI"]:::Literal
11(["schema:Place"]) -->|schema:name| 20["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:description| 21["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:thumbnailUrl| 22["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:publisher| 23["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:associatedMedia| 9(["schema:MediaObject"])
16(["schema:Person"]) -->|schema:hasOccupation| 2(["schema:Occupation"])
4(["schema:CreativeWork"]) -->|schema:alternateName| 24["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:contentUrl| 25["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:temporal| 26["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:creator| 16(["schema:Person"])
16(["schema:Person"]) -->|schema:name| 27["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:identifier| 0(["schema:PropertyValue"])
16(["schema:Person"]) -->|schema:sameAs| 28["xsd:anyURI"]:::Literal
0(["schema:PropertyValue"]) -->|schema:value| 29["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 4(["schema:CreativeWork"])
4(["schema:CreativeWork"]) -->|schema:genre| 6(["schema:DefinedTerm"])
4(["schema:CreativeWork"]) -->|schema:size| 7(["schema:QuantitativeValue"])
16(["schema:Person"]) -->|schema:deathDate| 30["xsd:string"]:::Literal
7(["schema:QuantitativeValue"]) -->|schema:valueReference| 31["xsd:string"]:::Literal
0(["schema:PropertyValue"]) -->|schema:description| 32["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:copyrightHolder| 16(["schema:Person"])
2(["schema:Occupation"]) -->|schema:name| 33["xsd:string"]:::Literal
6(["schema:DefinedTerm"]) -->|schema:name| 34["xsd:string"]:::Literal
6(["schema:DefinedTerm"]) -->|schema:sameAs| 35["xsd:anyURI"]:::Literal
7(["schema:QuantitativeValue"]) -->|schema:value| 36["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:name| 37["xsd:string"]:::Literal
```