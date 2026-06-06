"""
Pure-Python JPEG/PNG Metadaten-Analyse und -Entfernung.
Keine externen Bibliotheken nötig — nur die Python-Standardbibliothek.
"""
import struct

# ── JPEG ──────────────────────────────────────────────────────────────────────

def _jpeg_segments(data: bytes):
    """Yields (marker_byte, payload) for each JPEG segment.
    After SOS, yields (0x00, remaining_bytes) for the entropy-coded image data.
    """
    if len(data) < 2 or data[:2] != b'\xff\xd8':
        return
    i = 2
    while i + 1 < len(data):
        if data[i] != 0xFF:
            break
        marker = data[i + 1]
        i += 2
        # Standalone markers (no length field)
        if marker == 0xD9 or 0xD0 <= marker <= 0xD7:
            yield marker, b''
            if marker == 0xD9:
                return
            continue
        if marker == 0xD8:
            yield marker, b''
            continue
        # Length-prefixed segment
        if i + 2 > len(data):
            break
        length = struct.unpack('>H', data[i:i + 2])[0]
        if length < 2 or i + length > len(data):
            break
        payload = data[i:i + length]
        i += length
        yield marker, payload
        # After SOS header, the entropy-coded data follows until EOI
        if marker == 0xDA:
            yield 0x00, data[i:]
            return


def _strip_jpeg(data: bytes) -> bytes:
    """Remove APP1 (EXIF/XMP) and APP13 (IPTC) segments from a JPEG."""
    out = bytearray(b'\xff\xd8')
    for marker, payload in _jpeg_segments(data):
        if marker == 0xE1:   # APP1  — EXIF / XMP
            continue
        if marker == 0xED:   # APP13 — IPTC / Photoshop
            continue
        if marker == 0xD8:   # SOI already written
            continue
        if marker == 0x00:   # Raw entropy-coded image data (after SOS)
            out += payload
            break
        if marker == 0xD9:
            out += b'\xff\xd9'
            break
        if 0xD0 <= marker <= 0xD7:
            out += bytes([0xFF, marker])
            continue
        out += bytes([0xFF, marker]) + payload
    return bytes(out)


def _read_jpeg_meta(data: bytes) -> dict:
    """Return a human-friendly summary of JPEG metadata."""
    info: dict = {}
    for marker, payload in _jpeg_segments(data):
        # APP1 with EXIF
        if marker == 0xE1 and len(payload) >= 8 and payload[2:8] == b'Exif\x00\x00':
            info['exif_bytes'] = len(payload)
            info.update(_parse_exif_ifd(payload[8:]))
        # APP13 IPTC
        if marker == 0xED:
            info['iptc'] = True
        # APP1 with XMP
        if marker == 0xE1 and len(payload) > 32 and b'xpacket' in payload[:50]:
            info['xmp'] = True
    return info


# ── Minimal EXIF / TIFF IFD parser ───────────────────────────────────────────

_TAGS = {
    0x010F: 'make',
    0x0110: 'model',
    0x0131: 'software',
    0x0132: 'datetime',
    0x013B: 'artist',
    0x8298: 'copyright',
    0x8825: 'gps_ifd',   # Presence → GPS data exists
}

_TYPE_BYTES = {1: 1, 2: 1, 3: 2, 4: 4, 5: 8,
               6: 1, 7: 1, 8: 2, 9: 4, 10: 8, 11: 4, 12: 8}


