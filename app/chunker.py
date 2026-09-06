import re


# 실제 문서 Section 번호만 인식
#
# 인식:
#   15.1
#   15.2
#   15.2.1
#   24.3
#   24.37.2
#
# 인식하지 않음:
#   1
#   2
#   3
#   1.
#   2.
#
SECTION_PATTERN = re.compile(
    r"(?m)^(\d+\.\d+(?:\.\d+)*)\s*$"
)


def clean_text(text):
    """
    PDF에서 추출된 텍스트를 정리한다.
    """

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        # 목차의 점선 제거
        if re.fullmatch(r"[.\s]+", line):
            continue

        lines.append(line)

    return "\n".join(lines)


def extract_sections(pages, min_page=1):
    """
    PDF 페이지들을 Section 단위로 묶는다.

    하나의 Section이 여러 페이지에 걸쳐 있으면
    다음 Section이 나올 때까지 계속 내용을 누적한다.
    """

    sections = []

    current = None

    for page in pages:

        page_number = page["page"]

        if page_number < min_page:
            continue

        text = page["text"]

        matches = list(
            SECTION_PATTERN.finditer(text)
        )

        # --------------------------------------------------
        # 현재 페이지에 Section이 없는 경우
        # --------------------------------------------------

        if not matches:

            if current is not None:

                content = clean_text(text)

                if content:
                    current["text"] += "\n" + content

                if page_number not in current["pages"]:
                    current["pages"].append(page_number)

            continue

        # --------------------------------------------------
        # 현재 페이지에서 Section 처리
        # --------------------------------------------------

        for index, match in enumerate(matches):

            section_number = match.group(1)

            # Section 번호 다음 영역
            start = match.end()

            # 다음 Section 위치
            if index + 1 < len(matches):
                end = matches[index + 1].start()
            else:
                end = len(text)

            section_area = text[start:end]

            lines = [
                line.strip()
                for line in section_area.splitlines()
                if line.strip()
            ]

            if not lines:
                continue

            # 첫 줄 = 제목
            title = lines[0]

            # 나머지 = 본문
            content = "\n".join(lines[1:])

            content = clean_text(content)

            # --------------------------------------------------
            # 기존 Section 종료
            # --------------------------------------------------

            if current is not None:

                if content:
                    current["text"] += "\n" + content

                if page_number not in current["pages"]:
                    current["pages"].append(page_number)

                sections.append(current)

            # --------------------------------------------------
            # 새 Section 시작
            # --------------------------------------------------

            current = {
                "section": section_number,
                "title": title,
                "pages": [page_number],
                "text": content,
            }

    # ------------------------------------------------------
    # 마지막 Section
    # ------------------------------------------------------

    if current is not None:
        sections.append(current)

    return sections