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
0(["schema:Person"]) -->|schema:birthDate| 1["xsd:string"]:::Literal
2(["schema:Organization"]) -->|schema:contactPoint| 3(["schema:ContactPoint"])
4(["schema:CreativeWork"]) -->|schema:isPartOf| 5["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:about| 6(["schema:DefinedTerm"])
7(["schema:QuantitativeValue"]) -->|schema:valueReference| 8["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:genre| 6(["schema:DefinedTerm"])
4(["schema:CreativeWork"]) -->|schema:identifier| 9(["schema:PropertyValue"])
4(["schema:CreativeWork"]) -->|schema:width| 7(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:depth| 7(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:locationCreated| 10(["schema:Place"])
11(["schema:Product"]) -->|schema:sameAs| 12["xsd:anyURI"]:::Literal
10(["schema:Place"]) -->|schema:name| 13["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:dateCreated| 14["xsd:string"]:::Literal
0(["schema:Person"]) -->|schema:deathDate| 15["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:size| 16["xsd:string"]:::Literal
6(["schema:DefinedTerm"]) -->|schema:sameAs| 17["xsd:anyURI"]:::Literal
2(["schema:Organization"]) -->|schema:name| 18["xsd:string"]:::Literal
0(["schema:Person"]) -->|schema:name| 19["xsd:string"]:::Literal
9(["schema:PropertyValue"]) -->|schema:propertyID| 20["xsd:anyURI"]:::Literal
7(["schema:QuantitativeValue"]) -->|schema:unitText| 21["xsd:string"]:::Literal
3(["schema:ContactPoint"]) -->|schema:name| 22["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:material| 11(["schema:Product"])
4(["schema:CreativeWork"]) -->|schema:associatedMedia| 23(["schema:MediaObject"])
6(["schema:DefinedTerm"]) -->|schema:name| 24["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:name| 25["xsd:string"]:::Literal
3(["schema:ContactPoint"]) -->|schema:email| 26["xsd:string"]:::Literal
23(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 4(["schema:CreativeWork"])
4(["schema:CreativeWork"]) -->|schema:description| 27["xsd:string"]:::Literal
2(["schema:Organization"]) -->|schema:sameAs| 28["xsd:anyURI"]:::Literal
7(["schema:QuantitativeValue"]) -->|schema:value| 29["xsd:string"]:::Literal
10(["schema:Place"]) -->|schema:sameAs| 30["xsd:anyURI"]:::Literal
2(["schema:Organization"]) -->|schema:identifier| 31["xsd:string"]:::Literal
23(["schema:MediaObject"]) -->|schema:contentUrl| 32["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:creator| 0(["schema:Person"])
9(["schema:PropertyValue"]) -->|schema:value| 33["xsd:string"]:::Literal
9(["schema:PropertyValue"]) -->|schema:description| 34["xsd:string"]:::Literal
2(["schema:Organization"]) -->|schema:alternateName| 35["xsd:string"]:::Literal
11(["schema:Product"]) -->|schema:name| 36["xsd:string"]:::Literal
0(["schema:Person"]) -->|schema:sameAs| 37["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:height| 7(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:weight| 7(["schema:QuantitativeValue"])
```