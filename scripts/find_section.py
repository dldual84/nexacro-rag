import pymupdf


PDF_PATH = "data/nexacro_17_workbook.pdf"


def main():

    doc = pymupdf.open(PDF_PATH)

    print("=" * 70)
    print("CheckBox 본문 위치 검색")
    print("=" * 70)

    found = 0

    for page_number, page in enumerate(doc, start=1):

        text = page.get_text()

        # 목차에서는 "15.1"과 "CheckBox 소개"가
        # 모두 존재하지만 실제 본문도 동일함.
        # 우선 둘 다 포함된 페이지를 모두 찾는다.
        if "15.1" in text and "CheckBox 소개" in text:

            found += 1

            print()
            print("=" * 70)
            print(f"PDF Page: {page_number}")
            print("=" * 70)

            print(text[:2500])

    print()
    print("=" * 70)
    print("발견 페이지 수:", found)
    print("=" * 70)


if __name__ == "__main__":
    main()