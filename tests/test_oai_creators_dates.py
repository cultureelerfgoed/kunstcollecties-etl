"""Makers per Production-groep, datering, vaste adressen en extra velden."""
import os
import sys
import xml.etree.ElementTree as ET

from rdflib import Graph
from rdflib.namespace import RDF, SDO

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import transform_service
import oai_to_schemaorg_mapping as mapping
import oai_xpaths as xpath

TWO_MAKERS = (
    '<record priref="500"><priref>500</priref><object_number>x1</object_number>'
    '<Production>'
    '<creator><name>Eerste, A.</name><priref>11</priref><birth.place>Delft</birth.place></creator>'
    '<creator.role><term>schilder</term></creator.role>'
    '</Production>'
    '<Production>'
    '<creator><name>Tweede, B.</name><priref>22</priref><birth.place>Gouda</birth.place>'
    '<Source><source.number>https://rkd.nl/artists/22</source.number></Source></creator>'
    '<creator.date_of_birth>1800-01-02</creator.date_of_birth><creator.date_of_death>1870</creator.date_of_death>'
    '<creator.role><term>graveur</term></creator.role>'
    '</Production>'
    '</record>'
)


def _graph(xml, **kwargs):
    graph = Graph()
    transform_service.parse_tree_to_graph(graph, ET.fromstring(xml), mapping, xpath, **kwargs)
    return graph


def _person(graph, name):
    for s in graph.subjects(RDF.type, SDO.Person):
        if any(str(o) == name for o in graph.objects(s, SDO.name)):
            return s


def _names(graph, subject, predicate):
    return {str(graph.value(o, SDO.name)) for o in graph.objects(subject, predicate)}


def test_all_creators_are_modelled():
    graph = _graph(TWO_MAKERS)
    assert len(list(graph.subjects(RDF.type, SDO.Person))) == 2
    assert len(list(graph.objects(None, SDO.creator))) == 2


def test_creator_data_stays_with_its_own_creator():
    graph = _graph(TWO_MAKERS)
    first, second = _person(graph, 'Eerste, A.'), _person(graph, 'Tweede, B.')
    # de eerste maker heeft zelf geen RKD-koppeling en geen datums: die horen bij de tweede
    assert list(graph.objects(first, SDO.sameAs)) == []
    assert list(graph.objects(first, SDO.birthDate)) == []
    assert list(graph.objects(first, SDO.deathDate)) == []
    assert len(list(graph.objects(second, SDO.sameAs))) == 1
    assert [str(o) for o in graph.objects(second, SDO.birthDate)] == ['1800-01-02']
    assert _names(graph, first, SDO.hasOccupation) == {'schilder'}
    assert _names(graph, second, SDO.hasOccupation) == {'graveur'}
    assert _names(graph, first, SDO.birthPlace) == {'Delft'}
    assert _names(graph, second, SDO.birthPlace) == {'Gouda'}


def test_no_creator_gives_no_person():
    graph = _graph('<record priref="9"><priref>9</priref><object_number>x</object_number><Production></Production></record>')
    assert list(graph.subjects(RDF.type, SDO.Person)) == []
    assert list(graph.objects(None, SDO.creator)) == []


def test_graph_is_identical_between_runs():
    # geen uuid4 meer: twee runs over dezelfde brondata geven dezelfde triples
    xml = ('<record priref="7"><priref>7</priref><object_number>n1</object_number>'
           '<Rights><rights.holder>Houder</rights.holder></Rights>'
           '<Dimension><dimension.type>hoogte</dimension.type><dimension.unit>cm</dimension.unit><dimension.value>5</dimension.value></Dimension>'
           '<Production><creator><name>Zonder nummer</name></creator></Production></record>')
    assert set(_graph(xml)) == set(_graph(xml))


def test_creation_dates():
    cd = transform_service.creation_dates
    assert cd('1948', '1948') == {'dateCreated': '1948', 'temporal': '1948'}
    assert cd('1888', '1948') == {'dateCreated': None, 'temporal': '1888/1948'}
    assert cd(None, '1948') == {'dateCreated': '1948', 'temporal': '1948'}
    assert cd('250', '550') == {'dateCreated': None, 'temporal': '0250/0550'}
    assert cd('ca. 1650', '1700') == {'dateCreated': None, 'temporal': 'ca. 1650/1700'}
    assert cd(None, None) == {'dateCreated': None, 'temporal': None}


def test_period_is_kept_in_graph():
    graph = _graph('<record priref="1"><priref>1</priref><Production_date><production.date.start>1888</production.date.start>'
                   '<production.date.end>1948</production.date.end></Production_date></record>')
    assert [str(o) for o in graph.objects(None, SDO.temporal)] == ['1888/1948']
    assert list(graph.objects(None, SDO.dateCreated)) == []


