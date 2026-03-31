import whisper
import librosa
import numpy as np
from transformers import pipeline

whisper_model = whisper.load_model("base")
emotion_classifier = pipeline(
    "audio-classification", 
    model="ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition"
)


def audio_to_text(file_path:str):
    """
    Extracts text, tone, and calculates a 'User Confidence Score' 
    combining AI certainty, volume, and clarity.
    """
    
    result = whisper_model.transcribe(file_path)
    text = result['text'].strip()
    
    # Convert average logprob of segments to a 0-1 confidence scale
    avg_logprob = np.mean([s['avg_logprob'] for s in result['segments']])
    ai_confidence = np.exp(avg_logprob) 

    emotions = emotion_classifier(file_path)
    top_tone = emotions[0] # Best match (e.g., 'neutral', 'happy')

    y, sr = librosa.load(file_path)
    
    # Clarity: Spectral Centroid (Higher = crisper/brighter speech)
    # We normalize against 3000Hz as a "clear" benchmark
    raw_clarity = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    clarity_norm = min(raw_clarity / 3000, 1.0)
    
    # Volume: RMS Energy (Higher = stronger projection)
    # We normalize against 0.05 as a "solid" volume benchmark
    raw_volume = np.mean(librosa.feature.rms(y=y))
    volume_norm = min(raw_volume / 0.05, 1.0)

    # Weighting: 50% AI Certainty, 30% Volume Projection, 20% Clarity
    word_count = len(text.split())
    effort_score = min(word_count / 15, 1.0)
    # Final Kid-Optimized Score
    final_score = (ai_confidence * 0.40) + (effort_score * 0.30) + (volume_norm * 0.20) + (clarity_norm * 0.10)

    final_score_pct = round(final_score * 100, 2)

    # Interpret the score: Threshold is made kid friendly.
    if final_score > 0.75: # Lowered threshold: kids are rarely 85%+ on adult models
        status = "Super Star! Very Confident & Expressive"
    elif final_score > 0.45: # Lowered threshold: 0.45 is a solid 'passing' effort for a child
        status = "Great Effort! Keep Sharing Your Thoughts"
    else:
        status = "Quiet or Thinking? Try Speaking Up a Little More"

    response = {
        "prompt":"This is a audio input given by the user you are given tone, tone intensity, user confidence and other metrics according go through these metrics and return user your feedback along with the next question.",
        "text": text,
        "detected_tone": top_tone['label'],
        "tone_intensity": round(top_tone['score'], 2),
        "user_confidence_score": f"{final_score_pct}%",
        "assessment": status,
        "metrics": {
            "ai_certainty": round(ai_confidence, 2),
            "volume_level": round(volume_norm, 2),
            "vocal_clarity": round(clarity_norm, 2)
        }
    }

    print(f"Result: {response['assessment']} | Score: {response['user_confidence_score']}")
    return response

