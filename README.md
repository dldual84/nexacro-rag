# Nexacro 17 RAG AI Agent

Nexacro 17 기술문서(PDF, CHM)를 기반으로 문서를 검색하고 답변을 생성하는 RAG(Retrieval-Augmented Generation) 기반 AI Agent입니다.

Vector Search와 BM25 기반 Keyword Search를 결합한 Hybrid Search를 사용하며, 질문 유형에 따라 일반 검색, API 검색, 예제 검색 Tool을 선택합니다.

또한 MCP(Model Context Protocol)를 적용하여 Nexacro 전문 검색 기능을 MCP Tool 형태로 외부 AI Client에서 사용할 수 있도록 구성했습니다.

---

## 1. 주요 기능

- Nexacro 17 PDF 문서 처리
- Nexacro 17 CHM 문서 처리
- 문서 Chunking
- Embedding
- ChromaDB 기반 Vector Search
- BM25 기반 Keyword Search
- Hybrid Search
- 검색 결과 Ranking
- Nexacro 질문 유형 분석
- Nexacro API 검색
  - Property
  - Method
  - Event
- Nexacro 예제 검색
- 검색 결과 기반 LLM 답변 생성
- Flask REST API
- MCP Server

---

## 2. 전체 구조

```text
Nexacro 17 PDF
Nexacro 17 CHM
       │
       ▼
Document Processing
       │
       ▼
Chunking
       │
       ├───────────────┐
       ▼               ▼
Embedding          Keyword Index
       │               │
       ▼               ▼
   ChromaDB           BM25
       │               │
       └───────┬───────┘
               ▼
        Hybrid Search
               │
               ▼
            Ranking
               │
               ▼
        Nexacro Agent
               │
      ┌────────┼────────┐
      ▼        ▼        ▼
   General    API     Example
    Search   Search    Search
      │        │        │
      └────────┼────────┘
               ▼
              LLM
               │
               ▼
             Answer
```

---

## 3. MCP 구조

기존 RAG 검색 기능을 MCP Tool로 제공합니다.

```text
MCP Client
    │
    ▼
MCP Server
    │
    ├── nexacro_search
    │
    ├── nexacro_api_search
    │
    └── nexacro_example_search
             │
             ▼
       Existing RAG
             │
       ┌─────┴─────┐
       ▼           ▼
   Hybrid Search  Ranking
       │
       ▼
    ChromaDB
```

MCP는 기존 RAG 기능을 대체하지 않습니다.

기존 검색 로직을 그대로 사용하면서 외부 AI Client가 Nexacro 전문 검색 기능을 호출할 수 있도록 표준 MCP Tool 인터페이스를 추가합니다.

---

## 4. MCP Tools

### 4.1 nexacro_search

Nexacro 17의 일반적인 컴포넌트 및 기능을 검색합니다.

주요 검색 대상:

- Component
- 기능 설명
- 일반적인 사용 방법
- Nexacro 개념

예:

```text
Grid 컴포넌트의 주요 기능
```

호출:

```json
{
  "query": "Grid 컴포넌트의 주요 기능",
  "top_k": 3
}
```

---

### 4.2 nexacro_api_search

Nexacro 17 API 문서를 검색합니다.

검색 대상:

- Property
- Method
- Event
- API 설명
- Syntax
- Parameter
- Return

예:

```text
Grid setCellProperty 메서드 사용법
```

호출:

```json
{
  "query": "Grid setCellProperty 메서드 사용법",
  "top_k": 3
}
```

---

### 4.3 nexacro_example_search

Nexacro 17 기술문서에 포함된 실제 구현 예제 및 샘플 코드를 검색합니다.

예:

```text
Grid setCellProperty 실제 사용 예제
```

호출:

```json
{
  "query": "Grid setCellProperty 실제 사용 예제",
  "top_k": 3
}
```

---

## 5. 프로젝트 구조

```text
nexacro-rag/
│
├── app/
│   ├── agent.py
│   ├── api.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── hybrid_search.py
│   ├── keyword_search.py
│   ├── llm.py
│   ├── ranking.py
│   ├── retriever.py
│   ├── search.py
│   └── vector_store.py
│
├── tools/
│   ├── __init__.py
│   ├── nexacro_search.py
│   ├── nexacro_api_search.py
│   └── nexacro_example_search.py
│
├── mcp_server/
│   ├── __init__.py
│   └── server.py
│
├── scripts/
│   ├── ingest.py
│   ├── chunker_test.py
│   ├── pdf_test.py
│   ├── search_test.py
│   └── ...
│
├── web/
│   └── index.html
│
├── build_index.py
├── chunk_size_test.py
├── mcp_test.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### 데이터 디렉터리

문서 원본 및 생성 데이터는 GitHub에 저장하지 않습니다.

```text
data/
chroma_db/
```

개발 환경에서는 다음과 같은 구조로 사용합니다.

```text
data/
├── PDF 원본
├── CHM 원본
├── chunks.json
├── chm_parsed.json
└── chm_chunks.json

