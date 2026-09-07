import json
import os
import re
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).parent
PORT = int(os.getenv('PORT', '8000'))
API_KEY = os.getenv('TWELVE_DATA_API_KEY', '')
BASE_URL = 'https://api.twelvedata.com'
SOCIAL_FEED_URL = 'https://rss.app/feeds/qkLIKFkGSJMSJLO1.xml'


def provider_request(path, params):
    if not API_KEY:
        raise RuntimeError('TWELVE_DATA_API_KEY is not configured')
    query = '&'.join(f'{key}={value}' for key, value in params.items())
    request = Request(f'{BASE_URL}{path}?{query}&apikey={API_KEY}', headers={'User-Agent': 'VirtualPortfolio/1.0'})
    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode('utf-8'))
    if payload.get('status') == 'error' or payload.get('code'):
        raise RuntimeError(payload.get('message', 'Twelve Data request failed'))
    return payload


def provider_batch(symbols):
    if not API_KEY:
        raise RuntimeError('TWELVE_DATA_API_KEY is not configured')
    requests = {symbol: {'url': f'/quote?symbol={symbol}'} for symbol in symbols}
    body = json.dumps(requests).encode('utf-8')
    request = Request(f'{BASE_URL}/batch', data=body, method='POST', headers={'Authorization': f'apikey {API_KEY}', 'Content-Type': 'application/json'})
    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode('utf-8'))
    if payload.get('status') == 'error' or payload.get('code'):
        raise RuntimeError(payload.get('message', 'Twelve Data batch request failed'))
    return payload.get('data', {})


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/social-feed':
            try:
                request = Request(SOCIAL_FEED_URL, headers={'User-Agent': 'VirtualPortfolio/1.0'})
                with urlopen(request, timeout=15) as response:
                    raw = response.read()
                if b"We can\xe2\x80\x99t locate this feed" in raw or b"can't locate this feed" in raw.lower():
                    raise RuntimeError('RSS.app says this feed was deleted or invalid')
                root = ET.fromstring(raw)
                items = []
                symbols = set()
                for item in root.findall('.//item')[:10]:
                    title = item.findtext('title', '')
                    description = item.findtext('description', '')
                    symbols.update(re.findall(r'\$([A-Z]{1,5}(?:\.[A-Z])?)\b', f'{title} {description}'))
                    items.append({'title': title, 'link': item.findtext('link', ''), 'date': item.findtext('pubDate', ''), 'description': description})
                self.send_json(200, {'ok': True, 'items': items, 'symbols': sorted(symbols), 'source': SOCIAL_FEED_URL})
            except Exception as error:
                self.send_json(502, {'ok': False, 'source': SOCIAL_FEED_URL, 'error': f'RSS feed unavailable: {error}'})
            return
        if parsed.path == '/api/health':
            self.send_json(200 if API_KEY else 503, {'ok': bool(API_KEY), 'provider': 'Twelve Data', 'error': None if API_KEY else 'TWELVE_DATA_API_KEY is not configured'})
            return
        if parsed.path == '/api/quotes':
            symbols = [symbol for symbol in parse_qs(parsed.query).get('symbols', [''])[0].split(',') if symbol]
            try:
                self.send_json(200, {'provider': 'Twelve Data', 'quotes': provider_batch(symbols)})
            except Exception as error:
                self.send_json(502, {'error': str(error)})
            return
        if parsed.path == '/api/quote':
            symbol = parse_qs(parsed.query).get('symbol', [''])[0]
            try:
                quote = provider_request('/quote', {'symbol': symbol})
                self.send_json(200, {'provider': 'Twelve Data', 'quote': quote})
            except Exception as error:
                self.send_json(502, {'error': str(error)})
            return
        if parsed.path == '/api/history':
            values = parse_qs(parsed.query)
            symbol = values.get('symbol', [''])[0]
            date = values.get('date', [''])[0]
            try:
                history = provider_request('/time_series', {'symbol': symbol, 'interval': '1day', 'outputsize': '5000', 'start_date': date, 'end_date': date})
                self.send_json(200, {'provider': 'Twelve Data', 'history': history})
            except Exception as error:
                self.send_json(502, {'error': str(error)})
            return
        if parsed.path == '/' or parsed.path == '/index.html':
            body = (ROOT / 'index.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)

    def log_message(self, format, *args):
        return


if __name__ == '__main__':
    print(f'Virtual Portfolio running at http://localhost:{PORT}')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
