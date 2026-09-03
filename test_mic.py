import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 5
OUTPUT_FILE = "test.wav"

print("🎙️ Moon đang nghe...")
print("👉 Nói trong 5 giây!")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16"
)

sd.wait()

write(
    OUTPUT_FILE,
    SAMPLE_RATE,
    audio
)

print()
print(f"✅ Đã thu âm xong: {OUTPUT_FILE}")