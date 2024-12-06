import argparse
import requests
import json
import urllib.request

from urllib.parse import urlparse
from bs4 import BeautifulSoup


def get_pdf_url(resource):
    if resource.endswith("pdf"):
        return resource
    r = requests.get(resource)
    html_content = r.text
    soup = BeautifulSoup(html_content, "lxml")
    links = soup.find_all("a")
    for link in links:
        l = link.get("href", "")
        if l.endswith("pdf"):
            if l.startswith("http"):
                return l
            else:
                url_obj = urlparse(url)
                return f"{url_obj.scheme}://{url_obj.netloc}/{l}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download PDFs")
    parser.add_argument("-o", "--output-dir", default="data/pdfs")
    parser.add_argument("-m", "--metadata-file", default="data/metadata.json")
    args = parser.parse_args()

    with open(args.metadata_file, "r") as f:
        data = json.load(f)

    for i, item in enumerate(data):
        print("Downloading", i)
        doi = item["DOI"]
        url = item["resource"]["primary"]["URL"]
        pdf = get_pdf_url(url)
        if pdf is not None:
            opener = urllib.request.build_opener()
            opener.addheaders = [("User-agent", "Mozilla/5.0")]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(pdf, f"{args.output_dir}/{i}.pdf")
