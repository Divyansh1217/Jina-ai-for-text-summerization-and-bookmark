import requests
from bs4 import BeautifulSoup
from urllib.parse import quote,urlparse
# Fetch title and favicon


def extract_clean_name(url):
    return url.replace("https://", "").replace("http://", "")


def fetch_metadata(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    title = soup.title.string if soup.title else "No Title"
    favicon = url.rstrip("/") + "/favicon.ico"
    return title, favicon


def fetch_summary(url):
 
    url=extract_clean_name(url)

    full_url = f"https://r.jina.ai/http://{url}"

    try:
        response = requests.get(full_url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching summary: {e}")
        if response.status_code == 422:
            return "Summary unavailable: The provided URL could not be processed."
        return "Summary temporarily unavailable."


