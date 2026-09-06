from app.agent import NexacroAgent


def main():

    agent = NexacroAgent()

    questions = [

        "CheckBox의 truevalue가 뭔지 설명하고 실제 사용하는 예제도 보여줘",

        "Grid 데이터를 처리하는 예제를 보여줘",

        "Grid의 setCellProperty 메서드는 어떻게 사용하는가?",

    ]

    for question in questions:

        print()
        print()
        print("#" * 100)
        print("QUESTION")
        print(question)
        print("#" * 100)

        answer = agent.run(
            question
        )

        print()
        print("#" * 100)
        print("ANSWER")
        print("#" * 100)
        print(answer)


if __name__ == "__main__":
    main()