"""Gujarat government ITI finder — run with: streamlit run app.py"""
from pathlib import Path
from html import escape
import json
import os
import threading

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geo_utils import eligible, haversine_km, valid_point

ROOT = Path(__file__).resolve().parent
COLORS = ['#1976d2', '#923cb5']
st.set_page_config(page_title='Gujarat ITI Distance Finder', page_icon='📍', layout='wide')


@st.cache_data
def load_records():
    return json.loads((ROOT / 'data' / 'itis.json').read_text(encoding='utf-8'))


@st.cache_resource
def search_client():
    # One shared lock serializes requests across all sessions of this process.
    client = Nominatim(
        user_agent=os.getenv('GEOCODER_USER_AGENT', 'gujarat-iti-streamlit/1.0'),
        domain=os.getenv('NOMINATIM_DOMAIN', 'nominatim.openstreetmap.org'),
        timeout=12,
    )
    return RateLimiter(client.geocode, min_delay_seconds=1.1, max_retries=0, swallow_exceptions=False), threading.Lock()


@st.cache_data(ttl=86400, max_entries=500, show_spinner=False)
def find_address(query):
    # Explicit search button only; no autocomplete and no bulk geocoding.
    geocode, lock = search_client()
    with lock:
        results = geocode(query, exactly_one=False, limit=6, addressdetails=True)
    return [{'name': p.address, 'lat': p.latitude, 'lon': p.longitude} for p in (results or [])]


def set_origin(slot, name, lat, lon):
    if not valid_point(lat, lon):
        raise ValueError('Invalid coordinates')
    st.session_state[f'origin_{slot}'] = {'name': name, 'lat': float(lat), 'lon': float(lon)}


records = load_records()
st.title('📍 Gujarat Government ITI Distance Finder')
st.caption('Apni location chuniye • ITI list dekhiye • Distance compare kijiye')
st.warning('Distances approximate seedhi-line (air distance) hain, road distance nahi. '
           '274 ITI points town/locality centres hain; campus pins verified nahi hain. '
           '15 ITI ki location pending hai, par list mein sabhi 289 ITI hain.')

with st.sidebar:
    st.header('Starting location')
    compare = st.checkbox('Do locations compare karein', value=False)
    slot = st.radio('Kaunsi location set karni hai?', [0, 1] if compare else [0],
                    format_func=lambda i: f'Location {i+1}', horizontal=True)
    method = st.radio('Location kaise select karein?', ['Address search', 'Map par click', 'Latitude / longitude'])
    if method == 'Address search':
        with st.form('address_search'):
            query = st.text_input('Address / city / landmark', placeholder='Patan Bus Station, Gujarat, India')
            submitted = st.form_submit_button('Search location')
        if submitted:
            st.session_state['search_results'] = []
            if len(query.strip()) < 3:
                st.error('Kam se kam 3 characters likhein.')
            else:
                try:
                    with st.spinner('Location search ho rahi hai…'):
                        st.session_state['search_results'] = find_address(query.strip())
                    if not st.session_state['search_results']:
                        st.info('Result nahi mila. Map par click ya coordinates use karein.')
                except Exception:
                    st.error('Address service available nahi hai. Map click ya coordinates use karein.')
        matches = st.session_state.get('search_results', [])
        if matches:
            choice = st.selectbox('Sahi address chuniye', range(len(matches)), format_func=lambda i: matches[i]['name'])
            if st.button('Is location ko use karein'):
                p = matches[choice]
                set_origin(slot, p['name'], p['lat'], p['lon'])
    elif method == 'Latitude / longitude':
        previous = st.session_state.get(f'origin_{slot}', {'lat':23.0, 'lon':72.6})
        with st.form(f'coordinates_{slot}'):
            name = st.text_input('Location ka naam', value=f'My location {slot+1}')
            lat = st.number_input('Latitude', -90.0, 90.0, float(previous['lat']), format='%.6f')
            lon = st.number_input('Longitude', -180.0, 180.0, float(previous['lon']), format='%.6f')
            if st.form_submit_button('Set location'):
                set_origin(slot, name.strip() or f'Location {slot+1}', lat, lon)
    else:
        st.info('Neeche location picker map par click karein, phir Use selected pin dabayein.')
    for i in range(2 if compare else 1):
        p = st.session_state.get(f'origin_{i}')
        if p:
            st.markdown(f'**Location {i+1}:** {p["name"]}')
            st.caption(f'{p["lat"]:.6f}, {p["lon"]:.6f}')
            if st.button(f'Clear location {i+1}', key=f'clear_{i}'):
                del st.session_state[f'origin_{i}']
                st.rerun()
    st.divider()
    districts = st.multiselect('District filter (blank = all)', sorted({r['district'] for r in records}))
    keyword = st.text_input('ITI name / address / PIN search')
    show_lines = st.checkbox('Distance lines dikhayein', value=True)
    show_labels = st.checkbox('Har line par km label', value=False)
    st.caption('Address search: © OpenStreetMap contributors. Map click/coordinates work without address search.')

if method == 'Map par click':
    st.subheader(f'Location {slot+1} ka pin chuniye')
    p = st.session_state.get(f'origin_{slot}')
    picker = folium.Map(location=[p['lat'],p['lon']] if p else [22.7,71.5], zoom_start=8 if p else 6)
    if p:
        folium.Marker([p['lat'],p['lon']], tooltip=p['name']).add_to(picker)
    picked = st_folium(picker, height=330, use_container_width=True, key=f'picker_{slot}', returned_objects=['last_clicked'])
    click = (picked or {}).get('last_clicked')
    if click:
        st.caption(f'Selected: {click["lat"]:.6f}, {click["lng"]:.6f}')
        if st.button('Use selected pin'):
            set_origin(slot, f'Map pin {click["lat"]:.5f}, {click["lng"]:.5f}', click['lat'], click['lng'])
            st.rerun()

