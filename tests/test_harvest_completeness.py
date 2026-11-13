"""De laatste chunk moet worden weggeschreven en een onvolledige oogst moet de run laten falen."""
import json
import os
import sys
import xml.etree.ElementTree as ET

import pytest

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import harvest_service
import oai_harvester

OAI = 'http://www.openarchives.org/OAI/2.0/'


def _page_text(first, count, token, announced):
    records = ''.join(
        f'<record><header><identifier>ruben_s:{i}</identifier><datestamp>2021-07-15T04:55:40Z</datestamp></header>'
        f'<metadata><record priref="{i}"><priref>{i}</priref><object_number>o{i}</object_number></record></metadata></record>'
        for i in range(first, first + count))
    rt = f'<resumptionToken completeListSize="{announced}">{token}</resumptionToken>'
    return f'<OAI-PMH xmlns="{OAI}"><ListRecords>{records}{rt}</ListRecords></OAI-PMH>'


def _run(monkeypatch, tmp_path, total, announced, page_size=5, chunk=10):
    texts = []
    for n, first in enumerate(range(1, total + 1, page_size)):
        count = min(page_size, total - first + 1)
        last = first + count > total
        texts.append(_page_text(first, count, '' if last else f't{n + 1}', announced))
    pages = iter(texts)

    def fake_fetch(*args, **kwargs):
        text = next(pages)
        return ET.fromstring(text), text

    monkeypatch.setattr(oai_harvester, 'fetch_and_parse', fake_fetch)
    monkeypatch.setattr(oai_harvester.time, 'sleep', lambda s: None)
    monkeypatch.setenv('CACHE_PATH', str(tmp_path) + os.sep)
    monkeypatch.setattr(sys, 'argv', ['harvest_service.py', '--chunks', str(chunk)])
    harvest_service.main()


def test_last_chunk_is_written(monkeypatch, tmp_path):
    # 25 records in chunks van 10 -> 10 + 10 + 5. De laatste 5 werden vroeger nooit weggeschreven.
    _run(monkeypatch, tmp_path, total=25, announced=25)
    assert sorted(p.name for p in tmp_path.glob('*.jsonld')) == ['kc-pt-0.jsonld', 'kc-pt-1.jsonld', 'kc-pt-2.jsonld']
    manifest = json.loads((tmp_path / 'manifest.json').read_text())
    assert manifest['complete'] is True
    assert manifest['seen'] == 25 and manifest['written'] == 25


def test_exact_multiple_of_chunk_size(monkeypatch, tmp_path):
    _run(monkeypatch, tmp_path, total=20, announced=20)
    assert len(list(tmp_path.glob('*.jsonld'))) == 2
    assert json.loads((tmp_path / 'manifest.json').read_text())['written'] == 20


def test_incomplete_harvest_fails_the_run(monkeypatch, tmp_path):
    # de bron kondigt 30 records aan maar levert er 25: de run moet falen zodat er niets gepubliceerd wordt
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, tmp_path, total=25, announced=30)
    assert exc.value.code == 1
    assert json.loads((tmp_path / 'manifest.json').read_text())['complete'] is False
