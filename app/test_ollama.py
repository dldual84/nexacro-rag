import os

from dotenv import load_dotenv
from ollama import chat


load_dotenv()

MODEL_NAME = os.getenv("LLM_MODEL")
#MODEL_NAME = "qwen3:8b"


def main():
    response = chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": "Nexacro 17에서 Grid 컴포넌트가 무엇인지 한 문장으로 설명해줘."
            }
        ],
    )

    print(response.message.content)


if __name__ == "__main__":
    main()