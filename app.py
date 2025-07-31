from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to retrieve {url} (status code: {response.status_code})"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove unwanted tags
    for tag in soup(['script', 'style', 'noscript', 'header', 'footer', 'nav', 'img']):
        tag.decompose()

    # Remove elements by common class names
    common_classes = [
        'header', 'footer', 'site-header', 'site-footer', 
        'sidebar', 'nav', 'navigation', 'ad', 'ads', 
        'breadcrumbs', 'scroll-to-top', 'top-link'
    ]
    for class_name in common_classes:
        for el in soup.select(f'.{class_name}'):
            el.decompose()

    # Remove elements by common ID names
    common_ids = [
        'header', 'footer', 'site-header', 'site-footer', 
        'sidebar', 'nav', 'navigation', 'ad', 'ads', 
        'breadcrumbs', 'scroll-to-top', 'top-link'
    ]
    for id_name in common_ids:
        for el in soup.select(f'#{id_name}'):
            el.decompose()

    # Convert content to markdown-style text
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
