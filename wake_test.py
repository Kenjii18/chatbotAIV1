import os
import time
import numpy as np
import sounddevice as sd
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from openai import OpenAI
from dotenv import load_dotenv


# =========================================================
# CONFIG
# =========================================================

MIC_DEVICE = 1

MIC_RATE = 44100
STT_RATE = 16000

FRAME_MS = 30
FRAME_SIZE = int(MIC_RATE * FRAME_MS / 1000)

# VAD
SPEECH_THRESHOLD = 0.008
SILENCE_TIME = 0.7
MAX_RECORD_TIME = 60

# DeepSeek
DEEPSEEK_MODEL = "deepseek-v4-flash"


# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    raise RuntimeError(
        "❌ Không tìm thấy DEEPSEEK_API_KEY trong file .env"
    )


# =========================================================
# LOAD WHISPER
# =========================================================

print("🌙 Đang tải Moon STT...")

model = WhisperModel(
    "large-v3-turbo",
    device="cpu",
    compute_type="int8"
)

print("✅ Moon STT đã sẵn sàng.")


# =========================================================
# LOAD DEEPSEEK
# =========================================================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

print("✅ DeepSeek đã sẵn sàng.")
print()


# =========================================================
# LISTEN UNTIL SILENCE
# =========================================================

def listen_until_silence():

    print("🎙️ Moon đang nghe...", flush=True)

    frames = []
    speaking = False
    silence_frames = 0

    silence_limit = int(
        SILENCE_TIME / (FRAME_MS / 1000)
    )

    start_time = time.time()

    try:

        with sd.InputStream(
            device=MIC_DEVICE,
            samplerate=MIC_RATE,
            channels=1,
            dtype="float32",
            blocksize=FRAME_SIZE
        ) as stream:

            while True:

                data, overflowed = stream.read(FRAME_SIZE)

                if overflowed:
                    continue

                audio = data[:, 0]

                # Tính âm lượng
                rms = np.sqrt(
                    np.mean(audio ** 2)
                )

                # =========================================
                # BOSS ĐANG NÓI
                # =========================================

                if rms >= SPEECH_THRESHOLD:

                    if not speaking:
                        print("🟢 Boss bắt đầu nói...")

                    speaking = True
                    silence_frames = 0

                    frames.append(audio.copy())

                # =========================================
                # IM LẶNG
                # =========================================

                else:

                    if speaking:

                        # Giữ lại phần đuôi âm thanh
                        frames.append(audio.copy())

                        silence_frames += 1

                        if silence_frames >= silence_limit:
                            break

                # =========================================
                # MAX RECORD TIME
                # =========================================

                if time.time() - start_time >= MAX_RECORD_TIME:

                    print("⏱️ Đạt giới hạn 60 giây.")

                    break

    except Exception as e:

        print(f"❌ Lỗi microphone: {e}")

        return None

    if not frames:
        return None

    # Ghép toàn bộ audio
    audio = np.concatenate(frames)

    duration = len(audio) / MIC_RATE

    print(
        f"🛑 Boss nói xong "
        f"({duration:.2f} giây)"
    )

    # 44.1kHz → 16kHz
    audio_16k = resample_poly(
        audio,
        STT_RATE,
        MIC_RATE
    ).astype(np.float32)

    return audio_16k


# =========================================================
# WHISPER
# =========================================================

def speech_to_text(audio):

    print("🧠 Moon đang nhận dạng...")

    segments, info = model.transcribe(
        audio,
        language="vi",
        beam_size=1,
        vad_filter=True
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
        if segment.text.strip()
    ).strip()

    return text


# =========================================================
# WAKE WORD
# =========================================================

def is_wake_word(text):

    text = text.lower().strip()

    # Chuẩn hóa dấu câu
    clean_text = (
        text
        .replace(",", " ")
        .replace(".", " ")
        .replace("!", " ")
        .replace("?", " ")
    )

    clean_text = " ".join(
        clean_text.split()
    )

    # Alo alo
    if "alo alo" in clean_text:
        return True

    # Cho phép Whisper nhận thành "alo"
    if clean_text == "alo":
        return True

    return False


# =========================================================
# DEEPSEEK
# =========================================================

def ask_deepseek(text):

    print("🤖 Moon đang suy nghĩ...")

    try:

        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "Bạn là Moon, trợ lý AI nói tiếng Việt. "
                        "Gọi người dùng là Boss. "
                        "Xưng là Em. "
                        "Trả lời tự nhiên, thân thiện, "
                        "ngắn gọn và có chút hài hước."
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],

            stream=False,

            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }
        )

        answer = response.choices[0].message.content

        if not answer:
            return "Em chưa nghĩ ra câu trả lời, Boss ạ 😅"

        return answer.strip()

    except Exception as e:

        print(f"❌ Lỗi DeepSeek: {e}")

        return "Boss ơi, em bị lỗi kết nối DeepSeek rồi 😭"


# =========================================================
# MAIN
# =========================================================

print("===================================")
print("🌙 MOON - VOICE CHAT TEST")
print("===================================")
print()
print("Wake Word: Alo alo")
print()
print("🛑 Nhấn Ctrl+C để thoát.")
print()


try:

    while True:

        # =================================================
        # MOON NGỦ
        # =================================================

        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("😴 Moon đang ngủ...")
        print("🎙️ Nói: Alo alo")
        print()


        # =================================================
        # CHỜ WAKE WORD
        # =================================================

        while True:

            audio = listen_until_silence()

            if audio is None:
                continue

            text = speech_to_text(audio)

            if not text:
                continue

            print(f"🗣️ Boss: {text}")

            if is_wake_word(text):

                break

            print("😴 Không phải Wake Word.")
            print()


        # =================================================
        # MOON THỨC
        # =================================================

        print()
        print("🟢 ===============================")
        print("🟢 MOON ĐÃ THỨC!")
        print("🟢 ===============================")
        print()
        print("🌙 Moon: Em đây, Boss nói đi 😏")
        print()


        # =================================================
        # MOON GIỮ TRẠNG THÁI THỨC
        # =================================================

        while True:

            command_audio = listen_until_silence()

            if command_audio is None:
                continue

            command_text = speech_to_text(
                command_audio
            )

            if not command_text:

                print("🤷 Moon không nghe rõ.")
                print()

                continue


            # =============================================
            # HIỂN THỊ CÂU BOSS
            # =============================================

            print()
            print(f"🗣️ Boss: {command_text}")
            print()


            # =============================================
            # GỌI DEEPSEEK
            # =============================================

            answer = ask_deepseek(
                command_text
            )


            # =============================================
            # MOON TRẢ LỜI
            # =============================================

            print()
            print(f"🌙 Moon: {answer}")
            print()


except KeyboardInterrupt:

    print()
    print("🌙 Moon: Tạm biệt Boss! Hẹn gặp lại nhé. 👋")
    print("🛑 Moon đã dừng.")