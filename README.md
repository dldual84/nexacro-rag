1. Python 설치
2. venv 생성
3. pip install -r requirements.txt
4. Ollama 설치
5. qwen3:8b 다운로드
6. nomic-embed-text 다운로드
7. PDF 처리
8. CHM 처리
9. Index 생성
10. Flask 실행

| 구성 | 역할 |
| --- | --- |
| **Ollama** | LLM을 로컬에서 실행해주는 서버/런타임 |
| **qwen3:8b** | 실제로 답변을 생성하는 LLM 모델 |
| **nomic-embed-text** | Embedding |	
| **llm.py** | 우리 프로그램에서 Ollama를 호출하는 코드 |
| **ChromaDB** | 문서 벡터 저장 및 Vector Search |
| **BM25** | 키워드 검색 |
| **Ranking** | 검색 결과의 우선순위 재조정 |
| **RAG** | 검색한 문서를 LLM에게 제공해서 답변하게 하는 전체 방식 |