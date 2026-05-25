from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

_SPACY_AVAILABLE = False
_nlp = None

try:
    import spacy as _spacy_mod

    _SPACY_AVAILABLE = True
except ImportError:
    _SPACY_AVAILABLE = False

_ENTITY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"), "person"),
    (re.compile(r"\b[A-Z][a-z]+ (?:\w\.)?[A-Z][a-z]+(?:\s+(?:Jr|Sr|II|III|IV))?\b"), "person"),
    (
        re.compile(
            r"\b(?:Menteri|Presiden|Gubernur|Walikota|Bupati|Direktur|CEO|"
            r"Mantan|Anggota|Ketua|Wakil)\s+(?:[A-Z][a-z]+\s)*[A-Z][a-z]+\b"
        ),
        "person",
    ),
    (
        re.compile(
            r"\b[A-Z][a-zA-Z]+ (?:Corp|Inc|Ltd|LLC|PLC|Group|Bank|"
            r"University|Institute|Foundation|Perusahaan|PT\b|CV\b)"
        ),
        "organization",
    ),
    (re.compile(r"\b(?:PT\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b"), "organization"),
    (
        re.compile(
            r"\b(?:Pemerintah|Kementerian|KPU|DPR|DPRD|MUI|BNPT|"
            r"Bappenas|BPS|IDX|OJK|BI|IMF|World Bank|ASEAN|UN|WHO|"
            r"NATO|EU|G20|OECD)\b"
        ),
        "organization",
    ),
    (
        re.compile(
            r"\b(?:Indonesia|Jakarta|Bandung|Surabaya|Medan|Yogyakarta|"
            r"Makassar|Denpasar|Palembang|Semarang|Bali|Aceh|Papua|"
            r"Kalimantan|Sumatera|Sulawesi|Maluku|NTB|NTT|Batam|"
            r"Bogor|Depok|Tangerang|Bekasi|Malang|Solo|Samarinda|"
            r"Pontianak|Manado|Ambon|Jayapura|Mataram|Kupang|Pekanbaru|"
            r"Padang|Palangkaraya|Banjarmasin|Kendari|Palu|Gorontalo|"
            r"Serang|Bandar Lampung|Jambi|Bengkulu|Tanjung Pinang|"
            r"New York|London|Tokyo|Beijing|Singapore|Kuala Lumpur|"
            r"Jakarta|Washington|Seoul|Bangkok|Manila|Dubai|Moscow|"
            r"Paris|Berlin|Canberra|Riyadh|Ankara|New Delhi|Islamabad)\b"
        ),
        "location",
    ),
    (
        re.compile(
            r"\b(?:Danau|Gunung|Sungai|Selat|Teluk|Pulau|Kota|Kabupaten|"
            r"Provinsi|Kecamatan|Desa|Kelurahan)\s+[A-Z][a-z]+\b"
        ),
        "location",
    ),
    (
        re.compile(
            r"\b(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|"
            r"September|Oktober|November|Desember)\s+\d{4}\b"
        ),
        "date",
    ),
    (
        re.compile(
            r"\b\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|"
            r"Juli|Agustus|September|Oktober|November|Desember)\s+\d{4}\b"
        ),
        "date",
    ),
    (re.compile(r"\b\d{4}\b"), "year"),
    (
        re.compile(
            r"\b(?:Gempa|Banjir|Longsor|Tsunami|Kebakaran|Kecelakaan|"
            r"Demonstrasi|Pemilu|Pilpres|Pilkada|Konferensi|KTT|"
            r"Olimpiade|Piala Dunia|MotoGP|F1)\b"
        ),
        "event",
    ),
]

