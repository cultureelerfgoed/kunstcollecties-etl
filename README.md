# Kunstcollecties ETL

## Inhoud van deze repository
Deze ETL bestaat uit de volgende onderdelen:
- de workflows in ``` .github/workflows/ ```
- tests in ``` tests/ ```
- configuratie in ``` config/ ```
- code in ``` src/ ``` die bestaat uit:
    - een mapping in ``` src/oai_to_schemaorg_mapping.py ```
    - een lijst van AdlibXML xpaths in ``` src/oai_xpaths_py ``` of ``` src/adlib_xpaths_py ```
    - een lijst AdlibXML elementen in ``` src/oai_tags.py ```
    - transformatie logica in ``` src/transform_service.py ```
    - harvestering logica in ``` src/harvest_service.py ``` en ``` src/oai_harvester.py ``` of ``` src/adlib_harvester.py ```

## Context
- Dataset op de Linked Data Voorziening [rijkscollectie-rce](https://linkeddata.cultureelerfgoed.nl/rce/rijkscollectie-rce)
- Mapping op basis van CN model, wat een minder stricte versie van het NDE schema.org applicatieprofiel is.  
- Rechten voor afbeeldingen op Memorix basis van AdlibXML
- Limieten Github Actions en Triply API.

## Sequentiediagram
```mermaid
sequenceDiagram;
    participant Axiell Collections 
    participant ETL
    participant Linked Data Voorziening
    participant NDE Datasetregister
    participant Collectie Nederland

    ETL->>Axiell Collections:ophalen brondata
    Axiell Collections-->>ETL:
    ETL->>ETL:transformatie naar Linked Data
    ETL->>ETL:validatie 
    ETL->>Linked Data Voorziening:publicatie
    ETL->>Linked Data Voorziening:sync
    loop Na publicatie in datacatalog
        NDE Datasetregister->>Linked Data Voorziening: Ophalen datacatalog RCE
        Linked Data Voorziening-->>NDE Datasetregister:
        Collectie Nederland->>NDE Datasetregister: Ophalen CN.nl datasets 
        NDE Datasetregister-->>Collectie Nederland: 
        Collectie Nederland->>Linked Data Voorziening:
        Linked Data Voorziening-->>Collectie Nederland:
    end
```

## Uitvoeren tests
``` ./run-test-windows.sh ``` of ``` ./run-test-linux.sh ```

## Lokaal draaien pipeline
``` ./run-windows.sh ``` of ``` ./run-linux.sh ```

## Implementatiemodel
```mermaid
---
  config:
    theme: forest
    nodeSpacing: 50
    rankSpacing: 250
---
flowchart TD
classDef Literal fill:#ffffff,stroke:#000000,color:;
classDef Literal_URI fill:#ffffff,stroke:#000000,color:;
classDef Multi fill:#cccccc,stroke:#000000,color:;
classDef Multi_URI fill:#cccccc,stroke:#000000,color:;
0(["schema:Place"]) -->|schema:sameAs| 1["xsd:anyURI"]:::Literal
0(["schema:Place"]) -->|schema:name| 2["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:genre| 4(["schema:DefinedTerm"])
3(["schema:CreativeWork"]) -->|schema:url| 5["xsd:anyURI"]:::Literal
6(["schema:PropertyValue"]) -->|schema:propertyID| 7["xsd:anyURI"]:::Literal
3(["schema:CreativeWork"]) -->|schema:name| 8["xsd:string"]:::Literal
4(["schema:DefinedTerm"]) -->|schema:name| 9["xsd:string"]:::Literal
6(["schema:PropertyValue"]) -->|schema:value| 10["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:alternateName| 11["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:additionalType| 4(["schema:DefinedTerm"])
3(["schema:CreativeWork"]) -->|schema:copyrightHolder| 12(["schema:Person"])
4(["schema:DefinedTerm"]) -->|schema:sameAs| 13["xsd:anyURI"]:::Literal
3(["schema:CreativeWork"]) -->|schema:material| 14(["schema:Product"])
3(["schema:CreativeWork"]) -->|schema:creator| 12(["schema:Person"])
15(["schema:MediaObject"]) -->|schema:encodesCreativeWork| 3(["schema:CreativeWork"])
3(["schema:CreativeWork"]) -->|schema:associatedMedia| 15(["schema:MediaObject"])
3(["schema:CreativeWork"]) -->|schema:license| 16["xsd:string"]:::Literal
17(["schema:QuantitativeValue"]) -->|schema:value| 18["xsd:string"]:::Literal
15(["schema:MediaObject"]) -->|schema:license| 19["xsd:anyURI"]:::Literal
6(["schema:PropertyValue"]) -->|schema:description| 20["xsd:string"]:::Literal
15(["schema:MediaObject"]) -->|schema:thumbnailUrl| 21["xsd:anyURI"]:::Literal
3(["schema:CreativeWork"]) -->|schema:sdPublisher| 22["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:size| 17(["schema:QuantitativeValue"])
15(["schema:MediaObject"]) -->|schema:contentUrl| 23["xsd:anyURI"]:::Literal
3(["schema:CreativeWork"]) -->|schema:description| 24["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:identifier| 6(["schema:PropertyValue"])
25(["schema:Occupation"]) -->|schema:name| 26["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:size| 27["xsd:string"]:::Literal
17(["schema:QuantitativeValue"]) -->|schema:valueReference| 28["xsd:string"]:::Literal
12(["schema:Person"]) -->|schema:name| 29["xsd:string"]:::Literal
12(["schema:Person"]) -->|schema:hasOccupation| 25(["schema:Occupation"])
14(["schema:Product"]) -->|schema:name| 30["xsd:string"]:::Literal
25(["schema:Occupation"]) -->|schema:sameAs| 31["xsd:anyURI"]:::Literal
17(["schema:QuantitativeValue"]) -->|schema:unitText| 32["xsd:string"]:::Literal
12(["schema:Person"]) -->|schema:birthDate| 33["xsd:string"]:::Literal
12(["schema:Person"]) -->|schema:sameAs| 34["xsd:anyURI"]:::Literal
14(["schema:Product"]) -->|schema:sameAs| 35["xsd:anyURI"]:::Literal
12(["schema:Person"]) -->|schema:deathDate| 36["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:isPartOf| 37["xsd:anyURI"]:::Literal
3(["schema:CreativeWork"]) -->|schema:temporal| 38["xsd:string"]:::Literal
3(["schema:CreativeWork"]) -->|schema:locationCreated| 0(["schema:Place"])
```

# Tools

In de directory ``` tools ``` staan twee python files, namelijk ``` tools > criteria.py ``` en ``` tools > generate-datashape.py ```. ``` tools > criteria.py ``` kan gebruikt worden om een implementatiemodel te genereren op basis van getransformeerde data. ``` tools > generate-datashape.py ``` kan gebruikt worden om een .shex datashape te genereren op basis van getransformeerde data. 