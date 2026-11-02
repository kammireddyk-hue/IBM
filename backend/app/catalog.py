import re
from pathlib import Path


DATASET_PATTERN = re.compile(
    r"^Institution_(?P<id>\d{2})_"
    r"(?P<name>.+)_Annual_Institutional_Effectiveness_"
    r"Accreditation_Packet\.pdf$",
    re.IGNORECASE,
)


def list_institutions(dataset_dir):
    institutions = []
    for path in sorted(Path(dataset_dir).glob("Institution_*.pdf")):
        match = DATASET_PATTERN.match(path.name)
        if not match:
            continue
        institutions.append(
            {
                "id": match.group("id"),
                "name": match.group("name").replace("_", " "),
                "filename": path.name,
                "format": "pdf",
                "pages": 32,
            }
        )
    return institutions


def find_institution(dataset_dir, institution_id):
    if not re.fullmatch(r"\d{2}", institution_id):
        return None
    return next(
        (
            institution
            for institution in list_institutions(dataset_dir)
            if institution["id"] == institution_id
        ),
        None,
    )


def document_path(dataset_dir, institution):
    return Path(dataset_dir) / institution["filename"]
