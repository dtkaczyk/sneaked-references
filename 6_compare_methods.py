import argparse
import csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare results between methods")
    parser.add_argument("-m1", "--method1-results", default="data/results_method1.tsv")
    parser.add_argument("-m2", "--method2-results", default="data/results_method2.csv")
    parser.add_argument("-o", "--output", default="data/results_both.csv")
    args = parser.parse_args()

    method2_results = {}
    method2_statuses = {}
    with open(args.method2_results, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            doi, status, _, sneaked_refs, _ = row
            method2_statuses[doi] = status
            if "compared" == status:
                method2_results[doi] = int(sneaked_refs)

    with open(args.method1_results, "r") as fr, open(args.output, "w") as fw:
        reader = csv.reader(fr, delimiter="\t")
        writer = csv.writer(fw)
        for row in reader:
            if len(row) < 7:
                continue
            doi = row[0]
            if not doi.startswith("10."):
                writer.writerow(
                    [h.strip() for h in row]
                    + ["Nb Sneaked (method 2)", "Methods comparison"]
                )
                continue
            if row[7] == "No reference in Json":
                status = "No reference in Json"
            elif method2_statuses.get(doi, "") == "PDF missing or broken":
                status = "PDF missing or broken"
            elif method2_results[doi] == int(row[6]):
                status = "Methods agree"
            else:
                status = "Methods disagree"
            writer.writerow(row + [method2_results.get(doi, 0), status])
