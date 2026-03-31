import gradio as gr

from src.inference import Chatbot, raw_input, raw_input2
from src.audio_to_text import audio_to_text
from src.video_analysis import process_multimodal_video
import json

# ── init ──────────────────────────────────────────────────────────────────────
bot = Chatbot(raw_input, activity_name='gears')


# ── agent setup ───────────────────────────────────────────────────────────────
def set_agent(agent):
    bot.messages = []
    if agent == "Emo":
        bot.messages.append({"role": "system", "content": bot.emo_system_prompt})
    elif agent == "Logic":
        bot.messages.append({"role": "system", "content": bot.logic_system_prompt})
    else:
        bot.messages.append({"role": "system", "content": bot.gen_system_prompt})


# ── activity selection ────────────────────────────────────────────────────────
selected_activity = {"name": "gears"}

def select_activity(activity_name):
    """Update the selected activity and reset the conversation."""
    selected_activity["name"] = activity_name
    bot.activity_name = activity_name          # ← updates bot's activity
    bot.messages = []
    status_text = "⚙️ Gears Activity selected — ready!" if activity_name == "gears" else "📦 3D Volume Activity selected — ready!"
    return [], gr.update(value=status_text)


# ── chat (streaming) ──────────────────────────────────────────────────────────
def chat(agent, input_type, text, audio, video, history):
    if history is None:
        history = []

    if len(bot.messages) == 0:
        set_agent(agent)

    if input_type == "Text":
        print("Into the text")
        if not text or not text.strip():
            yield history, history, gr.update(value="")
            return
        user_input = text.strip()
        user_input = f"Text response: {user_input}"

    elif input_type == "Audio":
        print("In into the audio", flush=True)
        if audio is None:
            yield history, history, gr.update(value="")
            return
        user_input = audio_to_text(file_path=audio)
        if isinstance(user_input, dict):
            user_input = f"Audio response:{user_input}"
        else:
            user_input = str(user_input) if user_input else ""
        print(f"[Audio] transcription: {user_input}", flush=True)
        if not user_input:
            history.append({"role": "assistant", "content": "⚠️ Could not transcribe audio. Please try again."})
            yield history, history, gr.update(value="")
            return

    elif input_type == "Video":
        if video is None:
            yield history, history, gr.update(value="")
            return
        result = process_multimodal_video(video_path=video)
        user_input = f"Video analysis: {result}"

    else:
        yield history, history, gr.update(value="")
        return

    bot.messages.append({"role": "user", "content": user_input})
    history.append({"role": "user", "content": user_input})
    yield history, history, gr.update(value="")

    response = bot.generate()
    reply = ""
    history.append({"role": "assistant", "content": ""})

    for chunk in response:
        token = chunk["choices"][0]["text"]
        reply += token
        history[-1]["content"] = reply
        yield history, history, gr.update(value="")

    bot.messages.append({"role": "assistant", "content": reply})


# ── input panel toggle ────────────────────────────────────────────────────────
def toggle(choice):
    return (
        gr.update(visible=choice == "Text"),
        gr.update(visible=choice == "Audio"),
        gr.update(visible=choice == "Video"),
    )


# ══════════════════════════════════════════════════════════════════════════════
#  CSS — Sugar Labs palette
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --bg:      #eef4ee;
    --surface: #ffffff;
    --border:  #ccdacc;
    --green:   #3fb24c;
    --teal:    #00b4c8;
    --blue:    #0082cc;
    --orange:  #f47d00;
    --red:     #e6292b;
    --purple:  #7b4f9e;
    --pink:    #e84f99;
    --text:    #1a2a1a;
    --muted:   #607060;
    --r:       18px;
    --rs:      11px;
}

body, .gradio-container {
    font-family: 'Nunito', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
footer { display: none !important; }
.gradio-container { max-width: 880px !important; margin: 0 auto !important; padding: 20px !important; }

/* ── header ── */
#header-banner {
    background: linear-gradient(135deg, #0082cc 0%, #00b4c8 50%, #3fb24c 100%);
    border-radius: var(--r); padding: 20px 28px;
    display: flex; align-items: center; gap: 16px;
    margin-bottom: 20px;
    box-shadow: 0 6px 28px rgba(0,130,204,0.28);
}
#header-banner .hicon {
    width: 54px; height: 54px; background: #fff; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 28px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.14); flex-shrink: 0;
    animation: spin-slow 12s linear infinite;
}
@keyframes spin-slow { to { transform: rotate(360deg); } }
#header-banner h1 {
    font-family: 'Fredoka One', sans-serif !important;
    font-size: 30px !important; color: #fff !important; margin: 0 !important;
}
#header-banner p {
    color: rgba(255,255,255,0.85) !important; font-size: 13px !important;
    font-weight: 600 !important; margin: 2px 0 0 !important;
}

