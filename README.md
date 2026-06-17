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
0(["schema:QuantitativeValue"]) -->|schema:unitText| 1["xsd:string"]:::Literal
2(["schema:Occupation"]) -->|schema:sameAs| 3["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:name| 5["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:weight| 0(["schema:QuantitativeValue"])
6(["schema:Place"]) -->|schema:sameAs| 7["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:isPartOf| 8["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:associatedMedia| 9(["schema:MediaObject"])
10(["schema:Product"]) -->|schema:sameAs| 11["xsd:anyURI"]:::Literal
0(["schema:QuantitativeValue"]) -->|schema:valueReference| 12["xsd:string"]:::Literal
13(["schema:DefinedTerm"]) -->|schema:name| 14["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:genre| 13(["schema:DefinedTerm"])
4(["schema:CreativeWork"]) -->|schema:height| 0(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:dateCreated| 15["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:depth| 0(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:material| 10(["schema:Product"])
16(["schema:Person"]) -->|schema:name| 17["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:description| 18["xsd:string"]:::Literal
2(["schema:Occupation"]) -->|schema:name| 19["xsd:string"]:::Literal
20(["schema:PropertyValue"]) -->|schema:propertyID| 21["xsd:anyURI"]:::Literal
6(["schema:Place"]) -->|schema:name| 22["xsd:string"]:::Literal
20(["schema:PropertyValue"]) -->|schema:value| 23["xsd:string"]:::Literal
16(["schema:Person"]) -->|schema:birthDate| 24["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:identifier| 20(["schema:PropertyValue"])
4(["schema:CreativeWork"]) -->|schema:size| 25["xsd:string"]:::Literal
16(["schema:Person"]) -->|schema:deathDate| 26["xsd:string"]:::Literal
4(["schema:CreativeWork"]) -->|schema:copyrightHolder| 16(["schema:Person"])
0(["schema:QuantitativeValue"]) -->|schema:value| 27["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:contentUrl| 28["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:width| 0(["schema:QuantitativeValue"])
4(["schema:CreativeWork"]) -->|schema:locationCreated| 6(["schema:Place"])
13(["schema:DefinedTerm"]) -->|schema:sameAs| 29["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:creator| 16(["schema:Person"])
16(["schema:Person"]) -->|schema:sameAs| 30["xsd:anyURI"]:::Literal
4(["schema:CreativeWork"]) -->|schema:about| 13(["schema:DefinedTerm"])
16(["schema:Person"]) -->|schema:hasOccupation| 2(["schema:Occupation"])
20(["schema:PropertyValue"]) -->|schema:description| 31["xsd:string"]:::Literal
10(["schema:Product"]) -->|schema:name| 32["xsd:string"]:::Literal
9(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 4(["schema:CreativeWork"])
```