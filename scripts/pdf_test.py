import fitz


PDF_PATH = "data/nexacro_17_workbook.pdf"


def main():
    doc = fitz.open(PDF_PATH)

    print("PDF 정보")
    print("-" * 50)
    print("페이지 수:", len(doc))

    for page_number in range(min(3, len(doc))):
        page = doc[page_number]
        text = page.get_text()

        print()
        print("=" * 50)
        print(f"PAGE {page_number + 1}")
        print("=" * 50)
        print(text[:2000])


if __name__ == "__main__":
    main()