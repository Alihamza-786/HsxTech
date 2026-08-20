import xml.etree.ElementTree as ET
from typing import List
from urllib.parse import urljoin
import requests

# Sitemaps to skip (non-English and duplicate locale sitemaps)
SKIP_SITEMAPS = {
    "sitemap-fr.xml", 
    "sitemap-de.xml", 
    "sitemap-ar.xml", 
    "sitemap-es.xml", 
    "sitemap-id.xml", 
    "sitemap-th.xml",
    "sitemap-en-us.xml",
    "sitemap-en-gb.xml",
}

def fetch_urls_from_sitemap(sitemap_url: str) -> List[str]:
    """Fetch URLs from a single sitemap XML."""
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code == 404:
            return []
        response.raise_for_status()

        root = ET.fromstring(response.content)
        namespaces = (
            {"ns": root.tag.split("}")[0].strip("{")} if "}" in root.tag else ""
        )

        if namespaces:
            urls = [elem.text for elem in root.findall(".//ns:loc", namespaces)]
        else:
            urls = [elem.text for elem in root.findall(".//loc")]

        return [u for u in urls if u]

    except Exception as e:
        print(f"  [WARNING] Could not fetch {sitemap_url}: {e}")
        return []

def get_sitemap_urls(base_url: str, sitemap_filename: str = "sitemap.xml") -> List[str]:
    """
    Fetches URLs from sitemap or sitemap index.
    Supports both single sitemaps and sitemap index files.
    Skips non-English sitemaps automatically.
    """
    try:
        # First try sitemap index
        index_url = urljoin(base_url, "sitemap-index.xml")
        response = requests.get(index_url, timeout=10)

        all_urls = []

        if response.status_code == 200:
            print(f"Found sitemap index at: {index_url}")
            root = ET.fromstring(response.content)
            namespaces = (
                {"ns": root.tag.split("}")[0].strip("{")} if "}" in root.tag else ""
            )

            if namespaces:
                sub_sitemaps = [elem.text for elem in root.findall(".//ns:loc", namespaces)]
            else:
                sub_sitemaps = [elem.text for elem in root.findall(".//loc")]

            print(f"Found {len(sub_sitemaps)} sub-sitemaps")

            for sitemap in sub_sitemaps:
                sitemap_name = sitemap.rstrip("/").split("/")[-1]

                if sitemap_name in SKIP_SITEMAPS:
                    print(f"  Skipping: {sitemap_name}")
                    continue

                print(f"  Processing: {sitemap_name}")
                urls = fetch_urls_from_sitemap(sitemap)
                print(f"    Found {len(urls)} URLs")
                all_urls.extend(urls)

        else:
            print(f"No sitemap index found, trying {sitemap_filename}")
            sitemap_url = urljoin(base_url, sitemap_filename)
            all_urls = fetch_urls_from_sitemap(sitemap_url)

            if not all_urls:
                return [base_url.rstrip("/")]

        # Deduplicate while preserving order
        seen = set()
        unique_urls = []
        for url in all_urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)

        print(f"\nTotal unique URLs: {len(unique_urls)}")
        return unique_urls

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch sitemap: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse sitemap XML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error processing sitemap: {str(e)}")

if __name__ == "__main__":
    urls = get_sitemap_urls("https://netsoltech.com/")
    print("\nSample URLs:")
    for url in urls[:10]:
        print(f"  {url}")
