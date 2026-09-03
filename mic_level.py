import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 16000
FRAME_MS = 100
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

print("================================")
print("      🌙 MOON MIC LEVEL")
print("================================")
print()
print("Để mic yên, KHÔNG nói trong 5 giây...")
print()

time.sleep(2)

levels = []

for i in range(50):

    audio = sd.rec(
        FRAME_SAMPLES,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    samples = audio.astype(np.float32)

    rms = np.sqrt(np.mean(samples ** 2))

    levels.append(rms)

    print(f"\rMic level: {rms:8.1f}", end="", flush=True)

print()

noise_avg = np.mean(levels)
noise_max = np.max(levels)

print()
print(f"📊 Noise trung bình : {noise_avg:.1f}")
print(f"📊 Noise cao nhất   : {noise_max:.1f}")
print()
print("Bây giờ Boss nói một câu trong 3 giây...")
print()

time.sleep(2)

levels_speech = []

for i in range(30):

    audio = sd.rec(
        FRAME_SAMPLES,
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    samples = audio.astype(np.float32)

    rms = np.sqrt(np.mean(samples ** 2))

    levels_speech.append(rms)

    print(f"\rMic level: {rms:8.1f}", end="", flush=True)

print()

speech_avg = np.mean(levels_speech)
speech_max = np.max(levels_speech)

print()
print(f"🎙️ Speech trung bình : {speech_avg:.1f}")
print(f"🎙️ Speech cao nhất   : {speech_max:.1f}")
print()