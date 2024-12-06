import argparse
import json
import csv

from pypdf import PdfReader
from rapidfuzz import fuzz


def diff_references(metadata=None, pdf_path=None):
    if metadata is None or pdf_path is None:
        return {"status": "not_compared", "reason": "missing input data"}
    if "reference" not in metadata:
        return {"status": "not_compared", "reason": "missing metadata references"}

    pdf_text = ""
    try:
        reader = PdfReader(pdf_path)
        pdf_text = [p.extract_text() for p in reader.pages]
        pdf_text = " ".join(pdf_text)
    except:
        return {"status": "not_compared", "reason": "PDF missing or broken"}

    refs = [r.get("unstructured", "") for r in metadata["reference"]]
    cited_dois = [r.get("DOI", "") for r in metadata["reference"]]

    similarities = [fuzz.partial_ratio(r, pdf_text) for r in refs]
    sneaked = [r for r, s in zip(refs, similarities) if r and s < 60]

    sneaked_cited = [
        r for r, d, s in zip(refs, cited_dois, similarities) if r and d and s < 60
    ]
    return {
        "status": "compared",
        "results": {
            "metadata-refs": len(refs),
            "sneaked-refs": len(sneaked),
            "sneaked-refs-with-doi": len(sneaked_cited),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Compare references between the metadata and the PDF"
    )
    parser.add_argument("-p", "--pdfs-dir", default="data/pdfs")
    parser.add_argument("-m", "--metadata-file", default="data/metadata.json")
    parser.add_argument("-o", "--output", default="data/results_method2.csv")
    args = parser.parse_args()

    t_dois = 0
    t_sneaked = 0
    t_sneaked_cited = 0

    data = []
    with open(args.metadata_file, "r") as f:
        data = json.load(f)

    with open(args.output, "w") as f:
        writer = csv.writer(f)
        for i, item in enumerate(data):
            doi = item["DOI"]
            result = diff_references(metadata=item, pdf_path=f"{args.pdfs_dir}/{i}.pdf")
            if result["status"] != "compared":
                writer.writerow([doi, result["reason"], "", "", ""])
            else:
                writer.writerow(
                    [
                        doi,
                        "compared",
                        result["results"]["metadata-refs"],
                        result["results"]["sneaked-refs"],
                        result["results"]["sneaked-refs-with-doi"],
                    ]
                )

                t_sneaked += result["results"]["sneaked-refs"]
                t_sneaked_cited += result["results"]["sneaked-refs-with-doi"]
                if t_sneaked_cited:
                    t_dois += 1

            print(i, t_dois, t_sneaked, t_sneaked_cited)
