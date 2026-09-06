# Nexacro용 Chunker
import re


SECTION_PATTERN = re.compile(
    r"(?m)^(\d+\.\d+(?:\.\d+)?)\s+(.+)$"
)


def split_into_sections(text: str):
    """
    Nexacro 문서의
    24.15 제목
    24.15.1 제목
    같은 section 번호를 기준으로 텍스트를 분리한다.
    """

    matches = list(SECTION_PATTERN.finditer(text))

    if not matches:
        return [
            {
                "section": None,
                "title": None,
                "text": text.strip(),
            }
        ]

    sections = []

    for index, match in enumerate(matches):
        start = match.start()

        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)

        section_number = match.group(1)
        title = match.group(2).strip()

        section_text = text[start:end].strip()

        sections.append(
            {
                "section": section_number,
                "title": title,
                "text": section_text,
            }
        )

    return sections