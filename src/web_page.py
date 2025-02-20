import requests
from bs4 import BeautifulSoup

from src.exception import WebPageException

class WebPage():
    def __init__(self,
                 url):
        """
        Web page for which to extract text content         
        """
        self.url = url
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def extract_text(self):
        """
        Extracts the text from a web page by scraping page and parsing html
        content to get relevant text        
        """
        # Extracting html content from web page
        r = requests.get(self.url, headers=self.headers)
        if r.status_code != 200:
            raise WebPageException(message=f"Failed to extract web content with status code {r.status_code}")
        # Parsing content from webpage
        soup = BeautifulSoup(r.content, "html.parser")
        print(soup)
        # Remove unwanted elements
        for tag in ["script", "style", "header", "nav", "footer", "aside", "form", "noscript"]:
            for element in soup.find_all(tag):
                element.decompose()  # Removes the element
        # Try to find the main content
        main_content = soup.find("article") or soup.find("main") or soup.find("div", {"id": "content"})
        print(main_content)
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            # Fallback: Get the largest text-heavy div
            divs = soup.find_all("div")
            main_content = max(divs, key=lambda d: len(d.get_text()), default=None)
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
        return text