origins = [(i, st.session_state[f'origin_{i}']) for i in range(2 if compare else 1) if f'origin_{i}' in st.session_state]
if not origins:
    st.info('Sidebar se starting location chuniye. Abhi map aur saari ITI list dekh sakte hain.')
filtered = [r for r in records if (not districts or r['district'] in districts) and
            (not keyword.strip() or keyword.casefold().strip() in ' '.join(str(r.get(k,'')) for k in ['name','district','text','pin','extractedName']).casefold())]
columns = st.columns(3)
columns[0].metric('Total government ITIs', len(records))
columns[1].metric('Filtered ITIs', len(filtered))
columns[2].metric('Filtered locations available', sum(eligible(r) for r in filtered))
selected = st.selectbox('Ek ITI focus karein (blank = all filtered ITIs)', [None]+[r['id'] for r in filtered],
    format_func=lambda x: 'All filtered ITIs' if x is None else next(f'{r["name"]} — {r["district"]} (#{r["id"]})' for r in filtered if r['id']==x))

m = folium.Map(location=[22.7,71.5], zoom_start=7, tiles='OpenStreetMap', control_scale=True)
points = []
rows = []
for r in filtered:
    ok = eligible(r)
    row = {'ID': r['id'], 'ITI': r['name'], 'District': r['district'], 'Address (PDF extraction)': r.get('text',''),
           'PIN': r.get('pin',''), 'Location status': 'Approximate locality' if ok else 'Pending verification',
           'Latitude': r.get('lat') if ok else None, 'Longitude': r.get('lon') if ok else None,
           'PDF page': r['page']}
    popup = f'<b>{escape(r["name"])}</b><br>{escape(r["district"])}<br>Approximate locality centre'
    for i, p in origins:
        km = haversine_km(p['lat'],p['lon'],r['lat'],r['lon']) if ok else None
        row[f'Location {i+1} — {p["name"]} (air km)'] = round(km,1) if km is not None else None
        if ok:
            popup += f'<br>Location {i+1}: ≈ {km:,.0f} km'
            if show_lines and (selected is None or selected == r['id']):
                label = f'{escape(p["name"])} → {escape(r["name"])}: ≈ {km:,.0f} km (air)'
                folium.PolyLine([[p['lat'],p['lon']],[r['lat'],r['lon']]], color=COLORS[i],
                    weight=3 if selected else 1, opacity=.85 if selected else .22,
                    tooltip=folium.Tooltip(label, permanent=show_labels or selected is not None, sticky=False)).add_to(m)
    rows.append(row)
    if ok:
        points.append([r['lat'],r['lon']])
        folium.CircleMarker([r['lat'],r['lon']], radius=9 if selected==r['id'] else 5,
            color='#142e3a', weight=1, fill=True, fill_color='#f6b849' if selected==r['id'] else '#159a84', fill_opacity=.85,
            tooltip=escape(r['name']), popup=folium.Popup(popup,max_width=350)).add_to(m)
for i, p in origins:
    points.append([p['lat'],p['lon']])
    folium.Marker([p['lat'],p['lon']], tooltip=f'Location {i+1}: {escape(p["name"])}',
        icon=folium.Icon(color='blue' if i==0 else 'purple', icon='home')).add_to(m)
if selected:
    target = next(r for r in filtered if r['id']==selected)
    if eligible(target):
        points = [[target['lat'],target['lon']]]+[[p['lat'],p['lon']] for _,p in origins]
if points:
    m.fit_bounds(points, padding=(35,35), max_zoom=12)
st_folium(m, height=600, use_container_width=True, key='results_map', returned_objects=[])
st.caption('Green dots = approximate ITI locality; blue/purple = your selected locations. Overlapping dots may represent multiple ITIs in one town.')

st.subheader('ITI list aur distances')
df = pd.DataFrame(rows)
if not df.empty:
    distance_columns = [c for c in df.columns if c.endswith('(air km)')]
    if distance_columns:
        sort_by = st.selectbox('Nearest-first sort', distance_columns)
        df = df.sort_values(sort_by, na_position='last')
    st.dataframe(df, hide_index=True, width='stretch')
    st.download_button('Download current list + distances (CSV)', df.to_csv(index=False).encode('utf-8-sig'),
                       file_name='gujarat_iti_distances.csv', mime='text/csv')
else:
    st.info('Is filter mein koi ITI nahi mili. Filters clear karein.')
if selected:
    source_row = ROOT / 'data' / 'records' / f'{selected}.png'
    if source_row.exists():
        with st.expander('Original PDF address dekhein'):
            st.image(str(source_row), caption='Original Gujarati source row — extracted text can contain OCR errors.')
with st.expander('Data source aur accuracy'):
    st.write('User-provided MahitiPustika.pdf, printed pages 24–45 (PDF pages 34–55). '
             '289 government ITI entries. List is a source snapshot, not a live admission/vacancy feed. '
             'Coordinates are approximate GeoNames / OpenStreetMap locality points, not verified campuses. '
             'Distance uses Haversine on a spherical Earth. Missing locations remain blank; never treated as zero.')
    st.caption('GeoNames: CC BY 4.0 • OpenStreetMap contributors: ODbL • Map tiles: OpenStreetMap')
    st.markdown('[GeoNames](https://www.geonames.org/) · [OpenStreetMap copyright](https://www.openstreetmap.org/copyright)')
    pdf = ROOT / 'data' / 'MahitiPustika.pdf'
    if pdf.exists():
        st.download_button('Download source PDF', pdf.read_bytes(), 'MahitiPustika.pdf', 'application/pdf')
