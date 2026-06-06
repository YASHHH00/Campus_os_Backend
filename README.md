# Campus OS Laptop Backend

The local AI server component of the Campus OS ecosystem. It processes images via EasyOCR, runs local LLM inference using Ollama, and handles vector search with ChromaDB.

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running locally
- (Optional but recommended) A dedicated GPU for fast OCR and LLM inference

## Setup

1. **Install dependencies:**
   ```bash
   make install
   ```

2. **Set up Ollama (llama3) and ChromaDB:**
   ```bash
   make setup
   ```
   *Windows Users*: Download Ollama manually from their website, then run `ollama pull llama3`.

3. **Configure Environment:**
   Copy `.env.example` to `.env` and fill in your Supabase credentials if you want WebRTC signaling to work out of the box.

## Running

Start the FastAPI development server:

```bash
make dev
```

The API will be available at `http://localhost:8000`.

## Endpoints

- `GET /health` - Service health status
- `POST /ocr` - Upload an image to run the full OCR -> Intent -> Summary pipeline
- `POST /extract_deadline` - Extract a deadline from text
- `POST /parse_receipt` - Parse a receipt into line items and total
- `POST /search_notes` - Semantic search across your synced notes

## Testing

Run the test suite:

```bash
make test
```
