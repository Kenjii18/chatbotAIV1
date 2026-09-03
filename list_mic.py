import sounddevice as sd

print("================================")
print("       🌙 MOON MICROPHONES")
print("================================")
print()

devices = sd.query_devices()

for i, device in enumerate(devices):
    print(f"[{i}] {device['name']}")
    print(f"    Input : {device['max_input_channels']}")
    print(f"    Output: {device['max_output_channels']}")
    print(f"    Rate  : {device['default_samplerate']}")
    print()