chroma_db/
└── ChromaDB Vector Index
```

문서 데이터와 Vector Index는 각 개발 환경에서 다시 생성합니다.

---

## 6. 주요 구성요소

| 구성 | 역할 |
| --- | --- |
| Python | 전체 애플리케이션 개발 |
| Flask | REST API 제공 |
| Ollama | 로컬 LLM 및 Embedding 실행 |
| LLM | 검색 결과를 기반으로 답변 생성 |
| Embedding Model | 문서를 Vector로 변환 |
| ChromaDB | 문서 Vector 저장 및 Vector Search |
| BM25 | Keyword Search |
| Hybrid Search | Vector + Keyword 검색 결합 |
| Ranking | 검색 결과 우선순위 조정 |
| RAG | 검색 문서를 LLM에 제공하여 답변 생성 |
| Nexacro Agent | 질문 분석 및 Tool 선택 |
| MCP Server | Nexacro 검색 기능을 MCP Tool로 제공 |

---

## 7. 모델 설정

모델은 `.env`에서 설정합니다.

```env
LLM_MODEL=qwen3:8b
EMBED_MODEL=nomic-embed-text:latest
```

현재 권장 구성:

| 용도 | 모델 |
| --- | --- |
| LLM | `qwen3:8b` |
| Embedding | `nomic-embed-text:latest` |

---

## 8. 설치

### 8.1 Python

Python 3.x를 설치합니다.

### 8.2 가상환경 생성

```powershell
python -m venv .venv
```

가상환경 활성화:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 8.3 패키지 설치

```powershell
pip install -r requirements.txt
```

### 8.4 Ollama

Ollama가 실행 가능한 환경이어야 합니다.

설치된 모델 확인:

```powershell
ollama list
```

---

## 9. 문서 처리

문서 원본은 GitHub에 저장하지 않습니다.

개발 환경의 `data/` 폴더에 Nexacro 17 PDF와 CHM 파일을 준비합니다.

### 9.1 PDF Chunking

```powershell
python -m scripts.ingest
```

생성:

```text
data/chunks.json
```

### 9.2 CHM 처리

CHM 추출:

```powershell
python -m app.extract_chm
```

CHM Parsing:

```powershell
python -m app.parse_chm
```

CHM Chunking:

```powershell
python -m app.build_chm_chunks
```

생성:

```text
data/chm_parsed.json
data/chm_chunks.json
```

---

## 10. Vector Index 생성

PDF와 CHM Chunk가 생성된 후 Vector Index를 생성합니다.

```powershell
python .\build_index.py
```

생성된 Vector Index는 다음 위치에 저장됩니다.

```text
chroma_db/
```

---

## 11. 검색 테스트

일반 검색:

```powershell
python -m scripts.search_test
```

API 검색:

```powershell
python .\app\api_tool_test.py
```

예제 검색:

```powershell
python .\app\example_tool_test.py
```

---

## 12. Agent 테스트

Agent를 통해 Nexacro 질문을 테스트할 수 있습니다.

예:

```text
Grid의 setCellProperty 메서드는 어떻게 사용하는가?
```

Agent는 질문을 분석하여 필요한 Tool을 선택합니다.

```text
질문
 ↓
Question Analysis
 ↓
Tool Selection
 ↓
Search
 ↓
Ranking
 ↓
LLM
 ↓
Answer
```

---

## 13. Flask REST API

서버 실행:

```powershell
python -m app.api
```

기본 주소:

```text
http://127.0.0.1:5000
```

### 13.1 Health Check

```powershell
curl.exe http://127.0.0.1:5000/health
```

### 13.2 질문 요청

PowerShell에서는 JSON Property 이름에 반드시 큰따옴표를 사용해야 합니다.

```powershell
curl.exe -X POST "http://127.0.0.1:5000/api/ask" `
  -H "Content-Type: application/json" `
  -d '{"question":"Grid의 setCellProperty 메서드는 어떻게 사용하는가?"}'
