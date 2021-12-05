import os
import struct
from datetime import datetime
from threading import Thread

# import numpy as np
import pvporcupine
import pyaudio
# import soundfile


class computerWW(Thread):
    """
    Microphone Demo for Porcupine wake word engine. It creates an input audio stream from a microphone, monitors it, and
    upon detecting the specified wake word(s) prints the detection time and wake word on console. It optionally saves
    the recorded audio into a file for further debugging.
    """

    def __init__(self):

        super(computerWW, self).__init__()

        self._library_path = pvporcupine.LIBRARY_PATH
        self._model_path = pvporcupine.MODEL_PATH
        self._keyword_paths = [pvporcupine.KEYWORD_PATHS['computer']]
        self._sensitivities = [0.5]
        self._input_device_index = 1

        self._output_path = None
        if self._output_path is not None:
            self._recorded_frames = []

        self.keywords = list()
        for x in self._keyword_paths:
            self.keyword_phrase_part = os.path.basename(
                x).replace('.ppn', '').split('_')
            if len(self.keyword_phrase_part) > 6:
                self.keywords.append(' '.join(self.keyword_phrase_part[0:-6]))
            else:
                self.keywords.append(self.keyword_phrase_part[0])

        self.porcupine = None
        self.pa = None
        self.audio_stream = None

        self.porcupine = pvporcupine.create(
            library_path=self._library_path,
            model_path=self._model_path,
            keyword_paths=self._keyword_paths,
            sensitivities=self._sensitivities)

        self.pa = pyaudio.PyAudio()

        self.audio_stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length,
            input_device_index=self._input_device_index)

    def run(self):
        """
         Creates an input audio stream, instantiates an instance of Porcupine object, and monitors the audio stream for
         occurrences of the wake word(s). It prints the time of detection for each occurrence and the wake word.
         """
        try:
            print('Listening {')
            for keyword, sensitivity in zip(self.keywords, self._sensitivities):
                print('  %s (%.2f)' % (keyword, sensitivity))
            print('}')

            while True:
                pcm = self.audio_stream.read(self.porcupine.frame_length)
                pcm = struct.unpack_from(
                    "h" * self.porcupine.frame_length, pcm)

                if self._output_path is not None:
                    self._recorded_frames.append(pcm)

                result = self.porcupine.process(pcm)
                if result >= 0:
                    return 0

        except KeyboardInterrupt:
            print('Stopping ...')
