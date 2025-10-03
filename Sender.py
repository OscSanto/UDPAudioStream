"""
sender.py
-Captures system audio (Windows:WASAPI loopback)
-Chunks it into small frames
-Sends frames(link) via UDP to the receiver's IP:PORT

no compression, no encrptyion, no discovery(?)
"""

import socket
import sounddevice as sd
import numpy as np
import time
import struct
import os

# ------------SETTINGS------------
DEST_IP = "127.0.0.1"
DEST_PORT = 3001

SAMPLE_RATE = 48000  # Hertz
CHANNELS = 2  # Stereo
FRAME_DURATION = 20  # ms (20ms = 480 samples), 20 ms per packet (good for low latency) (good latency)
SAMPLES = SAMPLE_RATE * FRAME_DURATION // 1000  # Samples per frame
BUFFER_SIZE = SAMPLES * CHANNELS * 2  # 2 bytes per sample (16-bit audio)
DTYPE = "int16"  # 16-bit PCM (2 bytes per sample)


# --------------------------


"""


"""
def main():
    # Create UDP socket to send packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Sequence number and timestamp
    seq = 0
    timestamp = 0

    # Audio callback function for sounddevice InputStream with WASAPI loopback mode enabled (Windows only) 
    extra = sd.WasapiSettings(loopback=True) if hasattr(sd, "WasapiSettings") else None

    # Open an input stream from the "default" input device
    with sd.InputStream(
        samplerate=SAMPLE_RATE, # Hertz
        channels=CHANNELS, # 2 channels (stereo)
        dtype=DTYPE, # 16-bit PCM
        blocksize=SAMPLES,           # ask the OS to give us FRAME_MS chunks
        extra_settings=extra
    ) as stream:
        print(f"Sending audio to {DEST_IP}:{DEST_PORT}")
        print("Press Ctrl+C to stop.")

        while True:
            # Read audio data from stream
            # Get audio data
            frames, overflowed = stream.read(SAMPLES) # shape = (SAMPLES, CHANNELS)

            payload = frames.tobytes() # length = SAMPLES * CHANNELS * 2 bytes

            # Create header (sequence number and timestamp)
            header = struct.pack("!HI", seq, timestamp)

            # Send packet
            sock.sendto(header + payload, (DEST_IP, DEST_PORT))
            
            # Increment sequence number and timestamp
            seq = (seq + 1) % 65536  # Wrap around at 65536
            timestamp += SAMPLES * 1000 // SAMPLE_RATE
        

if __name__ == "__main__":

    DEST_IP = os.environ.get("DEST_IP", DEST_IP)
    try:   
        main()
    except KeyboardInterrupt:
        print("\nExiting...")