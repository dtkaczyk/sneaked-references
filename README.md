# Detecting sneaked references

A set of scripts for detecting and analysing the cases of sneaked references in the Crossref metadata. Sneaked references are bibliographic references deposited into Crossref that are missing from the original article.

The following scripts are included:

* `1_get_metadata.py` - download metadata records from [Crossref REST API](http://api.crossref.org/)
* `2_get_pdfs.py` - download corresponding PDFs from the landing pages
* `3_method2_detect.py` - detect sneaked references by searching for reference strings from the metadata records within the PDF text
* `4_use_grobid.py` - extract bibliographic references from PDFs using [GROBID](https://github.com/kermitt2/grobid)
* `5_method1_use_last.py` - detect sneaked references by comparing the metadata records with references extracted by GROBID
* `6_compare_methods.py` - compare and merge the results of two methods
* `7_Graph.R` - generate images and some additional statistics
* `8_statistics.py` - calculate overal statistics
