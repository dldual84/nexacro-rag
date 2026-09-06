import os
import subprocess
import sys


CHM_FILE = os.path.join("data", "nexacro_manual.chm")
OUTPUT_DIR = os.path.join("data", "chm_extracted")


def extract_chm():

    if not os.path.exists(CHM_FILE):
        print(f"CHM 파일을 찾을 수 없습니다.")
        print(f"경로: {CHM_FILE}")
        return False

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 60)
    print("CHM 추출 시작")
    print("=" * 60)

    print(f"CHM : {CHM_FILE}")
    print(f"OUT : {OUTPUT_DIR}")

    # 7-Zip 경로
    possible_paths = [
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ]

    seven_zip = None

    for path in possible_paths:
        if os.path.exists(path):
            seven_zip = path
            break

    if seven_zip is None:
        print()
        print("7-Zip을 찾을 수 없습니다.")
        print("다음 경로 중 하나에 7z.exe가 있어야 합니다.")
        for path in possible_paths:
            print(path)
        return False

    print()
    print(f"7-Zip : {seven_zip}")
    print()

    command = [
        seven_zip,
        "x",
        CHM_FILE,
        f"-o{OUTPUT_DIR}",
        "-y"
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        print(result.stdout)

        if result.returncode != 0:
            print("CHM 추출 실패")
            print(result.stderr)
            return False

    except Exception as e:
        print("CHM 추출 중 오류 발생")
        print(e)
        return False

    # HTML 파일 개수 확인
    html_files = []

    for root, dirs, files in os.walk(OUTPUT_DIR):

        for filename in files:

            lower = filename.lower()

            if lower.endswith((".html", ".htm")):

                html_files.append(
                    os.path.join(root, filename)
                )

    print()
    print("=" * 60)
    print("CHM 추출 완료")
    print("=" * 60)

    print(f"HTML 파일 : {len(html_files)}개")

    for path in html_files[:20]:
        print(path)

    if len(html_files) > 20:
        print(f"... 외 {len(html_files) - 20}개")

    return True


if __name__ == "__main__":

    success = extract_chm()

    if not success:
        sys.exit(1)