import sounddevice as sd
import numpy as np
import time

from faster_whisper import WhisperModel
from scipy.signal import resample_poly


# ============================================================
# CONFIG
# ============================================================

MIC_DEVICE = 1

MIC_SAMPLE_RATE = 44100
WHISPER_SAMPLE_RATE = 16000

CHANNELS = 1

FRAME_MS = 30

FRAME_SAMPLES = int(
    MIC_SAMPLE_RATE * FRAME_MS / 1000
)

ENERGY_THRESHOLD = 500

SILENCE_LIMIT = 0.8

MAX_RECORD_TIME = 3


# ============================================================
# LOAD WHISPER
# ============================================================

print()
print("========================================")
print("        🌙 MON WAKE WORD TEST")
print("========================================")
print()

print("🌙 Đang load Whisper...")

model = WhisperModel(
    "large-v3-turbo",
    device="cpu",
    compute_type="int8"
)

print("✅ Whisper ready")
print()

print("😴 MON đang ngủ.")
print('👉 Gọi: "Mon"')
print()


# ============================================================
# RECORD
# ============================================================

def record_audio():

    audio_buffer = []

    frames = []

    speech_started = False

    silence_start = None

    record_start = None


    def callback(
        indata,
        frames_count,
        time_info,
        status
    ):

        if status:
            print(
                f"\n⚠️ Audio: {status}"
            )

        audio_buffer.append(
            indata.copy()
        )


    try:

        with sd.InputStream(
            device=MIC_DEVICE,
            samplerate=MIC_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            callback=callback
        ):

            while True:

                if not audio_buffer:

                    time.sleep(0.005)

                    continue


                audio = audio_buffer.pop(0)


                # ============================================
                # RMS
                # ============================================

                samples = audio.astype(
                    np.float32
                )

                energy = float(
                    np.sqrt(
                        np.mean(
                            samples ** 2
                        )
                    )
                )


                is_speech = (
                    energy > ENERGY_THRESHOLD
                )


                # ============================================
                # CHƯA PHÁT HIỆN GIỌNG
                # ============================================

                if not speech_started:

                    if is_speech:

                        speech_started = True

                        record_start = time.time()

                        frames.append(
                            audio.copy()
                        )

                    continue


                # ============================================
                # ĐANG GHI
                # ============================================

                frames.append(
                    audio.copy()
                )


                if is_speech:

                    silence_start = None

                else:

                    if silence_start is None:

                        silence_start = time.time()


                    silence_time = (
                        time.time()
                        - silence_start
                    )


                    if silence_time >= SILENCE_LIMIT:

                        break


                # ============================================
                # MAX TIME
                # ============================================

                elapsed = (
                    time.time()
                    - record_start
                )


                if elapsed >= MAX_RECORD_TIME:

                    break


    except Exception as e:

        print(
            f"\n❌ Microphone lỗi: {e}"
        )

        return None


    if not frames:

        return None


    audio = np.concatenate(
        frames,
        axis=0
    )


    if audio.ndim > 1:

        audio = audio[:, 0]


    return audio


# ============================================================
# WHISPER
# ============================================================

def recognize(audio):

    # --------------------------------------------------------
    # 44.1kHz → 16kHz
    # --------------------------------------------------------

    audio_float = (
        audio.astype(
            np.float32
        )
        / 32768.0
    )


    audio_16k = resample_poly(
        audio_float,
        WHISPER_SAMPLE_RATE,
        MIC_SAMPLE_RATE
    )


    # --------------------------------------------------------
    # STT
    # --------------------------------------------------------

    segments, info = model.transcribe(
        audio_16k,
        language="vi",
        beam_size=1,
        vad_filter=False
    )


    text = ""

    for segment in segments:

        text += segment.text


    return text.strip()


# ============================================================
# CHECK MON
# ============================================================

def is_mon(text):

    text = text.lower().strip()

    # Xóa một số dấu câu
    text = (
        text
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .strip()
    )


    # --------------------------------------------------------
    # CHỈ CHẤP NHẬN "MON"
    # --------------------------------------------------------

    if text == "mon":
        return True


    # Ví dụ:
    # "mon ơi"
    # "mon oi"
    # "mon à"

    words = text.split()

    if len(words) >= 1:

        if words[0] == "mon":

            return True


    return False


# ============================================================
# MAIN
# ============================================================

while True:

    try:

        audio = record_audio()


        if audio is None:

            continue


        print(
            "🧠 Kiểm tra..."
        )


        text = recognize(
            audio
        )


        if not text:

            print(
                "😴 Không nghe rõ."
            )

            print()

            continue


        print(
            f"📝 Nghe được: {text}"
        )


        # ====================================================
        # MON DETECTED
        # ====================================================

        if is_mon(text):

            print()
            print(
                "🟢 MON ĐÃ THỨC!"
            )

            print(
                "🌙 Boss gọi Em đấy à? 😏"
            )

            print()


            time.sleep(1)


            print(
                "😴 MON quay lại ngủ."
            )

            print()


        else:

            print(
                "😴 Không phải wake word."
            )

            print()


    except KeyboardInterrupt:

        print()
        print(
            "🌙 MON: Bye Boss 😏"
        )

        break