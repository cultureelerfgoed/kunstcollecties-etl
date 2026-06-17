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
0(["schema:DefinedTerm"]) -->|schema:sameAs| 1["xsd:anyURI"]:::Literal
2(["schema:Person"]) -->|schema:hasOccupation| 3(["schema:Occupation"])
4(["schema:CreativeWork"]) -->|schema:height| 5(["schema:QuantitativeValue"])
6(["schema:PropertyValue"]) -->|schema:value| 7["xsd:string"]:::Literal
2(["schema:Person"]) -->|schema:sameAs| 8["xsd:anyURI"]:::Literal
9(["schema:Product"]) -->|schema:name| 10["xsd:string"]:::Literal
11(["schema:Place"]) -->|schema:sameAs| 12["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:creator| 2(["schema:Person"])
3(["schema:Occupation"]) -->|schema:sameAs| 13["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:locationCreated| 11(["schema:Place"])
0(["schema:DefinedTerm"]) -->|schema:name| 14["xsd:string"]:::Literal
5(["schema:QuantitativeValue"]) -->|schema:valueReference| 15["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:material| 9(["schema:Product"])
6(["schema:PropertyValue"]) -->|schema:description| 16["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:description| 17["xsd:string"]:::Literal
2(["schema:Person"]) -->|schema:birthDate| 18["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:copyrightHolder| 2(["schema:Person"])
11(["schema:Place"]) -->|schema:name| 19["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:isPartOf| 20["xsd:anyURI"]:::Literal
2(["schema:Person"]) -->|schema:name| 21["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:dateCreated| 22["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:weight| 5(["schema:QuantitativeValue"])
3(["schema:Occupation"]) -->|schema:name| 23["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:width| 5(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:associatedMedia| 24(["schema:MediaObject"])
2(["schema:Person"]) -->|schema:deathDate| 25["xsd:string"]:::Literal
24(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 4(["schema:CreativeWork"])
4(["schema:CreativeWork"]) -->|schema:depth| 5(["schema:QuantitativeValue"])
9(["schema:Product"]) -->|schema:sameAs| 26["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:name| 27["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:genre| 0(["schema:DefinedTerm"])
24(["schema:MediaObject"]) -->|schema:contentUrl| 28["xsd:anyURI"]:::Literal
6(["schema:PropertyValue"]) -->|schema:propertyID| 29["xsd:anyURI"]:::Literal
5(["schema:QuantitativeValue"]) -->|schema:value| 30["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:identifier| 6(["schema:PropertyValue"])
4(["schema:CreativeWork"]) -->|schema:size| 31["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:about| 0(["schema:DefinedTerm"])
5(["schema:QuantitativeValue"]) -->|schema:unitText| 32["xsd:string"]:::Literal
```