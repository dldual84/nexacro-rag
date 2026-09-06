from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

from pathlib import Path

from app.agent import NexacroAgent


BASE_DIR = Path(
    __file__
).resolve().parent.parent

WEB_DIR = BASE_DIR / "web"


app = Flask(__name__)

CORS(app)

agent = NexacroAgent()


@app.route("/")
def index():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )


@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify(
        {
            "status": "ok"
        }
    )


@app.route(
    "/api/ask",
    methods=["POST"]
)
def api_ask():

    try:

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify(
                {
                    "error":
                        "JSON body is required"
                }
            ), 400

        question = data.get(
            "question",
            ""
        )

        if not isinstance(
            question,
            str
        ):

            return jsonify(
                {
                    "error":
                        "question must be a string"
                }
            ), 400

        question = question.strip()

        if not question:

            return jsonify(
                {
                    "error":
                        "question is required"
                }
            ), 400

        print("=" * 70)
        print("Nexacro Agent API")
        print("=" * 70)
        print("질문:")
        print(question)
        print("Agent 실행 중...")

        answer = agent.run(
            question
        )

        return jsonify(
            {
                "question": question,
                "answer": answer
            }
        )

    except Exception as e:

        print(
            "API ERROR:",
            repr(e)
        )

        return jsonify(
            {
                "error": str(e)
            }
        ), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )