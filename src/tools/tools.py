from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os 
from tavily import TavilyClient
from rich import print
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re 

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query : str) -> str:
  "Search the web for ewcent andd reliable information on a topic."
  results = tavily.search(query=query, max_results=5)

  out = []

  for r in results['results']:
    out.append(
      f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"
    )

  return "\n-----\n".join(out)





@tool

def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL.
    Uses multiple extraction strategies for better reliability.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-us, en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # Step 1: Fetch webpage
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        response.raise_for_status()

        html = response.text

        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        doc = BeautifulSoup
        clean_html = doc.summary()

        # Step 2: Parse HTML
        soup = BeautifulSoup(clean_html,"html.parser")

        # Step 3: Remove unwanted elements
        for tag in soup([
            "script",
            "style",
            "nav",
            "header",
            "footer",
            "aside",
            "noscript",
            "iframe",
            "form"
        ]):
            tag.decompose()



        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]




        soup = BeautifulSoup(clean_html,"html.parser")
        
                # Step 3: Remove unwanted elements
        for tag in soup([
                    "script",
                    "style",
                    "nav",
                    "header",
                    "footer",
                    "aside",
                    "noscript",
                    "iframe",
                    "form"
                ]):
                    tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]

        return "Could not extract meaningful content from the page."


    except requests.exceptions.Timeout:
        return "Error: Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {str(e)}"

    except requests.exceptions.RequestException as e:
        return f"Request Error: {str(e)}"

    except Exception as e:
        return f"Scraping Error: {str(e)}"
