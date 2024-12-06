import argparse
import json
import sys
import os


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract references using GROBID")
    parser.add_argument("-p", "--pdfs-dir", default="data/pdfs")
    parser.add_argument("-m", "--metadata-file", default="data/metadata.json")
    parser.add_argument("-g", "--grobid-dir", default="data/grobid")
    args = parser.parse_args()

    data = []
    with open(args.metadata_file, "r") as f:
        data = json.load(f)

    for i, item in enumerate(data):
        doi = item["DOI"]
        if not os.path.isfile(f"data/grobid/{i}.xml") and os.path.isfile(
            f"data/pdfs/{i}.pdf"
        ):
            cmd = f"curl -v --form includeRawCitations=1 --form input=@./{args.pdfs_dir}/{i}.pdf https://nanobubbles.univ-grenoble-alpes.fr/grobid/api/processReferences > {args.grobid_dir}/{i}.xml"
            print("Converting into XML:\n'" + cmd + "'")
            os.system(cmd)
        else:
            print(
                f"{args.grobid_dir}/{i}.xml already exists or {args.pdfs_dir}/{i}.pdf missing"
            )
