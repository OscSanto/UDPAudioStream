"""
sender.py
-Captures system audio (Windows:WASAPI loopback)
-Chunks it into small frames
-Sends frames(link) via UDP to the receiver's IP:PORT

no compression, no encrptyion, no discovery(?)
"""

import socket
import struct
import os

import socket
import sounddevice as sd
import numpy as np
import time
import struct
import os
import sys
import pyaudiowpatch as pyaudio

# ------------SETTINGS------------
DEST_IP = "192.168.0.159"
DEST_PORT = 3001

SAMPLE_RATE = 48000  # Hz
# CHANNELS = 2         # stereo
FRAME_DURATION = 20  # ms
SAMPLES = SAMPLE_RATE * FRAME_DURATION // 1000
FORMAT = pyaudio.paInt16  # 16-bit PCM
# -------------------------------


def main():
    dest_ip = os.environ.get("DEST_IP", DEST_IP)
    dest_port = os.environ.get("DEST_PORT", DEST_PORT)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket using IPv4 protocol and UDP transport layer
    seq = 0 # Sequence number (0-65535) for each packet (rolls over) 
    timestamp_ms = 0 # Timestamp in ms (for reference; not used by receiver) 

    # Initialize PyAudio with WASAPI loopback capture device 
    # query available devices with p.get_device_info_by_index(i)
    p = pyaudio.PyAudio()

    try:
        # Get default WASAPI info
        wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
        # Get default output device (speakers)
        default_speakers = p.get_device_info_by_index(
            wasapi_info["defaultOutputDevice"]
        )

        
        # Find the loopback device for those speakers
        if not default_speakers["isLoopbackDevice"]:
            for loopback in p.get_loopback_device_info_generator():
                # Match by name
                if default_speakers["name"] in loopback["name"]:
                    default_speakers = loopback
                    break
            else:
                print("Could not find loopback device. Available loopback devices:")
                for loopback in p.get_loopback_device_info_generator():
                    print(f"  - {loopback['name']}")
                raise RuntimeError("No loopback device found")
        
        print(f"Capturing from: {default_speakers['name']}")
        print(f"Channels: {default_speakers['maxInputChannels']}")
        print(f"Sample rate: {int(default_speakers['defaultSampleRate'])} Hz")
        print(f"Sending to {dest_ip}:{dest_port}")
        print("Press Ctrl+C to stop.\n")

        # Open the loopback stream
        stream = p.open(
            format=FORMAT,
            channels=default_speakers["maxInputChannels"], # usually stereo (2) or mono (1)
            rate=int(default_speakers["defaultSampleRate"]), # usually 48000 Hz 
            input=True,
            frames_per_buffer=SAMPLES,
            input_device_index=default_speakers["index"]
        )

        # Capture and send loop
        while True:
            data = stream.read(SAMPLES, exception_on_overflow=False) # Read a chunk of audio data from the stream, exception_on_overflow=False to prevent overflow
            header = struct.pack("!HI", seq, timestamp_ms) # Pack sequence number and timestamp into binary format (big-endian)
            sock.sendto(header + data, (dest_ip, dest_port)) # Send the packet via UDP to the destination IP and port
            print(f"Sent packet seq={seq}, timestamp={timestamp_ms}ms, size)={len(data)+6} bytes") # Print packet info, 6 bytes for header (2 for seq, 4 for timestamp)
            
            seq = (seq + 1) % 65536 # Wrap sequence number at 65536. Use & 0xFFFF for slightly faster wrap-around (me: how does 0xFFFF work?)
            timestamp_ms += (SAMPLES * 1000) // SAMPLE_RATE

    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        print(f"Error: {e}")
        print("\nAvailable devices:")
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            print(f"[{i}] {dev['name']}")
            print(f"     Inputs: {dev['maxInputChannels']}, Outputs: {dev['maxOutputChannels']}")
        sys.exit(1)
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()
        sock.close()


if __name__ == "__main__":
    main()