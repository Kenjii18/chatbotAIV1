import sounddevice as sd
import numpy as np
import openwakeword
from openwakeword.model import Model
from scipy.signal import resample_poly


# ==============================
# CẤU HÌNH
# ==============================

MIC_DEVICE = 9       # Microphone Array - WASAPI
MIC_RATE = 48000     # Mic Windows chạy native 48 kHz
WAKE_RATE = 16000    # OpenWakeWord cần 16 kHz

CHANNELS = 1
BLOCK_SIZE = 480     # 10 ms ở 48 kHz

THRESHOLD = 0.20


# ==============================
# LOAD MODEL
# ==============================

print("⏳ Đang tải OpenWakeWord...")

model_path = (
    r"C:\Users\Admin\Documents\Moon\.venv\Lib\site-packages"
    r"\openwakeword\resources\models\hey_jarvis_v0.1.tflite"
)

model = Model(
    wakeword_models=[model_path]
)

print("✅ Wake-word model đã sẵn sàng!")
print("😴 Moon đang ngủ...")
print("👉 Hãy nói: Hey Jarvis")
print()


# ==============================
# CALLBACK MICROPHONE
# ==============================

def callback(indata, frames, time, status):

    if status:
        print("⚠️ Audio:", status)

    # Lấy mono channel
    audio = indata[:, 0]

    # ==========================
    # 48 kHz → 16 kHz
    # ==========================

    audio_16k = resample_poly(
        audio,
        WAKE_RATE,
        MIC_RATE
    )

    # float32 → int16
    audio_16k = (
        audio_16k * 32767
    ).astype(np.int16)

    # ==========================
    # OPENWAKEWORD
    # ==========================

    prediction = model.predict(audio_16k)

    score = float(
        prediction.get("hey_jarvis_v0.1", 0)
    )

    # Chỉ in khi score đáng chú ý
    if score > 0.01:
        print(f"Wake score: {score:.4f}")

    # ==========================
    # WAKE
    # ==========================

    if score >= THRESHOLD:
        print()
        print("🟢 ===========================")
        print("🟢 HEY JARVIS ĐƯỢC PHÁT HIỆN!")
        print(f"🟢 Score: {score:.4f}")
        print("🟢 ===========================")
        print()


# ==============================
# START MICROPHONE
# ==============================

try:

    with sd.InputStream(
        device=MIC_DEVICE,
        samplerate=MIC_RATE,
        channels=CHANNELS,
        dtype="float32",
        blocksize=BLOCK_SIZE,
        callback=callback
    ):

        while True:
            sd.sleep(1000)


except KeyboardInterrupt:

    print()
    print("🛑 Moon đã đi ngủ.")


except Exception as e:

    print()
    print("❌ Lỗi microphone:")
    print(e)