```

---

## 14. MCP Server 실행

MCP Server는 stdio transport를 사용합니다.

실행:

```powershell
mcp run mcp_server/server.py
```

서버가 실행되면 MCP Client의 요청을 기다립니다.

다음 Tool을 MCP Client에서 호출할 수 있습니다.

```text
nexacro_search
nexacro_api_search
nexacro_example_search
```

---

## 15. MCP Client 테스트

프로젝트에는 MCP Server를 직접 호출하여 테스트하는 `mcp_test.py`가 포함되어 있습니다.

실행:

```powershell
python .\mcp_test.py
```

정상 실행 시 다음과 같이 Tool 목록이 출력됩니다.

```text
NEXACRO MCP TEST

등록된 MCP Tools
- nexacro_search
- nexacro_api_search
- nexacro_example_search
```

이후 각 Tool을 실제로 호출하여 Nexacro 문서 검색 결과를 확인합니다.

---

## 16. MCP 테스트 결과

현재 MCP 연결 테스트에서 다음 기능이 정상 동작합니다.

```text
MCP Client
    ↓
MCP Server
    ↓
Tool Discovery
    ↓
nexacro_search
    ↓
Hybrid Search / Ranking
    ↓
Nexacro 문서 검색 결과
```

API 검색도 정상 동작합니다.

예:

```text
Grid setCellProperty 메서드 사용법
```

검색 결과:

```text
source  : nexacro_manual
section : Grid_Method_setCellProperty
api_intent : METHOD
```

예제 검색에서는 실제 Nexacro 코드가 포함된 Workbook 문서를 반환합니다.

---

## 17. 코드 예제 처리

RAG 답변 생성 시 검색된 문서를 기준으로 답변합니다.

특히 코드 예제의 경우 다음 원칙을 적용합니다.

- 검색 문서에 실제 코드가 있으면 해당 코드를 사용
- 검색 문서에 코드가 없으면 코드를 임의로 생성하지 않음
- 문서에 없는 Property / Method / Event 정보를 추측하지 않음
- 문서에 없는 XML / JavaScript 예제를 생성하지 않음

검색 문서에 실제 코드가 없는 경우:

```text
제공된 문서에서 실제 코드 예제를 확인할 수 없습니다.
```

검색 근거가 부족한 경우:

```text
제공된 문서만으로는 확인하기 어렵습니다.
```

---

## 18. Git 관리

GitHub에는 소스 코드와 설정 파일만 저장합니다.

### GitHub에 저장

```text
app/
tools/
mcp_server/
scripts/
web/
*.py
requirements.txt
README.md
.gitignore
```

### GitHub에 저장하지 않음

```text
data/
chroma_db/
.venv/
__pycache__/
.env
```

특히 다음 데이터는 용량이 크거나 개발 환경에서 다시 생성할 수 있으므로 GitHub에 저장하지 않습니다.

```text
PDF
CHM
chunks.json
chm_parsed.json
chm_chunks.json
ChromaDB
```

---

## 19. Git Branch

MCP 기능은 별도의 Branch에서 관리합니다.

```text
main
 │
 └── feature/mcp-server
```

MCP 관련 변경사항은 다음 Branch에 반영합니다.

```text
feature/mcp-server
```

---

## 20. 향후 개선

### 검색 품질 개선

- Reranker 적용
- Component / API / Example 관계 강화
- API 검색 정확도 개선
- Example 검색 정확도 개선
- 코드 검색 강화

### Agent 개선

- 질문 유형 분류 고도화
- Tool 선택 정확도 향상
- 복수 Tool 결과 통합
- 검색 결과 평가 및 재검색

### MCP 고도화

현재:

```text
MCP
 ├── nexacro_search
 ├── nexacro_api_search
 └── nexacro_example_search
```

향후:

```text
MCP
 ├── Nexacro Search
 ├── Nexacro API Search
 ├── Nexacro Example Search
 ├── Nexacro Component Information
 └── Nexacro Code Assistance
```

Nexacro 개발환경 또는 외부 AI Agent에서 Nexacro 전문 Tool을 직접 사용할 수 있는 구조로 확장합니다.

---

## 21. 기술 스택

```text
Python
Flask
Ollama
ChromaDB
BM25
PyMuPDF
BeautifulSoup
MCP
```

### 문서

```text
Nexacro 17 Component Workbook PDF
Nexacro 17 CHM Manual
```