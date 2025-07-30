from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to retrieve {url} (status code: {response.status_code})"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove unwanted elements
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'img']):
        tag.decompose()

    # Remove common class names
    for class_name in ['header', 'footer', 'site-header', 'site-footer', 'navigation']:
        for tag in soup.select(f'.{class_name}'):
            tag.decompose()

    markdown_lines = []

    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'p', 'li', 'a']):
        text = tag.get_text(strip=True)
        if not text:
            continue

        if tag.name == 'h1':
            markdown_lines.append(f"# {text}")
        elif tag.name == 'h2':
            markdown_lines.append(f"## {text}")
        elif tag.name == 'h3':
            markdown_lines.append(f"### {text}")
        elif tag.name == 'h4':
            markdown_lines.append(f"#### {text}")
        elif tag.name == 'h5':
            markdown_lines.append(f"##### {text}")
        elif tag.name == 'li':
            markdown_lines.append(f"- {text}")
        elif tag.name == 'a':
            href = tag.get('href', '#')
            markdown_lines.append(f"[{text}]({href})")
        else:
            markdown_lines.append(text)

    return "\n\n".join(markdown_lines)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    # Add https:// if missing
    if not url.startswith("http"):
        url = "https://" + url

    try:
        text = scrape_text(url)

        if not text.strip():
            return jsonify({'error': 'No content found on the page'}), 404

        if "Failed to retrieve" in text:
            return jsonify({'error': text}), 500

        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