_KNOWN_LOCATIONS: set[str] = {
    "indonesia",
    "jakarta",
    "bandung",
    "surabaya",
    "medan",
    "yogyakarta",
    "makassar",
    "denpasar",
    "palembang",
    "semarang",
    "bali",
    "aceh",
    "papua",
    "kalimantan",
    "sumatera",
    "sulawesi",
    "maluku",
    "ntb",
    "ntt",
    "batam",
    "bogor",
    "depok",
    "tangerang",
    "bekasi",
    "malang",
    "solo",
    "samarinda",
    "pontianak",
    "manado",
    "ambon",
    "jayapura",
    "mataram",
    "kupang",
    "pekanbaru",
    "padang",
    "palangkaraya",
    "banjarmasin",
    "kendari",
    "palu",
    "gorontalo",
    "serang",
    "bandar lampung",
    "jambi",
    "bengkulu",
    "tanjung pinang",
    "new york",
    "london",
    "tokyo",
    "beijing",
    "singapore",
    "kuala lumpur",
    "washington",
    "seoul",
    "bangkok",
    "manila",
    "dubai",
    "moscow",
    "paris",
    "berlin",
    "canberra",
    "riyadh",
    "ankara",
    "new delhi",
    "islamabad",
}


def _init_spacy() -> Any:
    global _nlp
    if not _SPACY_AVAILABLE:
        return None
    if _nlp is not None:
        return _nlp
    models = ["id_core_news_sm", "en_core_web_sm", "xx_ent_wiki_sm"]
    for model in models:
        try:
            _nlp = _spacy_mod.load(model)
            logger.info("[NER] spaCy loaded: %s", model)
            return _nlp
        except OSError:
            continue
    logger.warning("[NER] no spaCy model found, falling back to heuristics")
    return None


def get_spacy_model() -> Any:
    return _init_spacy()


async def extract_entities_spacy(text: str, topic: str) -> list[dict[str, str]]:
    nlp = get_spacy_model()
    if nlp is None:
        return []

    doc = nlp(text[:50000])
    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    label_map = {
        "PERSON": "person",
        "PER": "person",
        "ORG": "organization",
        "GPE": "location",
        "LOC": "location",
        "EVENT": "event",
        "DATE": "date",
        "TIME": "date",
    }

    for ent in doc.ents:
        ent_type = label_map.get(ent.label_, "concept")
        name = ent.text.strip()
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        start = max(0, ent.start_char - 60)
        end = min(len(text), ent.end_char + 60)
        context = text[start:end].replace("\n", " ")
        entities.append(
            {
                "name": name,
                "type": ent_type,
                "description": f"Entitas {ent_type} ditemukan di artikel tentang '{topic}'",
                "context": context,
            }
        )

    return entities


async def extract_entities_heuristics(text: str, topic: str) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    for pattern, ent_type in _ENTITY_PATTERNS:
        for match in pattern.finditer(text):
            name = match.group().strip()
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            start = max(0, match.start() - 60)
            end = min(len(text), match.end() + 60)
            context = text[start:end].replace("\n", " ")
            entities.append(
                {
                    "name": name,
                    "type": ent_type,
                    "description": f"Entitas {ent_type} ditemukan di artikel tentang '{topic}'",
                    "context": context,
                }
            )

    words = re.findall(r"[A-Z][a-z]+", text)
    for word in words:
        w = word.lower()
        if w in _KNOWN_LOCATIONS and w not in seen:
            seen.add(w)
            entities.append(
                {
                    "name": word,
                    "type": "location",
                    "description": f"Lokasi ditemukan di artikel tentang '{topic}'",
                    "context": "",
                }
            )

    return entities


async def extract_entities(
    text: str,
    topic: str = "",
    use_spacy: bool = True,
) -> list[dict[str, str]]:
    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    if use_spacy and _SPACY_AVAILABLE:
        spacy_entities = await extract_entities_spacy(text, topic)
        for ent in spacy_entities:
            if ent["name"].lower() not in seen:
                seen.add(ent["name"].lower())
                entities.append(ent)

    heuristics_entities = await extract_entities_heuristics(text, topic)
    for ent in heuristics_entities:
        if ent["name"].lower() not in seen:
            seen.add(ent["name"].lower())
            entities.append(ent)

    if topic and topic.lower() not in seen:
        entities.append(
            {
                "name": topic[:100],
                "type": "concept",
                "description": "Topik utama artikel",
                "context": text[:200],
            }
        )

    logger.info("[NER] extracted %d entities (spacy=%s)", len(entities), _SPACY_AVAILABLE)
    return entities
