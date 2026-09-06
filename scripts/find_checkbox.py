import pymupdf


PDF_PATH = "data/nexacro_17_workbook.pdf"


def main():

    doc = pymupdf.open(PDF_PATH)

    print("=" * 70)
    print("CheckBox 텍스트 검색")
    print("=" * 70)

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text()

        if "CheckBox" in text:

            print()
            print("=" * 70)
            print(f"PDF Page: {page_number}")
            print("=" * 70)

            print(text[:2000])


if __name__ == "__main__":
    main()