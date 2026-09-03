from faster_whisper import WhisperModel
import os
import time

# ==============================
# FILE VAD MỚI NHẤT
# ==============================

AUDIO_FILE = "vad_test.wav"

if not os.path.exists(AUDIO_FILE):
    raise FileNotFoundError(
        f"❌ Không tìm thấy {AUDIO_FILE}"
    )

print("================================")
print("       🌙 MOON STT TEST")
print("================================")
print()

print(f"🎵 Audio: {os.path.abspath(AUDIO_FILE)}")
print()


# ==============================
# LOAD WHISPER
# ==============================

print("🌙 Loading Whisper...")

t0 = time.time()

model = WhisperModel(
    "large-v3-turbo",
    device="cpu",
    compute_type="int8"
)

print(
    f"✅ Model loaded: "
    f"{time.time() - t0:.2f}s"
)

print()


# ==============================
# TRANSCRIBE
# ==============================

print("🎙️ Transcribing...")

t1 = time.time()

segments, info = model.transcribe(
    AUDIO_FILE,
    language="vi",
    beam_size=1,
    vad_filter=True
)


text = ""

for segment in segments:

    text += segment.text


text = text.strip()

t2 = time.time()


# ==============================
# RESULT
# ==============================

print()
print("📝 Boss nói:")
print(text)

print()

print(
    f"⏱️ Thời gian STT: "
    f"{t2 - t1:.2f}s"
)

print()