/* ── section labels ── */
.slabel {
    font-family: 'Fredoka One', sans-serif !important;
    font-size: 11px; text-transform: uppercase; letter-spacing: 1.4px;
    color: var(--muted); margin-bottom: 8px; display: block;
}

/* ── activity selector — Gradio buttons only ── */
#gears-btn-gr, #volume-btn-gr {
    border-radius: var(--r) !important;
    border: 3px solid var(--border) !important;
    background: var(--surface) !important;
    padding: 18px 10px !important;
    font-family: 'Fredoka One', sans-serif !important;
    font-size: 16px !important;
    color: var(--muted) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    transition: all 0.2s !important;
}
#gears-btn-gr:hover {
    border-color: var(--orange) !important;
    color: var(--orange) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(244,125,0,0.25) !important;
}
#volume-btn-gr:hover {
    border-color: var(--blue) !important;
    color: var(--blue) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 6px 20px rgba(0,130,204,0.25) !important;
}

/* ── agent radio — activity cards ── */
#agent-selector .wrap { display: flex !important; gap: 10px !important; }
#agent-selector label {
    flex: 1 !important; min-width: 120px !important;
    border-radius: var(--r) !important; border: 3px solid var(--border) !important;
    background: var(--surface) !important; padding: 16px 10px !important;
    cursor: pointer !important; transition: all 0.2s !important;
    display: flex !important; flex-direction: column !important;
    align-items: center !important; gap: 5px !important;
    font-family: 'Fredoka One', sans-serif !important;
    font-size: 15px !important; color: var(--muted) !important;
    text-align: center !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
#agent-selector label:nth-child(1):hover { border-color: var(--pink)  !important; color: var(--pink)  !important; transform: translateY(-3px) !important; }
#agent-selector label:nth-child(2):hover { border-color: var(--blue)  !important; color: var(--blue)  !important; transform: translateY(-3px) !important; }
#agent-selector label:nth-child(3):hover { border-color: var(--green) !important; color: var(--green) !important; transform: translateY(-3px) !important; }
#agent-selector label:nth-child(1).selected { background: linear-gradient(135deg, var(--pink), var(--purple)) !important; color: #fff !important; border-color: transparent !important; box-shadow: 0 6px 20px rgba(232,79,153,0.35) !important; transform: translateY(-3px) !important; }
#agent-selector label:nth-child(2).selected { background: linear-gradient(135deg, var(--blue), var(--teal))   !important; color: #fff !important; border-color: transparent !important; box-shadow: 0 6px 20px rgba(0,130,204,0.35)    !important; transform: translateY(-3px) !important; }
#agent-selector label:nth-child(3).selected { background: linear-gradient(135deg, var(--green), #22a845)      !important; color: #fff !important; border-color: transparent !important; box-shadow: 0 6px 20px rgba(63,178,76,0.35)     !important; transform: translateY(-3px) !important; }
#agent-selector input { display: none !important; }

/* ── input type pill bar ── */
#input-type-selector .wrap {
    display: flex !important; gap: 6px !important;
    background: var(--surface) !important; border: 2px solid var(--border) !important;
    border-radius: 50px !important; padding: 4px !important;
}
#input-type-selector label {
    flex: 1 !important; border-radius: 50px !important; border: none !important;
    padding: 8px 14px !important; font-family: 'Fredoka One', sans-serif !important;
    font-size: 13px !important; color: var(--muted) !important;
    background: transparent !important; cursor: pointer !important;
    transition: all 0.18s !important; text-align: center !important;
    display: flex !important; align-items: center !important; justify-content: center !important; gap: 5px !important;
}
#input-type-selector label:hover { background: var(--bg) !important; }
#input-type-selector label.selected {
    background: linear-gradient(135deg, var(--teal), var(--blue)) !important;
    color: #fff !important; box-shadow: 0 3px 10px rgba(0,130,204,0.30) !important;
}
#input-type-selector input { display: none !important; }

