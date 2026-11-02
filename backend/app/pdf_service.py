from functools import lru_cache
from pathlib import Path
import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError


class DocumentReadError(Exception):
    pass


@lru_cache(maxsize=10)
def _read_pages(path, modified_ns, size):
    del modified_ns, size
    try:
        with open(path, "rb") as source:
            reader = PdfReader(source)
            if reader.is_encrypted:
                raise DocumentReadError("The PDF is encrypted and cannot be searched.")
            return tuple(page.extract_text() or "" for page in reader.pages)
    except DocumentReadError:
        raise
    except (OSError, PdfReadError, ValueError) as error:
        raise DocumentReadError(f"Could not extract text from {Path(path).name}.") from error


def read_pages(path):
    path = Path(path)
    try:
        stat = path.stat()
    except OSError as error:
        raise DocumentReadError(f"Could not access {path.name}.") from error
    return _read_pages(str(path), stat.st_mtime_ns, stat.st_size)


def search_pages(path, query, limit):
    matches = []
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    for page_number, text in enumerate(read_pages(path), start=1):
        match = pattern.search(text)
        if not match:
            continue
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        snippet = re.sub(r"\s+", " ", text[start:end]).strip()
        matches.append({"page": page_number, "snippet": snippet})
        if len(matches) == limit:
            break
    return matches
