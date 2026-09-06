import os
import json
import re

from bs4 import BeautifulSoup


INPUT_DIR = os.path.join("data", "chm_extracted")
OUTPUT_FILE = os.path.join("data", "chm_parsed.json")


def clean_text(text):

    text = text.replace("\xa0", " ")

    # 여러 공백 정리
    text = re.sub(r"[ \t]+", " ", text)

    # 너무 많은 빈 줄 제거
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()


def extract_title(soup):

    # 우선순위
    for tag_name in ["h1", "h2", "h3"]:

        tag = soup.find(tag_name)

        if tag:

            title = tag.get_text(
                " ",
                strip=True
            )

            if title:
                return title

    if soup.title:

        title = soup.title.get_text(
            " ",
            strip=True
        )

        if title:
            return title

    return ""


def parse_html(file_path):

    try:

        with open(
            file_path,
            "rb"
        ) as f:

            raw = f.read()

        # CHM 내부 HTML은 인코딩이 다양할 수 있으므로
        # BeautifulSoup에 자동 감지를 맡긴다.
        soup = BeautifulSoup(
            raw,
            "html.parser"
        )

    except Exception as e:

        print(f"HTML 읽기 실패: {file_path}")
        print(e)

        return None

    # 필요없는 태그 제거
    for tag in soup([
        "script",
        "style",
        "noscript"
    ]):

        tag.decompose()

    title = extract_title(soup)

    body = soup.body

    if body:

        text = body.get_text(
            "\n",
            strip=True
        )

    else:

        text = soup.get_text(
            "\n",
            strip=True
        )

    text = clean_text(text)

    if not text:
        return None

    # 상대 경로
    relative_path = os.path.relpath(
        file_path,
        INPUT_DIR
    )

    return {
        "source": "nexacro_manual",
        "title": title,
        "path": relative_path,
        "text": text
    }


def parse_all():

    if not os.path.exists(INPUT_DIR):

        print("CHM 추출 폴더가 없습니다.")
        print(f"경로: {INPUT_DIR}")
        print()
        print("먼저 실행하세요:")
        print("python -m app.extract_chm")

        return

    documents = []

    print("=" * 60)
    print("CHM HTML 파싱 시작")
    print("=" * 60)

    for root, dirs, files in os.walk(INPUT_DIR):

        for filename in files:

            if not filename.lower().endswith(
                (".html", ".htm")
            ):
                continue

            file_path = os.path.join(
                root,
                filename
            )

            document = parse_html(
                file_path
            )

            if document:

                documents.append(
                    document
                )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            documents,
            f,
            ensure_ascii=False,
            indent=2
        )

    print()
    print("=" * 60)
    print("CHM HTML 파싱 완료")
    print("=" * 60)

    print(f"HTML : {len(documents)}개")
    print(f"출력: {OUTPUT_FILE}")

    print()
    print("샘플")

    for document in documents[:5]:

        print("-" * 60)
        print(f"Title : {document['title']}")
        print(f"Path  : {document['path']}")
        print(
            f"Text  : {document['text'][:300]}"
        )


if __name__ == "__main__":
    parse_all()