/* ── chatbot window ── */
#chatbot-window {
    border-radius: var(--r) !important; border: 2px solid var(--border) !important;
    background: var(--surface) !important; box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
    overflow: hidden !important;
}
#chatbot-window .message-wrap { font-family: 'Nunito', sans-serif !important; font-size: 14px !important; }

/* ── text input — FIXED: text now visible ── */
#text-input textarea {
    font-family: 'Nunito', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    border-radius: var(--rs) !important;
    border: 2.5px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text) !important;              /* ← typed text visible */
    caret-color: var(--teal) !important;        /* ← cursor colour */
    transition: border-color 0.2s, box-shadow 0.2s !important;
    padding: 12px 16px !important;
    resize: none !important;
}
#text-input textarea::placeholder {
    color: var(--muted) !important;
    opacity: 1 !important;
}
#text-input textarea:focus {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0,180,200,0.15) !important;
    outline: none !important;
}
#text-input label {
    font-weight: 800 !important; font-size: 11px !important; color: var(--muted) !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
}

/* ── audio / video upload ── */
#audio-input, #video-input {
    border: 2.5px dashed var(--border) !important; border-radius: var(--r) !important;
    background: var(--surface) !important; transition: border-color 0.2s !important;
}
#audio-input:hover  { border-color: var(--orange) !important; }
#video-input:hover  { border-color: var(--red)    !important; }
#audio-input label, #video-input label {
    font-weight: 800 !important; font-size: 11px !important; color: var(--muted) !important;
    text-transform: uppercase !important; letter-spacing: 1px !important;
}

/* ── send button ── */
#send-btn {
    background: linear-gradient(135deg, #0082cc, #00b4c8) !important;
    color: #fff !important; font-family: 'Fredoka One', sans-serif !important;
    font-size: 16px !important; border-radius: 50px !important; border: none !important;
    padding: 13px 32px !important; box-shadow: 0 4px 16px rgba(0,130,204,0.35) !important;
    transition: all 0.2s !important; letter-spacing: 0.3px !important;
    width: 100% !important;
}
#send-btn:hover { transform: translateY(-2px) !important; box-shadow: 0 7px 22px rgba(0,130,204,0.45) !important; }

