from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
import os
from datetime import datetime



app = Flask(__name__)
CORS(app)


def scrape_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"<p>Failed to retrieve {url} (status code: {response.status_code})</p>"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove unwanted tags
    for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
        tag.decompose()

    # Remove elements by common class names
    for class_name in ['header', 'footer', 'site-header', 'site-footer', 'navigation']:
        for tag in soup.select(f'.{class_name}'):
            tag.decompose()

    # Try to extract the main content
    if soup.body:
        return str(soup.body)  # Keep formatting for frontend styling
    else:
        return str(soup)  # Fallback



@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        text = scrape_text(url)
        if not text or text.startswith("Failed to retrieve"):
            return jsonify({'error': text}), 500

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
