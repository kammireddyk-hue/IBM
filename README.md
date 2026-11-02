# Institutional Effectiveness Dataset

## Project structure

The project currently contains ten annual institutional effectiveness and
accreditation packet datasets. Each dataset is provided as a PDF at the project
root; there are no extracted CSV, JSON, or spreadsheet files in the current
project.

```text
IBM project/
├── README.md
├── Institution_01_Northridge_State_University_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_02_Harborview_Community_College_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_03_Ashwood_Liberal_Arts_College_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_04_Midlands_Technical_Polytechnic_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_05_Riverbend_HBCU_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_06_Summit_Online_University_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_07_St_Helena_Faith_Affiliated_University_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_08_Metro_City_Public_University_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
├── Institution_09_Prairie_Regional_State_College_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
└── Institution_10_Bayshore_Health_Sciences_University_Annual_Institutional_Effectiveness_Accreditation_Packet.pdf
```

## Dataset inventory

| Dataset ID | Institution | File format |
|---|---|---|
| 01 | Northridge State University | PDF |
| 02 | Harborview Community College | PDF |
| 03 | Ashwood Liberal Arts College | PDF |
| 04 | Midlands Technical Polytechnic | PDF |
| 05 | Riverbend HBCU | PDF |
| 06 | Summit Online University | PDF |
| 07 | St. Helena Faith-Affiliated University | PDF |
| 08 | Metro City Public University | PDF |
| 09 | Prairie Regional State College | PDF |
| 10 | Bayshore Health Sciences University | PDF |

Each PDF is a 32-page synthetic annual institutional effectiveness and
accreditation packet. The packets cover institutional profiles and strategic
aims, enrollment and access, retention and graduation, equity, learning
outcomes, accreditation/CAP status, Title IV and compliance, and supporting
exhibits. They are source documents rather than structured table files.

## Project structure

The backend serves the web frontend and reads the PDFs in the project root
directly; it does not duplicate them into another data directory or assume a
normalized database schema.

```text
IBM project/
├── frontend/
│   ├── index.html        # Dashboard and document viewer
│   ├── styles.css        # Responsive visual design
│   └── app.js            # API integration and page interactions
├── backend/
│   ├── app/
│   │   ├── __init__.py   # Flask application factory and frontend route
│   │   ├── catalog.py    # PDF discovery and institution metadata
│   │   ├── pdf_service.py # Cached PDF text extraction and search
│   │   └── routes.py     # Versioned JSON and document endpoints
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   └── run.py
├── Institution_01_..._Packet.pdf
├── ...
├── Institution_10_..._Packet.pdf
└── README.md
```

## Flask backend

The Flask application serves the frontend from `/` and its assets from
`/assets/`, in addition to its JSON and PDF API:

```text
backend/
├── app/
│   ├── __init__.py
│   ├── catalog.py
│   ├── pdf_service.py
│   └── routes.py
├── tests/
│   └── test_api.py
├── requirements.txt
└── run.py
```

### Setup and run

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python backend\run.py
```

The development server runs at `http://127.0.0.1:5000`. The dataset directory
defaults to the project root and can be overridden with the Flask app setting
`DATASET_DIR`.

## Frontend

The responsive dashboard lives in `frontend/` and uses the Flask API on the
same origin. It includes an institution catalogue with name filtering, dataset
summary cards, full-packet PDF previews, and page-level text search across the
source documents. No separate frontend build or package installation is
required.

### API

All API routes are prefixed with `/api/v1`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check and discovered dataset count |
| `GET` | `/institutions` | List institution metadata and PDF filenames |
| `GET` | `/institutions/<id>` | Get one institution's metadata |
| `GET` | `/institutions/<id>/document` | Stream the source PDF |
| `GET` | `/search?q=<text>` | Search extracted PDF text and return matching page snippets |

Search accepts an optional `institution_id` to limit the search to one packet
and a `limit` from 1 to 100 (default 20). Example:

```text
GET /api/v1/search?q=retention&institution_id=01&limit=10
```

### Tests

Run the backend tests from the project root:

```powershell
python -m unittest discover -s backend\tests
```
