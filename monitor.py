import pyaudio, struct, settings

def continuous(call, seconds = 24*3600*30):
    audiostream = AudioSteam()
    
    for _ in range(0, int(settings.RATE / settings.CHUNK * seconds)):
        data = audiostream.stream.read(settings.CHUNK)
        count = len(data)/2
        shorts = struct.unpack('%dh' % count, data)
        call(shorts)

    audiostream.close()

def record_for_time(seconds):
    audiostream = AudioSteam()
    frames = []
    for _ in range(0, int(settings.RATE / settings.CHUNK * seconds)):
        data = audiostream.stream.read(settings.CHUNK)
        frames.append(data)

    audiostream.close()
    samples = []
    for block in frames:
        count = len(block)/2
        shorts = struct.unpack( '%dh' % count, block )
        samples.extend(shorts)
    return samples
    
class AudioSteam(object):
    def __init__(self):
        self._p = pyaudio.PyAudio()
        self.stream = self._p.open(format=settings.FORMAT,
                        channels=settings.CHANNELS,
                        rate=settings.RATE,
                        input=True,
                        frames_per_buffer=settings.CHUNK)
    
    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self._p.terminate()