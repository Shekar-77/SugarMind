"""
SugarMind — FastAPI Backend
════════════════════════════
Install:
    pip install fastapi uvicorn python-multipart

Run:
    uvicorn server:app --reload --port 8000

Then open:  http://localhost:8000
"""

import json, shutil, datetime, pathlib, asyncio
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ── Your modules (unchanged) ─────────────────────────────────────────────────
from src.inference import Chatbot, raw_input
from src.audio_to_text import audio_to_text
from src.video_analysis import process_multimodal_video

# ── Upload directory ──────────────────────────────────────────────────────────
UPLOAD_DIR = pathlib.Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="SugarMind")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

# ── Lazy bot singleton ────────────────────────────────────────────────────────
_bot: Chatbot | None = None

def get_bot() -> Chatbot:
    global _bot
    if _bot is None:
        print("⚙️  Loading model…")
        _bot = Chatbot(raw_input)
        print("✅  Model ready.")
    return _bot

# Per-agent conversation histories  {agent: [{role, content}, …]}
histories: dict[str, list] = {"Emo": [], "Logic": [], "Gen": []}


def system_prompt(agent: str) -> str:
    bot = get_bot()
    return {
        "Emo":   bot.emo_system_prompt,
        "Logic": bot.logic_system_prompt,
        "Gen":   bot.gen_system_prompt,
    }[agent]


# ── Serve the single-page frontend ───────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return open("index.html", encoding="utf-8").read()


# ── Reset a single agent's history ───────────────────────────────────────────
@app.post("/reset")
async def reset(agent: str = Form(...)):
    histories[agent] = []
    return {"ok": True}


# ── Upload audio or video, run processing, return transcript/description ──────
@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    agent: str = Form(...),
    mode:  str = Form(...),   # "audio" | "video"
):
    ext = pathlib.Path(file.filename).suffix or ".webm"
    ts  = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = UPLOAD_DIR / f"{mode}_{agent}_{ts}{ext}"

    with open(dst, "wb") as f:
        shutil.copyfileobj(file.file, f)

    if mode == "audio":
        text = audio_to_text(file_path=str(dst))
    else:
        desc = process_multimodal_video(video_path=str(dst))
        text = f"Video analysis: {desc}"

    return {"text": text, "saved_as": dst.name}


# ── SSE streaming chat ───────────────────────────────────────────────────────
@app.get("/chat")
async def chat_stream(agent: str, message: str):

    bot = get_bot()

    msgs = [{"role": "system", "content": system_prompt(agent)}] + histories[agent]
    msgs.append({"role": "user", "content": message})
    histories[agent].append({"role": "user", "content": message})

    async def event_gen():
        q: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_event_loop()
        full_reply = ""

        # Sync producer: runs bot.generate() in a thread.
        # Each token is immediately put on the queue — no waiting for completion.
        def _produce():
            bot.messages = msgs
            try:
                for chunk in bot.generate():
                    token = chunk["choices"][0]["text"]
                    loop.call_soon_threadsafe(q.put_nowait, token)
            finally:
                loop.call_soon_threadsafe(q.put_nowait, None)  # sentinel

        loop.run_in_executor(None, _produce)

        # Async consumer: yield each token to the SSE client as it arrives
        while True:
            token = await q.get()
            if token is None:   # sentinel — generation complete
                break
            full_reply += token
            yield f"data: {json.dumps({'token': token})}\n\n"

        histories[agent].append({"role": "assistant", "content": full_reply})
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )