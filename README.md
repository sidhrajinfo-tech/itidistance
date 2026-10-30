# Gujarat ITI Distance Finder — Python + Streamlit

## Kya milega
- PDF ke 289 government ITIs ki searchable list.
- User apni location address search, map click, ya latitude/longitude se select kar sakta hai.
- Optional second location comparison; fixed Vastral/Patan addresses nahi hain.
- Gujarat map par ITI dots, selected origins se lines aur approximate air-distance labels.
- District/name/PIN filter, nearest-first sorting, CSV download, original Gujarati PDF rows.

**Accuracy:** 274 ITIs ke points approximate town/locality centres hain, verified campus coordinates nahi. 15 entries ki locations pending hain; list mein rehti hain aur distance blank rehta hai. Distances straight-line Haversine estimates hain, driving distance nahi. PDF extraction mein Gujarati text errors ho sakte hain; original row/image check karein. Data uploaded PDF ka snapshot hai, live admission list nahi.

## Local computer par chalayein
Python 3.11 ya 3.12 recommended.

```bash
python -m venv .venv
```
Windows:
```powershell
.venv\Scripts\Activate.ps1
```
macOS/Linux:
```bash
source .venv/bin/activate
```
Phir:
```bash
pip install -r requirements.txt
streamlit run app.py
```
Browser mein terminal ka Local URL kholein (normally http://localhost:8501).

## Streamlit Community Cloud par deploy
1. ZIP extract karein.
2. GitHub repository mein **app.py, geo_utils.py, requirements.txt aur poora data folder** upload karein. Sirf app.py upload karne se app nahi chalega.
3. Streamlit Community Cloud mein repository select karein, main file `app.py` rakhein. Agar files subfolder mein hain to uska full path dein.
4. Python 3.11/3.12 select karke deploy karein.
5. Sidebar mein address Search karein → sahi result select karein → Use location; ya map click/coordinates choose karein.
6. Do origins chahiye to 'Do locations compare karein' enable karein aur dono set karein.

## Address search aur map
Address searches use Nominatim; internet required. Search explicit button se hoti hai, autocomplete nahi. Results cache hote hain aur shared process mein requests serialized/rate-limited hain. Map tiles need browser internet; Leaflet assets also load through the map component.

Address service unavailable ho to manual coordinates ka option available hai. Search text geocoding provider ko bheja jata hai; origin selection app session memory mein rehti hai. CSV contains selected origin names/distances. No location database or login is included.

For a public deployment set an identifying `GEOCODER_USER_AGENT` environment variable including your app URL/contact. Optional `NOMINATIM_DOMAIN` can point to another compatible/self-hosted provider. Public Nominatim is for light usage; review https://operations.osmfoundation.org/policies/nominatim/ before public launch. Multiple app processes/replicas need a shared global limiter or suitable hosted geocoder. This package limits requests per process. No API key required for the default small-use setup.

## Files / editing locations
- `app.py`: complete Streamlit UI, map, address search, export.
- `geo_utils.py`: coordinate validation and Haversine calculations.
- `data/itis.json`: source ITI list and coordinates.
- `data/records/*.png`: original Gujarati table rows.
- `data/MahitiPustika.pdf`: original source.
- `tests/test_distances.py`: numerical/data checks.

To correct an ITI pin, edit `lat`, `lon`, `distanceEligible`, `locationNote`, `locationSource` in `data/itis.json`. Verify campus coordinates before claiming campus-accurate distances. Restart app/clear cache after editing data. Existing global disclaimer assumes original approximate dataset and should be updated only after verification.

## Tests
```bash
python -m unittest discover -s tests -v
```

## Attribution
Directory: user-provided MahitiPustika.pdf, printed pages 24–45 / physical PDF pages 34–55. Official admission portal: https://itiadmission.gujarat.gov.in/ITIForms/VacantSeats.aspx

Locality coordinates: GeoNames (CC BY 4.0, https://www.geonames.org/) and OpenStreetMap contributors (ODbL, https://www.openstreetmap.org/copyright). Individual sources are retained in JSON. Map tiles: © OpenStreetMap contributors.
