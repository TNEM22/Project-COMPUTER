import json
import queue
import sounddevice as sd
import vosk
import sys


class WakeWordVosk():
    def __init__(self, model, device=1, sample_rate=44100, ww='computer'):
        self.model = model
        self.device = device
        self.samplerate = int(sample_rate)
        self.q = queue.Queue()
        self.ww = str(ww).lower()

    def callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.q.put(bytes(indata))

    def run(self):
        with sd.RawInputStream(samplerate=self.samplerate, blocksize=8000, device=self.device, dtype='int16',
                               channels=1, callback=self.callback):

            rec = vosk.KaldiRecognizer(self.model, self.samplerate)
            while True:
                data = self.q.get()
                if rec.AcceptWaveform(data):
                    pass
                else:
                    text = json.loads(rec.PartialResult())['partial']
                    if self.ww in text:
                        return 0
