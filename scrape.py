import requests
from bs4 import BeautifulSoup

def scrape_text(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36'
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve {url} (status code: {response.status_code})")
        return ""
    
    soup = BeautifulSoup(response.content, 'html.parser')

    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    text = soup.get_text(separator='\n', strip=True)
    return text

# Example usage
url = 'https://pirana.biz/'
print(scrape_text(url))
