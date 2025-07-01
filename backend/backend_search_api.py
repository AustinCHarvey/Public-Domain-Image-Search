# backend_search_api
# Flask backend for aggregating public domain image searches

from flask import Flask, request, jsonify
import requests
from urllib.parse import urlencode
from datetime import datetime

app = Flask(__name__)

LOC_BASE_URL = 'https://www.loc.gov/photos/'
WIKIMEDIA_API = 'https://commons.wikimedia.org/w/api.php'

# Optional: Simple in-memory cache of past queries
cache = {}

@app.route('/api/search')
def search():
    query = request.args.get('q', '').strip().lower()
    public_only = request.args.get('public_only', 'false').lower() == 'true'
    if not query:
        return jsonify({"results": []})

    if query in cache and not public_only:
        return jsonify(cache[query])

    results = []

    # Library of Congress Search
    loc_params = {'q': query, 'fo': 'json'}
    loc_resp = requests.get(LOC_BASE_URL, params=loc_params)
    if loc_resp.ok:
        data = loc_resp.json()
        for item in data.get('results', []):
            if 'image' in item:
                results.append({
                    'thumbnail': item['image'][0],
                    'link': item['url'],
                    'source': 'Library of Congress',
                    'title': item.get('title', 'LOC Image'),
                    'license': 'Public Domain'
                })

    # Wikimedia Commons Search
    wm_params = {
        'action': 'query',
        'format': 'json',
        'generator': 'search',
        'gsrsearch': query,
        'gsrlimit': 10,
        'prop': 'imageinfo',
        'iiprop': 'url|extmetadata',
        'iiurlwidth': 300
    }
    wm_resp = requests.get(WIKIMEDIA_API, params=wm_params)
    if wm_resp.ok:
        data = wm_resp.json()
        for page in data.get('query', {}).get('pages', {}).values():
            imginfo = page.get('imageinfo', [{}])[0]
            if imginfo.get('thumburl'):
                license_info = imginfo.get('extmetadata', {}).get('LicenseShortName', {}).get('value', 'Unknown')
                results.append({
                    'thumbnail': imginfo['thumburl'],
                    'link': imginfo.get('descriptionurl', '#'),
                    'source': 'Wikimedia Commons',
                    'title': page.get('title', 'Wikimedia Image'),
                    'license': license_info
                })

    # Filter only public domain if requested
    if public_only:
        public_licenses = [
            'Public Domain',
            'No known copyright restrictions',
            'Public Domain Dedication',
            'US Government Work'
        ]
        results = [img for img in results if img.get('license') in public_licenses]

    payload = {"results": results, "query": query, "timestamp": datetime.utcnow().isoformat()}
    if not public_only:
        cache[query] = payload
    return jsonify(payload)

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/')
def index():
    return '🖼️ Public Domain Image Search API is running.'
