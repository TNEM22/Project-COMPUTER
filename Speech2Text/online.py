# from PIL.Image import preinit
import speech_recognition as sr

from pydub import AudioSegment
from pydub.playback import play

import os


class Speech2TextON():
    def __init__(self, real_path):
        chime_path = os.path.join(
            os.path.dirname(real_path), 'Resources/chime.wav')
        self.chime = AudioSegment.from_wav(chime_path)

        self.recording = sr.Recognizer()

    def run(self):
        while True:
            with sr.Microphone(device_index=1, sample_rate=44100) as source:
                # recording.adjust_for_ambient_noise(source)
                # print("Please Say something:")
                play(self.chime)
                audio = self.recording.listen(source, timeout=2)
                # source, timeout=2, phrase_time_limit=2)

            print("Recognizing")
            try:
                text = self.recording.recognize_google(audio, language='en-in')
            except sr.UnknownValueError:
                return "Unable to Hear!"
            return text


if __name__ == "__main__":
    print(Speech2TextON().run())
