import logging
import traceback
from rdflib import Graph
import yaml
import json
import os
import re
import time
import gzip
import zlib
import urllib.request
import urllib.parse
import urllib.error
import xml.etree.ElementTree as ET
from typing import Optional, Tuple
import adlib_transformer
from rdflib.namespace import SDO, RDF

logger = logging.getLogger(__name__)

config = yaml.safe_load(open('config/config.yml', encoding='utf-8'))

# Verwijder ongeldige XML control chars (0x00-0x08, 0x0B, 0x0C, 0x0E-0x1F)
INVALID_XML_CHARS = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

# Repareer losse & die geen geldige entity openen, bijv. "A&B" -> "A&amp;B"
AMP_FIX = re.compile(r'&(?![A-Za-z#][A-Za-z0-9]*;)')

# Namespaces
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/"
}

HEADER = ".//oai:header"
IDENTIFIER = ".//oai:identifier"
DATESTAMP =  ".//oai:datestamp"

def clean_xml(s: str) -> str:
    s = INVALID_XML_CHARS.sub("", s)
    return s

def build_url(base: str, params: dict) -> str:
    base = base.rstrip("?")
    return f"{base}?{urllib.parse.urlencode(params)}"

def oai_params_first_call(verb: str, metadata_prefix: Optional[str], set_spec: Optional[str]) -> dict:
    params = {"verb": verb}
    if verb in ("ListRecords", "ListIdentifiers"):
        if metadata_prefix:
            params["metadataPrefix"] = metadata_prefix
        if set_spec:
            params["set"] = set_spec
    return params

# -----------------------------
# HTTP ophalen met retries en Retry-After
# -----------------------------
def safe_open_url(req: urllib.request.Request, retries: int = 3, backoff: float = 1.5) -> Tuple[int, str, bytes, dict]:
    """
    HTTP GET met retries en backoff.
    Respecteert Retry-After bij 429/503.
    Retourneert (status, content_type, raw_bytes, headers_dict).
    """
    last_err = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req) as resp:
                status = getattr(resp, "status", 200)
                headers = {k: v for k, v in resp.headers.items()}
                ct = headers.get("Content-Type", "")
                ce = headers.get("Content-Encoding", "")
                raw = resp.read()

                # Decompressie (pas ná read)
                if ce.lower() == "gzip":
                    raw = gzip.decompress(raw)
                elif ce.lower() in ("deflate", "zlib"):
                    try:
                        raw = zlib.decompress(raw)
                    except zlib.error:
                        raw = zlib.decompress(raw, -zlib.MAX_WBITS)

                logger.debug(f"HTTP {status} | Content-Type: {ct} | Content-Encoding: {ce or 'none'}")
                return status, ct, raw, headers

        except urllib.error.HTTPError as e:
            last_err = e
            status = e.code
            headers = {k: v for k, v in (e.headers or {}).items()}
            retry_after = headers.get("Retry-After")
            wait = backoff * (attempt + 1)
            if status in (429, 503) and retry_after:
                try:
                    wait = max(wait, float(retry_after))
                except ValueError:
                    # Als Retry-After geen seconds is: val terug op backoff
                    pass
            if attempt == retries - 1:
                raise
            logger.info(f"HTTPError {status}: {e.reason}. Wachten {wait:.1f}s en opnieuw proberen...")
            time.sleep(wait)

        except Exception as e:
            last_err = e
            if attempt == retries - 1:
                raise
            wait = backoff * (attempt + 1)
            logger.warning(f"Netwerkfout: {e}. Wachten {wait:.1f}s en opnieuw proberen...")
            time.sleep(wait)

    if last_err:
        raise last_err

