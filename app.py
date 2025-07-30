def scrape_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to retrieve {url} (status code: {response.status_code})"

    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove unwanted elements
    for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
        tag.decompose()
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
