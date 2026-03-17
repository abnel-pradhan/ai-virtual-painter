import mediapipe
import os

print("\n" + "="*30)
print("🕵️ DETECTIVE REPORT 🕵️")
print("="*30)

# This tells us exactly where Python is pulling 'mediapipe' from
if hasattr(mediapipe, '__file__'):
    print(f"I found mediapipe at:\n➡️ {mediapipe.__file__}")
else:
    print("I found a 'mediapipe' folder, but it has no file (It is a namespace package).")
    print(f"Look inside: {os.getcwd()}")

print("="*30 + "\n")