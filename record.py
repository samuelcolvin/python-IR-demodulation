import pyaudio, struct
CHUNK = 16384#4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

def continuous(call):
    seconds = 24*3600
    audiostream = AudioSteam()
    
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = audiostream.stream.read(CHUNK)
        count = len(data)/2
        format = "%dh" % count
        shorts = struct.unpack(format, data)
        call(shorts)

    audiostream.close()

def record_for_time(seconds):
    audiostream = AudioSteam()
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = audiostream.stream.read(CHUNK)
        frames.append(data)

    audiostream.close()
    samples = []
    for block in frames:
        count = len(block)/2
        format = "%dh"%(count)
        shorts = struct.unpack( format, block )
        samples.extend(shorts)
    return samples
    
class AudioSteam(object):
    def __init__(self):
        self._p = pyaudio.PyAudio()
        self.stream = self._p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self._p.terminate()