def test_sd_date_published_from_header_datestamp():
    graph = _graph('<record priref="1"><priref>1</priref></record>', datestamp='2021-07-15T04:55:40Z')
    assert [str(o) for o in graph.objects(None, SDO.sdDatePublished)] == ['2021-07-15']


def test_alternative_numbers_themes_and_inscriptions():
    graph = _graph('<record priref="1"><priref>1</priref><object_number>a</object_number>'
                   '<Alternative_number><alternative_number>L12</alternative_number><alternative_number.type>inventarisnummer</alternative_number.type></Alternative_number>'
                   '<Thema><content.motif.general>Koloniaal verleden</content.motif.general></Thema>'
                   '<Thema_wat><theme.subject.what>tabak</theme.subject.what></Thema_wat>'
                   '<Inscription><inscription.description>Sign. linksonder</inscription.description></Inscription></record>')
    assert len(list(graph.objects(None, SDO.identifier))) == 2   # object_number + alternatief nummer
    assert len(list(graph.objects(None, SDO.about))) == 2
    assert [str(o) for o in graph.objects(None, SDO.text)] == ['Sign. linksonder']


def test_namespaced_records_like_the_oai_feed():
    xml = ('<record xmlns="http://www.openarchives.org/OAI/2.0/" priref="3"><priref>3</priref>'
           '<Production><creator><name>A</name><priref>1</priref></creator></Production>'
           '<Production><creator><name>B</name><priref>2</priref></creator></Production></record>')
    graph = _graph(xml, ns_pfx='ns0', ns='http://www.openarchives.org/OAI/2.0/')
    assert len(list(graph.subjects(RDF.type, SDO.Person))) == 2


def test_technique_becomes_additional_type_with_uri():
    graph = _graph('<record priref="1"><priref>1</priref>'
                   '<Technique><technique><term>kopergravure</term><Source><source.number>http://vocab.getty.edu/aat/300053149</source.number></Source></technique></Technique>'
                   '<Technique><technique><term>bekleed</term></technique></Technique></record>')
    types = list(graph.objects(None, SDO.additionalType))
    assert len(types) == 2
    assert {str(graph.value(t, SDO.name)) for t in types} == {'kopergravure', 'bekleed'}
    assert [str(o) for o in graph.objects(None, SDO.sameAs)] == ['http://vocab.getty.edu/aat/300053149']


def test_urls_are_iris_and_safe():
    from rdflib import URIRef
    graph = _graph('<record priref="1"><priref>1</priref><object_number>DV412 A-D</object_number>'
                   '<Rights><rights.assigned><value>YES</value></rights.assigned></Rights>'
                   '<Reproduction><reproduction.reference>37d77ebb-3c6c-d691-884e-75cdf50125f7</reproduction.reference></Reproduction></record>')
    for predicate in (SDO.url, SDO.contentUrl, SDO.thumbnailUrl, SDO.license):
        values = list(graph.objects(None, predicate))
        assert values, predicate
        assert all(isinstance(v, URIRef) for v in values), predicate
    assert ' ' not in str(list(graph.objects(None, SDO.url))[0])
    assert 'DV412%20A-D' in str(list(graph.objects(None, SDO.url))[0])


def test_term_names_are_language_tagged():
    graph = _graph('<record priref="1"><priref>1</priref>'
                   '<Material><material><term>papier</term></material></Material>'
                   '<Technique><technique><term>ets</term></technique></Technique>'
                   '<Production><production.place><term>Delft</term></production.place><creator><name>X</name><birth.place>Gouda</birth.place></creator>'
                   '<creator.role><term>graveur</term></creator.role></Production>'
                   '<Thema_wat><theme.subject.what>tabak</theme.subject.what></Thema_wat></record>')
    terms = [s for s in graph.subjects(RDF.type, SDO.DefinedTerm)]
    assert len(terms) >= 6
    for term in terms:
        names = list(graph.objects(term, SDO.name))
        assert len(names) == 1 and names[0].language == 'nl', term


def test_person_names_are_language_tagged():
    graph = _graph(TWO_MAKERS.replace('</record>', '<Rights><rights.holder>Houder, H.</rights.holder></Rights></record>'))
    persons = list(graph.subjects(RDF.type, SDO.Person))
    assert len(persons) == 3
    for person in persons:
        names = list(graph.objects(person, SDO.name))
        assert len(names) == 1 and names[0].language == 'nl'