def _read_ifd(tiff: bytes, offset: int, e: str) -> dict:
    if offset + 2 > len(tiff):
        return {}
    try:
        count = struct.unpack(e + 'H', tiff[offset:offset + 2])[0]
    except struct.error:
        return {}
    entries: dict = {}
    pos = offset + 2
    for _ in range(min(count, 256)):
        if pos + 12 > len(tiff):
            break
        tag = struct.unpack(e + 'H', tiff[pos:pos + 2])[0]
        typ = struct.unpack(e + 'H', tiff[pos + 2:pos + 4])[0]
        cnt = struct.unpack(e + 'I', tiff[pos + 4:pos + 8])[0]
        raw = tiff[pos + 8:pos + 12]
        size = _TYPE_BYTES.get(typ, 1) * cnt
        if size <= 4:
            value_data = raw[:size]
        else:
            try:
                voff = struct.unpack(e + 'I', raw)[0]
                value_data = tiff[voff:voff + size]
            except (struct.error, IndexError):
                value_data = b''
        if typ == 2:
            try:
                entries[tag] = value_data.rstrip(b'\x00').decode('latin-1')
            except Exception:
                pass
        else:
            entries[tag] = value_data
        pos += 12
    return entries


def _parse_exif_ifd(tiff: bytes) -> dict:
    result: dict = {}
    if len(tiff) < 8:
        return result
    e = '<' if tiff[:2] == b'II' else '>' if tiff[:2] == b'MM' else None
    if e is None:
        return result
    try:
        if struct.unpack(e + 'H', tiff[2:4])[0] != 42:
            return result
        ifd0_off = struct.unpack(e + 'I', tiff[4:8])[0]
        entries  = _read_ifd(tiff, ifd0_off, e)
    except Exception:
        return result
    for tag, val in entries.items():
        if tag == 0x8825:
            result['gps'] = True
        elif tag in _TAGS and isinstance(val, str) and val.strip():
            result[_TAGS[tag]] = val.strip()
    return result


# ── PNG ───────────────────────────────────────────────────────────────────────

_PNG_SIG   = b'\x89PNG\r\n\x1a\n'
_PNG_STRIP = {b'tEXt', b'zTXt', b'iTXt', b'eXIf'}


def _strip_png(data: bytes) -> bytes:
    """Remove metadata chunks (tEXt, zTXt, iTXt, eXIf) from a PNG."""
    if data[:8] != _PNG_SIG:
        return data
    out = bytearray(_PNG_SIG)
    i = 8
    while i + 12 <= len(data):
        length = struct.unpack('>I', data[i:i + 4])[0]
        ctype  = data[i + 4:i + 8]
        end    = i + 12 + length
        if ctype not in _PNG_STRIP:
            out += data[i:end]
        i = end
    return bytes(out)


def _read_png_meta(data: bytes) -> dict:
    info: dict = {}
    if data[:8] != _PNG_SIG:
        return info
    found: list[str] = []
    i = 8
    while i + 12 <= len(data):
        length = struct.unpack('>I', data[i:i + 4])[0]
        ctype  = data[i + 4:i + 8]
        if ctype in _PNG_STRIP:
            found.append(ctype.decode('ascii', errors='?'))
        i += 12 + length
    if found:
        info['png_meta'] = found
    return info


# ── Public API ────────────────────────────────────────────────────────────────

SUPPORTED = ('.jpg', '.jpeg', '.png')


def detect_format(data: bytes) -> str:
    if data[:2] == b'\xff\xd8':
        return 'JPEG'
    if data[:8] == _PNG_SIG:
        return 'PNG'
    return 'unknown'


def read_meta(data: bytes) -> dict:
    """
    Liest Metadaten-Zusammenfassung aus JPEG oder PNG.

    Mögliche Keys im Rückgabe-Dict:
      format, gps, make, model, datetime, software, artist,
      copyright, iptc, xmp, png_meta, exif_bytes
    """
    fmt = detect_format(data)
    if fmt == 'JPEG':
        info = _read_jpeg_meta(data)
        info['format'] = 'JPEG'
        return info
    if fmt == 'PNG':
        info = _read_png_meta(data)
        info['format'] = 'PNG'
        return info
    return {'format': 'unknown'}


def strip(data: bytes) -> bytes | None:
    """
    Entfernt alle Metadaten aus JPEG oder PNG.
    Gibt None zurück wenn das Format nicht unterstützt wird.
    """
    fmt = detect_format(data)
    if fmt == 'JPEG':
        return _strip_jpeg(data)
    if fmt == 'PNG':
        return _strip_png(data)
    return None
