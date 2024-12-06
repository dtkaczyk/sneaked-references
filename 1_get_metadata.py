import argparse
import requests
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download metadata")
    parser.add_argument("-p", "--path", default="members/23876/works")
    parser.add_argument("-e", "--email", required=True)
    parser.add_argument("-m", "--metadata-file", default="data/metadata.json")
    args = parser.parse_args()

    data = []
    cursor = "*"
    downloaded = 0
    while True:
        page = requests.get(
            f"https://api.crossref.org/{args.path}",
            {
                "filter": "until-created-date:2024-11-25",
                "mailto": args.email,
                "cursor": cursor,
                "rows": 500,
            },
        ).json()["message"]
        total = page["total-results"]
        cursor = page["next-cursor"]
        if not page["items"]:
            break
        data.extend(page["items"])
        downloaded += len(page["items"])
        print(f"Downloaded {downloaded} out of {total}")

    data = [
        item
        for item in data
        if "journal" != item["type"]
        and item["container-title"][0]
        != "International Journal of Scientific Research and Modern Technology (IJSRMT)"
    ]

    with open(args.metadata_file, "w") as f:
        json.dump(data, f, indent=2)