def fetch_and_parse(url: str, headers: dict, 
                    retries: int, backoff: float) -> Tuple[ET.Element, str]:
    """
    Haal op -> decodeer -> schoon -> parse.
    Bij parsefout: één reparatiepoging met AMP_FIX. Dump ruwe response en stop als het dan nog faalt.
    Retourneert (root_element, text_na_clean/repair).
    """
    req = urllib.request.Request(url, headers=headers)
    status, ct, raw, _ = safe_open_url(req, retries=retries, backoff=backoff)

    # Decodeer en schoon
    text = raw.decode("utf-8", errors="replace")
    text = clean_xml(text)

    # Eerste parsepoging
    try:
        root = ET.fromstring(text)
        return root, text
    except ET.ParseError:
        pass

    # Reparatie: losse & omzetten naar &amp; en opnieuw proberen
    repaired = AMP_FIX.sub("&amp;", text)
    try:
        root = ET.fromstring(repaired)
        logger.debug("Waarschuwing: XML gerepareerd (losse & geëscapet).")
        return root, repaired
    except ET.ParseError as e2:
        # Dump voor diagnose
        raise e2

# -----------------------------
# OAI helpers
# -----------------------------
def wrapper_open_tag(verb: str) -> str:
    if verb == "ListRecords":
        return "<OAI-PMH>\n<ListRecords>\n"
    if verb == "ListIdentifiers":
        return "<OAI-PMH>\n<ListIdentifiers>\n"
    return "<OAI-PMH>\n"

def wrapper_close_tag(verb: str) -> str:
    if verb == "ListRecords":
        return "</ListRecords>\n</OAI-PMH>\n"
    if verb == "ListIdentifiers":
        return "</ListIdentifiers>\n</OAI-PMH>\n"
    return "</OAI-PMH>\n"

def ensure_open_wrapper(out_path: str, verb: str):
    """
    Zorg dat begin-tags aanwezig zijn en strip closing tags bij hervatten.
    """
    open_tag = wrapper_open_tag(verb)
    close_tag = wrapper_close_tag(verb)

    if not os.path.exists(out_path) or os.path.getsize(out_path) == 0:
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(open_tag)
        return

    tail_len = min(8192, os.path.getsize(out_path))
    with open(out_path, "rb") as f:
        f.seek(-tail_len, os.SEEK_END)
        tail = f.read().decode("utf-8", errors="ignore")

    idx = tail.rfind(close_tag)
    if idx != -1:
        with open(out_path, "rb+") as f:
            f.seek(-tail_len + idx, os.SEEK_END)
            f.truncate()
        logger.info("Closing tags verwijderd om te hervatten.")

def write_close_wrapper(out_path: str, verb: str):
    with open(out_path, "a", encoding="utf-8") as out:
        out.write(wrapper_close_tag(verb))

def oai_params_first_call(verb: str, metadata_prefix: Optional[str], set_spec: Optional[str]) -> dict:
    params = {"verb": verb}
    if verb in ("ListRecords", "ListIdentifiers"):
        if metadata_prefix:
            params["metadataPrefix"] = metadata_prefix
        if set_spec:
            params["set"] = set_spec
    return params

# -----------------------------
# State (hervatten)
# -----------------------------
def state_path_for(out_path: str) -> str:
    return out_path + ".state.json"

def save_state(path: str, state: dict):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def load_state(path: str) -> Optional[dict]:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def remove_state(path: str):
    if os.path.exists(path):
        os.remove(path)

# -----------------------------
# Preflight: Identify + ListMetadataFormats
# -----------------------------
def preflight_identify(base_url: str, headers: dict, retries: int, backoff: float):
    url = build_url(base_url, {"verb": "Identify"})
    logger.info(f"Preflight Identify: {url}")
    root, text = fetch_and_parse(url, headers, retries, backoff)
    text = clean_xml(text)
    root = ET.fromstring(text)

    repo = root.find(".//oai:Identify/oai:repositoryName", NS)
    base = root.find(".//oai:Identify/oai:baseURL", NS)
    gran = root.find(".//oai:Identify/oai:granularity", NS)
    earliest = root.find(".//oai:Identify/oai:earliestDatestamp", NS)

    logger.info(f"Identify: repositoryName={repo.text if repo is not None else '?'} | "
               f"baseURL={base.text if base is not None else '?'} | "
               f"granularity={gran.text if gran is not None else '?'} | "
               f"earliestDatestamp={earliest.text if earliest is not None else '?'}")

