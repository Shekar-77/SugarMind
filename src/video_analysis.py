import cv2
import whisper
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import librosa
import numpy as np
from moviepy.editor import VideoFileClip
from transformers import pipeline
import torch
from fer import FER

# ── Load Models ───────────────────────────────────────────────────────────────
device = "cpu"
print("Loading Whisper (Audio)...")
audio_model = whisper.load_model("base", device=device)

print("Loading BLIP (Visual)...")
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained(
    "Salesforce/blip-image-captioning-base",
    use_safetensors=True
).to(device)

device = "cuda" if torch.cuda.is_available() else "cpu"

emotion_classifier = pipeline(
    "audio-classification",
    model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition",
    device=0 if device == "cuda" else -1
)

face_detector = FER(mtcnn=True)


# ── helpers ───────────────────────────────────────────────────────────────────

def _safe_detect_emotions(frame: np.ndarray) -> list[dict]:
    """
    Crash-safe wrapper around FER.detect_emotions.

    MTCNN's ONet crashes with a Conv2D ValueError when the bbox batch is empty
    (shape (0, 48, 48, 3)). This happens when:
      • the frame is physically too small  → Guard 1
      • the frame is small enough that PNet/RNet filter all candidates → Guard 2
      • any other edge-case (dark/blurry frame, codec artefact)        → Guard 3

    Returns [] on any failure so callers can simply do `if not face_data`.
    """
    h, w = frame.shape[:2]

    # Guard 1 — absolute minimum: smaller than ONet's kernel → instant crash
    if h < 48 or w < 48:
        return []

    # Guard 2 — upscale so PNet/RNet produce candidates for ONet
    MIN_DIM = 300
    if min(h, w) < MIN_DIM:
        scale = MIN_DIM / min(h, w)
        frame = cv2.resize(
            frame,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_LINEAR,
        )

    # Guard 3 — catch the Conv2D empty-batch error and any other MTCNN error
    try:
        return face_detector.detect_emotions(frame) or []
    except Exception:
        return []


# ── main function ─────────────────────────────────────────────────────────────

def process_multimodal_video(video_path: str) -> list[dict]:

    # --- STEP 1: Audio Extraction & Transcription ---
    print("Extracting and analyzing audio quality...")
    video_clip = VideoFileClip(video_path)
    audio_path = "temp_audio.wav"

    if video_clip.audio:
        video_clip.audio.write_audiofile(audio_path, logger=None)
        audio_result = audio_model.transcribe(audio_path, verbose=False)
        segments = audio_result["segments"]
        y, sr = librosa.load(audio_path)
    else:
        segments, y, sr = [], None, None

    # --- STEP 2: Per-second Visual & Audio Analysis ---
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration_sec = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / max(fps, 1))
    final_report = []

    for second in range(duration_sec):
        cap.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
        ret, frame = cap.read()
        if not ret:
            break

        # 2.1 Visual Captioning (BLIP)
        rgb_frame = cv2.cvtColor(cv2.resize(frame, (384, 384)), cv2.COLOR_BGR2RGB)
        inputs = blip_processor(Image.fromarray(rgb_frame), return_tensors="pt").to(device)
        out = blip_model.generate(**inputs, max_new_tokens=20)
        visual_caption = blip_processor.decode(out[0], skip_special_tokens=True)

        # 2.2 Face & Visual Emotion Detection — uses crash-safe wrapper
        face_data = _safe_detect_emotions(frame)
        face_present = len(face_data) > 0
        visual_emotion = "N/A"
        visual_conf = 0.0

        if face_present:
            emotions = face_data[0]["emotions"]
            visual_emotion = max(emotions, key=emotions.get)
            visual_conf = float(emotions[visual_emotion])

        # 2.3 Audio Logic & Kid-Optimized Scoring
        audio_text = "[No Speech]"
        final_score = 0.0
        audio_tone = "N/A"

        if y is not None:
            current_segments = [s for s in segments if s["start"] <= second <= s["end"]]

            if current_segments:
                audio_text = " ".join([s["text"] for s in current_segments]).strip()
                ai_cert = float(np.exp(np.mean([s["avg_logprob"] for s in current_segments])))

                # Technical Quality Slicing
                start_samp = int(second * sr)
                end_samp   = int((second + 1) * sr)
                audio_slice = y[start_samp:end_samp]

                if len(audio_slice) > 0:
                    vol_norm     = min(float(np.mean(librosa.feature.rms(y=audio_slice))) / 0.05, 1.0)
                    clarity_norm = min(float(np.mean(librosa.feature.spectral_centroid(y=audio_slice, sr=sr))) / 3000, 1.0)

                    # Kid-Specific Metric: Verbal Effort (words per second)
                    effort_score = min(len(audio_text.split()) / 5, 1.0)

                    # Weighted Formula (40% AI cert, 30% Effort, 20% Volume, 10% Clarity)
                    audio_conf = (ai_cert * 0.4) + (effort_score * 0.3) + (vol_norm * 0.2) + (clarity_norm * 0.1)

                    # Final Fusion: 70% Audio + 30% Visual (penalised by 0.5 if no face)
                    face_multiplier = 1.0 if face_present else 0.5
                    final_score = round(
                        ((audio_conf * 0.7) + (visual_conf * 0.3)) * face_multiplier * 100, 2
                    )

                    # Tone Detection
                    tone_res   = emotion_classifier(audio_path)
                    audio_tone = tone_res[0]["label"]

        # 2.4 Kid-Friendly Status Interpretation
        if final_score > 75:
            status = "Super Star! Very Confident"
        elif final_score > 45:
            status = "Great Effort! Keep Sharing"
        else:
            status = "Thinking or Needs Encouragement"

        final_report.append({
            "timestamp":        f"{second}s",
            "face_detected":    face_present,
            "visual_emotion":   visual_emotion,
            "visual_caption":   visual_caption,
            "audio_speech":     audio_text,
            "audio_tone":       audio_tone,
            "confidence_score": f"{final_score}%",
            "status":           status,
        })
        print(f"[{second}s] Face: {face_present} | Score: {final_score}% | {status}")

    cap.release()
    video_clip.close()
    return final_report