/* ── status bar ── */
#status-bar {
    display: flex; align-items: center; gap: 8px; padding: 6px 2px;
    font-size: 12px; font-weight: 700; color: var(--muted);
}
.sdot { width:8px; height:8px; border-radius:50%; background:var(--green); box-shadow:0 0 6px var(--green); animation:sdot 2s infinite; }
@keyframes sdot { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:.4;transform:scale(1.4)} }
"""


# ══════════════════════════════════════════════════════════════════════════════
#  UI
# ══════════════════════════════════════════════════════════════════════════════
with gr.Blocks(
    css=CSS,
    title="SugarMind",
    theme=gr.themes.Soft(
        primary_hue="cyan", secondary_hue="green",
        font=gr.themes.GoogleFont("Nunito"),
    ),
) as demo:

    # ── header ────────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="header-banner">
      <div class="hicon">⚙️</div>
      <div>
        <h1>SugarMind</h1>
        <p>Activity Reflection — pick an agent and start the conversation</p>
      </div>
    </div>
    """)

    # ── activity selector — Gradio buttons only (decorative HTML buttons removed) ──
    gr.HTML('<span class="slabel">Choose your activity</span>')
    with gr.Row(elem_id="activity-selector-row"):
        gears_btn  = gr.Button("⚙️  Gears",     elem_id="gears-btn-gr",  variant="secondary")
        volume_btn = gr.Button("📦  3D Volume",  elem_id="volume-btn-gr", variant="secondary")

    activity_status = gr.Textbox(
        value="⚙️ Gears Activity selected — ready!",
        label="",
        interactive=False,
        elem_id="activity-status",
        show_label=False,
        container=False,
    )

    # ── agent selector ────────────────────────────────────────────────────────
    gr.HTML('<span class="slabel">Choose your learning companion</span>')
    agent = gr.Radio(
        choices=["Emo", "Logic", "Gen"],
        value="Gen",
        label="",
        elem_id="agent-selector",
    )
    gr.HTML("""
    <script>
    (function() {
        const ICONS = {Emo:'💜', Logic:'🧩', Gen:'✨'};
        function inject() {
            document.querySelectorAll('#agent-selector label').forEach(lbl => {
                const t = lbl.textContent.trim();
                if (ICONS[t] && !lbl.querySelector('._aico')) {
                    const s = document.createElement('span');
                    s.className = '_aico';
                    s.style.cssText = 'font-size:28px;display:block;margin-bottom:3px;pointer-events:none';
                    s.textContent = ICONS[t];
                    lbl.insertBefore(s, lbl.firstChild);
                }
            });
        }
        if (document.readyState !== 'loading') inject();
        else document.addEventListener('DOMContentLoaded', inject);
        setTimeout(inject, 800);
    })();
    </script>
    """)

    # ── input type switcher ───────────────────────────────────────────────────
    gr.HTML('<span class="slabel" style="margin-top:18px;display:block">Input mode</span>')
    input_type = gr.Radio(
        choices=["Text", "Audio", "Video"],
        value="Text",
        label="",
        elem_id="input-type-selector",
    )
    gr.HTML("""
    <script>
    (function() {
        const MAP = {Text:'💬', Audio:'🎤', Video:'🎥'};
        function inject() {
            document.querySelectorAll('#input-type-selector label').forEach(lbl => {
                const t = lbl.textContent.trim();
                if (MAP[t] && !lbl.querySelector('._iico')) {
                    const s = document.createElement('span');
                    s.className = '_iico';
                    s.style.cssText = 'margin-right:5px;pointer-events:none';
                    s.textContent = MAP[t];
                    lbl.insertBefore(s, lbl.firstChild);
                }
            });
        }
        if (document.readyState !== 'loading') inject();
        else document.addEventListener('DOMContentLoaded', inject);
        setTimeout(inject, 800);
    })();
    </script>
    """)

    # ── chatbot ───────────────────────────────────────────────────────────────
    chatbot = gr.Chatbot(
        height=430,
        show_label=False,
        elem_id="chatbot-window",
        placeholder="<div style='text-align:center;padding:40px;color:#607060;font-family:Fredoka One,sans-serif;font-size:16px'>⚙️ Select an activity and agent above, then say hello!</div>",
    )

    # ── status bar ────────────────────────────────────────────────────────────
    gr.HTML("""
    <div id="status-bar">
      <span class="sdot"></span>
      <span>Ready · SugarMind is listening</span>
    </div>
    """)

    # ── input panels ──────────────────────────────────────────────────────────
    text_input = gr.Textbox(
        label="Your message",
        placeholder="Type here and press Send (or hit Enter)…",
        lines=2, max_lines=6,
        visible=True,
        elem_id="text-input",
    )
    audio_input = gr.Audio(
        type="filepath", label="Record or upload audio",
        visible=False, elem_id="audio-input",
    )
    video_input = gr.Video(
        label="Record or upload video",
        visible=False, elem_id="video-input",
    )

    # ── send button ───────────────────────────────────────────────────────────
    send_btn = gr.Button("➤  Send", elem_id="send-btn", variant="primary")

    # ── wiring ────────────────────────────────────────────────────────────────
    input_type.change(toggle, inputs=input_type, outputs=[text_input, audio_input, video_input])

    # Activity buttons: update bot.activity_name, reset chat, update status
    gears_btn.click(
        fn=lambda: select_activity("gears"),
        inputs=[],
        outputs=[chatbot, activity_status],
    )
    volume_btn.click(
        fn=lambda: select_activity("threedvolume"),
        inputs=[],
        outputs=[chatbot, activity_status],
    )

    send_btn.click(
        chat,
        inputs=[agent, input_type, text_input, audio_input, video_input, chatbot],
        outputs=[chatbot, chatbot, text_input],
    )
    text_input.submit(
        chat,
        inputs=[agent, input_type, text_input, audio_input, video_input, chatbot],
        outputs=[chatbot, chatbot, text_input],
    )

    # reset history when switching agent
    agent.change(lambda a: (set_agent(a), [])[-1], inputs=agent, outputs=chatbot)


demo.queue()

if __name__ == "__main__":
    demo.launch(debug=True)