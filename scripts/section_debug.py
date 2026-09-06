import fitz
import re


PDF_PATH = "data/nexacro_17_workbook.pdf"

SECTION_PATTERN = re.compile(
    r"(?m)^(\d+\.\d+(?:\.\d+)?)\s+(.+)$"
)


def main():

    doc = fitz.open(PDF_PATH)

    print("=" * 70)
    print("PDF Section Debug")
    print("=" * 70)

    total_matches = 0

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text()

        matches = list(
            SECTION_PATTERN.finditer(text)
        )

        if matches:

            print()
            print(f"[PAGE {page_number}]")

            for match in matches:

                section = match.group(1)
                title = match.group(2).strip()

                print(
                    f"  {section} | {title}"
                )

                total_matches += 1

    print()
    print("=" * 70)
    print("전체 Section 발견 개수:", total_matches)
    print("=" * 70)


if __name__ == "__main__":
    main()