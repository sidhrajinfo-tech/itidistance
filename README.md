# Gujarat ITI Distance Finder — Streamlit

Gujarat Government ITI finder with:
- 289 government ITI records from the supplied `MahitiPustika.pdf`
- address search using OpenStreetMap Nominatim
- map-click or manual latitude/longitude selection
- one or two starting locations
- approximate straight-line (Haversine) distance
- district/name/PIN filtering
- CSV export
- original Gujarati source-row images
- source PDF download

> **Important:** ITI coordinates are approximate locality/town points, not verified campus coordinates. Distances are air/straight-line estimates, not driving distances. This is a source snapshot, not a live admission/vacancy feed.

## 1. Run locally

Python 3.11 is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start:

```bash
streamlit run app.py
```

Open the URL shown by Streamlit, normally `http://localhost:8501`.

## 2. GitHub upload

Create a **public or private GitHub repository**, then upload the complete contents of this folder.

The important structure is:

```text
.
├── app.py
├── geo_utils.py
├── requirements.txt
├── runtime.txt
├── .gitignore
├── README.md
├── data/
│   ├── itis.json
│   ├── MahitiPustika.pdf
│   └── records/
└── tests/
    └── test_distances.py
```

Do **not** upload `.venv`, `__pycache__`, `.pytest_cache`, or local secrets.

## 3. Streamlit Community Cloud

1. Push the project to GitHub.
2. Open Streamlit Community Cloud.
3. Choose **Create app**.
4. Select your GitHub repository and branch.
5. Main file path: `app.py`.
6. Deploy.

No API key is required for the default small-use Nominatim setup.

### Recommended deployment secret / environment variable

For public deployment, set:

```text
GEOCODER_USER_AGENT=gujarat-iti-distance-finder/1.0 (+https://your-app-url)
```

If you use another compatible Nominatim provider:

```text
NOMINATIM_DOMAIN=your-domain.example
```

Optional debugging:

```text
SHOW_GEOCODER_ERRORS=1
```

Do not put secrets in `app.py` or commit them to GitHub.

## 4. Nominatim usage

Address search sends explicit user searches to Nominatim. The app:
- has no autocomplete
- caches repeated searches for 24 hours
- rate-limits requests to about one request per 1.1 seconds per app process
- does not bulk-geocode the ITI dataset

For a high-traffic public app, use a suitable hosted geocoder or your own service and review the provider's usage policy.

## 5. Tests

Run:

```bash
python -m unittest discover -s tests -v
```

The included tests validate Haversine calculations, coordinate validation, and the 289-record dataset.

## 6. Data / attribution

The ITI list and source PDF were supplied for this project.

Locality coordinates are attributed in the source data to GeoNames and/or OpenStreetMap. Map tiles are from OpenStreetMap contributors.

Official Gujarat ITI admission portal:
https://itiadmission.gujarat.gov.in/ITIForms/VacantSeats.aspx
