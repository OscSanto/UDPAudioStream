"""
receiver.py
- Listens on UDP port for 20 ms stereo int16 PCM frames
- Very simple jitter buffer: prebuffer a few packets, then play in seq order
- Missing packets are replaced with silence (to keep timing steady)
"""

import socket
import struct
import numpy as np
import sounddevice as sd

# -------- SETTINGS --------
LISTEN_IP   = "0.0.0.0"                 # listen on all interfaces
LISTEN_PORT = int(os.environ.get("LISTEN_PORT", "3001"))

SAMPLE_RATE = 48000
CHANNELS    = 2
FRAME_MS    = 20
SAMPLES     = SAMPLE_RATE * FRAME_MS // 1000
DTYPE       = "int16"

TARGET_BUFFER_PACKETS = 5   # ~5 * 20ms = ~100ms prebuffer (raise if crackles; lower for less lag)
# --------------------------

def main():
    # Playback stream
    out = sd.OutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=SAMPLES
    )
    out.start()

    # UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    sock.settimeout(0.5)

    print(f"Listening on {LISTEN_IP}:{LISTEN_PORT} (press Ctrl+C to stop)")

    # Tiny jitter buffer keyed by sequence number
    buffer = {}            # seq -> payload(bytes)
    play_started = False
    expected_seq = None

    bytes_per_sample = 2
    frame_bytes = SAMPLES * CHANNELS * bytes_per_sample
    silence = (np.zeros((SAMPLES, CHANNELS), dtype=DTYPE)).tobytes()

    try:
        while True:
            # Receive one datagram (non-blocking with timeout)
            try:
                pkt, addr = sock.recvfrom(65535)
            except socket.timeout:
                pkt = None

            if pkt:
                # Header = seq:uint16 + ts:uint32
                if len(pkt) >= 6:
                    seq, ts = struct.unpack("!HI", pkt[:6])
                    payload = pkt[6:]

                    # Only accept exactly one frame worth of audio
                    if len(payload) == frame_bytes:
                        buffer[seq] = payload

                # Start playback after we have a few packets queued
                if not play_started and len(buffer) >= TARGET_BUFFER_PACKETS:
                    expected_seq = min(buffer.keys())
                    play_started = True
                    print("Starting playback…")

            # If playing, write the next frame every loop
            if play_started and expected_seq is not None:
                if expected_seq in buffer:
                    out.write(buffer.pop(expected_seq))
                else:
                    # Missing packet → write silence
                    out.write(silence)

                # Move to next seq (wrap @ 65536)
                expected_seq = (expected_seq + 1) & 0xFFFF

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        out.stop()
        out.close()
        sock.close()

if __name__ == "__main__":
    main()