def preflight_check_metadata_prefix(base_url: str, headers: dict, 
                                    desired_prefix: str, retries: int, backoff: float):
    url = build_url(base_url, {"verb": "ListMetadataFormats"})
    logger.info(f"Preflight ListMetadataFormats: {url}")
    root, text = fetch_and_parse(url, headers, retries, backoff)
    text = clean_xml(text)
    root = ET.fromstring(text)

    prefixes = [el.text.strip() for el in root.findall(".//oai:metadataPrefix", NS) if el.text]
    logger.info(f"Beschikbare metadataPrefix: {', '.join(prefixes) if prefixes else '(geen)'}")
    if desired_prefix not in prefixes:
        raise SystemExit(f"metadataPrefix '{desired_prefix}' niet beschikbaar. Kies een van: {', '.join(prefixes)}")

# -----------------------------
# Harvest met rotatie, limiet, CSV/JSONL
# -----------------------------
def harvest(target_graph: Graph, base_url: str, verb: str, metadata_prefix: Optional[str], set_spec: Optional[str],
            sleep_between: float = 0.3, retries: int = 3, backoff: float = 1.5,
            max_items: Optional[int] = None, start_from: Optional[int] = 0) -> Graph:

    headers = {
        "User-Agent": "OAI-PMH harvester (Python stdlib)",
        "Accept": "application/xml, text/xml;q=0.9, */*;q=0.1",
        "Accept-Encoding": "identity, gzip, deflate",
    }

    # Preflight
    try:
        preflight_identify(base_url, headers, retries, backoff)
    except Exception as e:
        logger.warning(f"Failed to identify endpoint: {e}")

    if verb in ("ListRecords", "ListIdentifiers") and metadata_prefix:
        preflight_check_metadata_prefix(base_url, headers, metadata_prefix, retries, backoff)

    # State init
    num_items = 0
    file_index = 1
    params = oai_params_first_call(verb, metadata_prefix, set_spec)
    state = {
        "base_url": base_url,
        "verb": verb,
        "metadataPrefix": metadata_prefix,
        "set": set_spec,
        "file_index": file_index,
        "num_items": 0,
        "resumptionToken": "",
    }

    page = int(start_from / 10)
    try:
        while True:
            if max_items is not None and num_items >= max_items:
                logger.info(f"Max-items bereikt ({max_items}). Stoppen.")
                break

            page += 1
            url = build_url(base_url, params)

            root, text = fetch_and_parse(url, headers, retries, backoff)
            text = clean_xml(text)
            root = ET.fromstring(text)

            # Selecteer items
            if verb == "ListRecords":
                elements = root.findall(".//oai:metadata/oai:record", NS)
 
            for element in elements:
                if max_items is not None and num_items >= max_items:
                    break
                
                try:
                    adlib_transformer.parse_tree_to_graph(target_graph, element, 'ns0', 'http://www.openarchives.org/OAI/2.0/')
                except (AssertionError, TypeError, Exception) as te:
                    logger.warning('Error during transformation: %s', str(traceback.format_exception(te)))

                num_items += 1

            # Volgende pagina
            rt_el = root.find(".//oai:resumptionToken", NS)
            rt = rt_el.text.strip() if rt_el is not None and rt_el.text else ""
            logger.info(f"Pagina {page}, {num_items} items total. ResumptionToken {'aanwezig' if rt else 'ontbreekt'}.")

            state.update({
                "file_index": file_index,
                "num_items": num_items,
                "resumptionToken": rt,
            })

            if not rt:
                break

            params = {"verb": verb, "resumptionToken": rt}
            time.sleep(sleep_between)

        
        return target_graph
    except Exception as e:
        raise e

def main():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    print('Starting harvest test.')
    rgraph = Graph()
    print('Calling harvester..')
    rgraph = harvest(rgraph, 
                        base_url=config['SRC_URI'], 
                        verb='ListRecords', 
                        metadata_prefix='rs', 
                        set_spec=config['SRC_DB'],
                        start_from=200,
                        max_items=100)
    records = len(list(rgraph.subjects(RDF.type, SDO.ArchiveComponent)))
    rgraph.serialize(format='json-ld', 
                            destination='TEST-oai-kc.json-ld',  
                            auto_compact=True)
    logger.info(f'got {records} records ')
    assert records == 100

if __name__ == "__main__":
    main()