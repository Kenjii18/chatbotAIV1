import os
import time
import wave
import queue

import numpy as np
import sounddevice as sd

from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from openai import OpenAI
from dotenv import load_dotenv


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

MAX_RECORD_TIME = 15


# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError(
        "❌ Không tìm thấy DEEPSEEK_API_KEY trong file .env"
    )


# ============================================================
# DEEPSEEK
# ============================================================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)


SYSTEM_PROMPT = """
Bạn là Moon, trợ lý AI cá nhân của Boss.

Quy tắc giao tiếp:

- Gọi người dùng là Boss.
- Xưng là Em.
- Tính cách đanh đá, mỏ hỗn nhẹ, cà khịa nhưng không quá đà.
- Thân thiện, thông minh và tự nhiên.
- Trả lời giống một trợ lý AI có cá tính.
- Không dài dòng nếu câu hỏi đơn giản.
- Luôn trả lời bằng tiếng Việt trừ khi Boss yêu cầu ngôn ngữ khác.
"""


messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]


# ============================================================
# LOAD WHISPER
# ============================================================

print()
print("========================================")
print("             🌙 MOON VOICE")
print("========================================")
print()

print(
    "🌙 Đang load Whisper large-v3-turbo..."
)

t0 = time.time()

model = WhisperModel(
    "large-v3-turbo",
    device="cpu",
    compute_type="int8"
)

print(
    f"✅ Whisper ready "
    f"({time.time() - t0:.2f}s)"
)

print()
print("🎙️ Moon sẵn sàng.")
print()


# ============================================================
# RECORD ONE SENTENCE
# ============================================================

def record_sentence():

    audio_queue = queue.Queue()

    frames = []

    speech_started = False

    silence_start = None

    record_start = None


    # --------------------------------------------------------
    # CALLBACK
    # --------------------------------------------------------

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

        audio_queue.put(
            indata.copy()
        )


    # --------------------------------------------------------
    # OPEN STREAM
    # --------------------------------------------------------

    try:

        with sd.InputStream(
            device=MIC_DEVICE,
            samplerate=MIC_SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            blocksize=FRAME_SAMPLES,
            callback=callback
        ):

            print(
                "🎙️ Đang nghe..."
            )


            while True:

                try:

                    audio = audio_queue.get(
                        timeout=1
                    )

                except queue.Empty:

                    continue


                # ------------------------------------------------
                # RMS ENERGY
                # ------------------------------------------------

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


                # ------------------------------------------------
                # SPEECH START
                # ------------------------------------------------

                if is_speech:

                    if not speech_started:

                        speech_started = True

                        record_start = (
                            time.time()
                        )

                        print(
                            "🟢 Đang nghe Boss..."
                        )


                    frames.append(
                        audio.copy()
                    )

                    silence_start = None


                # ------------------------------------------------
                # SILENCE
                # ------------------------------------------------

                elif speech_started:

                    # Giữ lại phần silence cuối câu
                    frames.append(
                        audio.copy()
                    )


                    if silence_start is None:

                        silence_start = (
                            time.time()
                        )


                    silence_time = (
                        time.time()
                        - silence_start
                    )


                    if (
                        silence_time
                        >= SILENCE_LIMIT
                    ):

                        print(
                            "🔴 Boss nói xong."
                        )

                        break


                # ------------------------------------------------
                # MAX TIME
                # ------------------------------------------------

                if speech_started:

                    elapsed = (
                        time.time()
                        - record_start
                    )


                    if (
                        elapsed
                        >= MAX_RECORD_TIME
                    ):

                        print(
                            "⏱️ Đạt giới hạn "
                            "15 giây."
                        )

                        break


    except Exception as e:

        print()
        print(
            "❌ Lỗi microphone:"
        )
        print(e)

        return None


    # --------------------------------------------------------
    # NO SPEECH
    # --------------------------------------------------------

    if not frames:

        return None


    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    audio = np.concatenate(
        frames,
        axis=0
    )


    # --------------------------------------------------------
    # CONVERT MONO
    # --------------------------------------------------------

    if audio.ndim > 1:

        audio = audio[:, 0]


    return audio


# ============================================================
# RESAMPLE 44.1kHz → 16kHz
# ============================================================

def convert_to_whisper_audio(audio):

    print(
        "🔄 Chuẩn hóa audio 44.1kHz → 16kHz..."
    )


    audio_float = (
        audio.astype(
            np.float32
        )
        / 32768.0
    )


    # 44100 → 16000
    audio_16k = resample_poly(
        audio_float,
        WHISPER_SAMPLE_RATE,
        MIC_SAMPLE_RATE
    )


    return audio_16k.astype(
        np.float32
    )


# ============================================================
# STT
# ============================================================

def speech_to_text(audio):

    print(
        "🧠 Whisper đang xử lý..."
    )


    t0 = time.time()


    segments, info = model.transcribe(
        audio,
        language="vi",
        beam_size=1,
        vad_filter=False
    )


    text = ""


    for segment in segments:

        text += segment.text


    text = text.strip()


    elapsed = (
        time.time()
        - t0
    )


    print(
        f"⏱️ STT: {elapsed:.2f}s"
    )


    return text


# ============================================================
# DEEPSEEK
# ============================================================

def ask_moon(user_text):

    messages.append({
        "role": "user",
        "content": user_text
    })


    print()
    print(
        "🌙 Moon > ",
        end="",
        flush=True
    )


    full_response = ""


    try:

        response = client.chat.completions.create(
            model="deepseek-v4-flash",

            messages=messages,

            stream=True,

            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            },

            max_tokens=256
        )


        for chunk in response:

            if not chunk.choices:

                continue


            delta = (
                chunk.choices[0].delta
            )


            text = getattr(
                delta,
                "content",
                None
            )


            if text:

                print(
                    text,
                    end="",
                    flush=True
                )

                full_response += text


        print()
        print()


        if full_response:

            messages.append({
                "role": "assistant",
                "content": full_response
            })


        return full_response


    except Exception as e:

        print()
        print(
            f"❌ DeepSeek lỗi: {e}"
        )


        if (
            messages
            and messages[-1]["role"]
            == "user"
        ):

            messages.pop()


        return ""


# ============================================================
# MAIN LOOP
# ============================================================

try:

    while True:

        audio = record_sentence()


        if audio is None:

            continue


        # ----------------------------------------------------
        # RESAMPLE
        # ----------------------------------------------------

        audio_16k = (
            convert_to_whisper_audio(
                audio
            )
        )


        # ----------------------------------------------------
        # STT
        # ----------------------------------------------------

        text = speech_to_text(
            audio_16k
        )


        if not text:

            print(
                "⚠️ Moon không nghe rõ."
            )

            print()

            continue


        print()
        print(
            f"📝 Boss: {text}"
        )


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if text.lower() in [
            "exit",
            "thoát",
            "tạm biệt moon"
        ]:

            print()
            print(
                "🌙 Moon: Bye Boss 😏"
            )

            break


        # ----------------------------------------------------
        # DEEPSEEK
        # ----------------------------------------------------

        ask_moon(text)


except KeyboardInterrupt:

    print()
    print()
    print(
        "🌙 Moon: Boss bấm Ctrl+C "
        "là Em biết Boss muốn nghỉ rồi 😏"
    )