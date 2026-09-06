from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path

from app.rag import ask


# ==================================================
# 기본 설정
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = BASE_DIR / "web"

app = Flask(__name__)
CORS(app)


# ==================================================
# 메인 화면
# ==================================================

@app.route("/")
def index():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )


# ==================================================
# Health Check
# ==================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({
        "status": "ok"
    })


# ==================================================
# RAG 질문 API
# ==================================================

@app.route(
    "/api/ask",
    methods=["POST"]
)
def api_ask():

    try:

        # --------------------------------------------------
        # JSON 데이터 확인
        # --------------------------------------------------

        data = request.get_json(
            silent=True
        )

        if not data:

            return jsonify({
                "error": "JSON body is required"
            }), 400


        # --------------------------------------------------
        # 질문 확인
        # --------------------------------------------------

        question = data.get(
            "question",
            ""
        )

        if not isinstance(
            question,
            str
        ):

            return jsonify({
                "error": "question must be a string"
            }), 400


        question = question.strip()


        if not question:

            return jsonify({
                "error": "question is required"
            }), 400


        # --------------------------------------------------
        # RAG 실행
        #
        # Hybrid Search
        #       ↓
        # Ranking
        #       ↓
        # LLM
        # --------------------------------------------------

        result = ask(
            question
        )


        # --------------------------------------------------
        # RAG 결과 반환
        # --------------------------------------------------

        return jsonify({

            "question":
                result.get(
                    "question",
                    question
                ),

            "answer":
                result.get(
                    "answer",
                    ""
                ),

            "contexts":
                result.get(
                    "contexts",
                    []
                )
        })


    except Exception as e:

        print(
            "API ERROR:",
            repr(e)
        )

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# Flask 실행
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
