# UDP Audio Stream
This is a simple UDP-based audio streaming solution for Windows. This code captures system audio using WASAPI (Windows Audio API) loopback and streams it in real time to a reciever over a local network. 

## Features
WASAPI LOOPBACK: captures all system audio output (what yuou've set as your window's active audio speakers)
Low latency and latency control: 20ms frame duration with configurable jitter buffer
Simple Protocol: Lightweight UDP transport with sequence numbers for packet ordering.
Jitter Buffer: Handles packet loss and netwrok jitter

## Requirements
Python 3.x
Windows (Sender uses WASAPI loopback)

## Libraries
pip install sounddevice pyaudiowpatch

# HOW TO USE
## Sender (The windows machine that we'll stream audio from)
Edit `Sender.py` and set the `DEST_IP` to the receiver's IP address.
Run `Sender.py`

### (optionally) Use enviornment varaibles
set DEST_IP = `ip here`
set DEST_PORT = `port here`
python Sender.py

## Receiver (The windows machien that will receive the audio stream)
Edit `Reciever.py` and set `Listen_IP` 
Run `Reciever.py`

### (Optionally) use environment varaibles
Set LISTEN_PORT = `port here`
Python Reciver.py

# Configuration
### Sender settings
| Setting | Default | Description |
|`DEST_IP` | `IP HERE` | Reciever's IP address
|`DEST_PORT`| `3002` | Reciver's UDP port 
|`SAMPLE_RATE` | `48000` | Audio Sample Rate (Hz) 
|`FRAME_DURATION` | `20`| Frame duration (ms)

### Receiver Settings
| Setting | Default | Description |
|`LISTEN_IP` | `IP HERE`| IP to bind to
|`LISTEN_PORT`| `3002` | UDP port to listen to
|`TARGET_BUFFER_PACKETS` | `1` | Packets to buffer before playback (Increase if audio begins to crackle)

## Limitations
No eencryption, authentication, compression (raw PCM), device discovvery, sender requires Windows for (WASAPI loopback)

## Issues
On some application switch Sender.py and Reciver.py must be restarted. 


## License
MIT