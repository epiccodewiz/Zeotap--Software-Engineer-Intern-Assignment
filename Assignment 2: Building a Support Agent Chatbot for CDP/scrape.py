import requests
from bs4 import BeautifulSoup
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
}

def scrape_documentation(base_url, output_dir, link_filter="/docs/"):
    """Scrapes documentation pages from the given base URL and saves them as text files."""
    os.makedirs(output_dir, exist_ok=True)

    # Fetch the main documentation page
    print(f"Scraping: {base_url}")
    response = requests.get(base_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Error: Failed to fetch {base_url} (Status Code: {response.status_code})")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract links from the documentation page
    links = soup.find_all("a", href=True)
    doc_links = set()  # Use set to avoid duplicates

    for link in links:
        href = link["href"]

        #  Fix duplicate `/docs/docs/`
        if href.startswith("/docs/docs/"):
            href = href.replace("/docs/docs/", "/docs/")  # Remove extra `/docs/`

        # Ensure URLs are properly formatted
        if href.startswith("/docs/"):
            full_url = base_url.rstrip("/") + href  # Convert to absolute URL
        elif href.startswith("http"):
            full_url = href  # Already an absolute URL
        else:
            full_url = base_url.rstrip("/") + "/" + href.lstrip("/")

        if link_filter in full_url:
            doc_links.add(full_url)

    if not doc_links:
        print("⚠️ No documentation links found! Check the website structure.")
        return
    
    print(f" Found {len(doc_links)} documentation pages.")

    # Fetch and save each documentation page
    for doc_url in doc_links:
        try:
            print(f"📄 Scraping page: {doc_url}")
            page_response = requests.get(doc_url, headers=HEADERS)
            if page_response.status_code != 200:
                print(f"⚠️ Skipping {doc_url} (Status Code: {page_response.status_code})")
                continue

            page_soup = BeautifulSoup(page_response.text, "html.parser")
            
            #  Extract main content (Modify this if needed)
            content = (
                page_soup.find("main") or 
                page_soup.find("article") or 
                page_soup.find("section", class_="doc-content") or 
                page_soup.find("div", class_="content")
            )

            if not content:
                print(f"⚠️ Skipping {doc_url} (No readable content found)")
                continue

            # Save extracted content
            filename = os.path.join(output_dir, doc_url.split("/")[-1] + ".txt")
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content.get_text())

            print(f" Saved: {filename}")
            time.sleep(1)  # 🕒 Avoid getting blocked

        except Exception as e:
            print(f"❌ Error scraping {doc_url}: {e}")

# ✅ Example Usage 
scrape_documentation("https://segment.com/docs/", "segment_docs")
scrape_documentation("https://docs.mparticle.com/", "mparticle_docs")
scrape_documentation("https://www.lytics.com/docs/", "lytics_docs")
scrape_documentation("https://www.zeotap.com/documentation/", "zeotap_docs")
