import argparse
import csv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Print basic statistics"
    )
    parser.add_argument("-r", "--results", default="data/results_both.csv")
    args = parser.parse_args()

    dois_processed = 0
    dois_no_refs = 0
    dois_no_pdf = 0
    dois_methods_agree = 0
    dois_methods_disagree = 0
    dois_manipulated_method1 = 0
    dois_manipulated_method2 = 0

    refs_sneaked_method1 = 0
    refs_sneaked_method2 = 0

    print("Disagreements (method1, method2):")

    with open(args.results, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            doi = row[0]
            if not doi.startswith("10."):
                continue
            status = row[-1]
            method1_sneaked = int(row[6])
            method2_sneaked = int(row[-2])

            dois_processed += 1

            if status == "No reference in Json":
                dois_no_refs += 1
                continue
            elif status == "PDF missing or broken":
                dois_no_pdf += 1
                continue
            elif status == "Methods agree":
                dois_methods_agree += 1
            else:
                print(doi, method1_sneaked, method2_sneaked)
                dois_methods_disagree += 1

            if method1_sneaked > 0:
                dois_manipulated_method1 += 1
            if method2_sneaked > 0:
                dois_manipulated_method2 += 1

            refs_sneaked_method1 += method1_sneaked
            refs_sneaked_method2 += method2_sneaked

    print()
    print("Total processed DOIs", dois_processed)
    print(" - DOIs with no references in JSON", dois_no_refs)
    print(" - DOIs with no PDF", dois_no_pdf)
    print(" - DOIs where methods agreed", dois_methods_agree)
    print(" - DOIs where methods disagreed", dois_methods_disagree)
    print()
    print("Total DOIs manipulated (method1)", dois_manipulated_method1)
    print("Total DOIs manipulated (method2)", dois_manipulated_method2)
    print()
    print("Total sneaked references (method1)", refs_sneaked_method1)
    print("Total sneaked references (method2)", refs_sneaked_method2)

