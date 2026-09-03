import sounddevice as sd
import numpy as np
import wave
import time

# ==============================
# CONFIG
# ==============================

MIC_DEVICE = 1

SAMPLE_RATE = 44100
CHANNELS = 1

FRAME_MS = 30
FRAME_SAMPLES = int(
    SAMPLE_RATE * FRAME_MS / 1000
)

ENERGY_THRESHOLD = 500

SILENCE_LIMIT = 0.8
MAX_RECORD_TIME = 15


# ==============================
# RMS
# ==============================

def get_energy(audio):

    samples = audio.astype(np.float32)

    return float(
        np.sqrt(np.mean(samples ** 2))
    )


# ==============================
# START
# ==============================

print("================================")
print("       🌙 MOON VAD TEST")
print("================================")
print()

print(f"🎙️ Microphone device: {MIC_DEVICE}")
print(f"🎵 Sample rate: {SAMPLE_RATE}")
print()

print("🎙️ Đang chờ Boss nói...")


frames = []

speech_started = False
silence_start = None
record_start = None


# ==============================
# CALLBACK
# ==============================

audio_buffer = []


def callback(indata, frames_count, time_info, status):

    if status:
        print(
            f"\n⚠️ Audio status: {status}"
        )

    audio_buffer.append(
        indata.copy()
    )


# ==============================
# OPEN ONE STREAM
# ==============================

try:

    with sd.InputStream(
        device=MIC_DEVICE,
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=FRAME_SAMPLES,
        callback=callback
    ):

        while True:

            # Chờ callback có dữ liệu
            if not audio_buffer:
                time.sleep(0.005)
                continue


            audio = audio_buffer.pop(0)


            # ======================
            # ENERGY
            # ======================

            energy = get_energy(audio)


            print(
                f"\rMic level: {energy:8.1f}",
                end="",
                flush=True
            )


            is_speech = (
                energy > ENERGY_THRESHOLD
            )


            # ======================
            # SPEECH START
            # ======================

            if is_speech:

                if not speech_started:

                    speech_started = True

                    record_start = time.time()

                    print()

                    print(
                        "🟢 Đã phát hiện Boss nói!"
                    )

                frames.append(
                    audio.tobytes()
                )

                silence_start = None


            # ======================
            # SILENCE
            # ======================

            elif speech_started:

                frames.append(
                    audio.tobytes()
                )

                if silence_start is None:

                    silence_start = time.time()


                silence_time = (
                    time.time()
                    - silence_start
                )


                if silence_time >= SILENCE_LIMIT:

                    print()

                    print(
                        "🔴 Boss đã nói xong."
                    )

                    break


            # ======================
            # MAX TIME
            # ======================

            if speech_started:

                elapsed = (
                    time.time()
                    - record_start
                )

                if elapsed >= MAX_RECORD_TIME:

                    print()

                    print(
                        "⏱️ Đạt giới hạn 15 giây."
                    )

                    break


except Exception as e:

    print()
    print("❌ Lỗi microphone:")
    print(e)

    raise SystemExit


# ==============================
# SAVE WAV
# ==============================

if not frames:

    print()
    print(
        "⚠️ Không phát hiện tiếng nói."
    )

    raise SystemExit


output_file = "vad_test.wav"


with wave.open(
    output_file,
    "wb"
) as wf:

    wf.setnchannels(CHANNELS)

    wf.setsampwidth(2)

    wf.setframerate(SAMPLE_RATE)

    wf.writeframes(
        b"".join(frames)
    )


print()
print(
    f"✅ Đã lưu: {output_file}"
)
print()