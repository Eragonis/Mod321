import subprocess
import signal
import os

class SoundPlayer():
    def __init__(self, filepath="Mission.ogg"):
        self.filepath = filepath
        self.process = None
        self.is_playing = False
        self.env = os.environ.copy()
        self.env["SDL_AUDIODRIVER"] = "alsa"
        self.env["AUDIODEV"] = "plughw:2,0"

    def _stop_process(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None

    def _start(self, start_seconds=0):
        self._stop_process()
        self.process = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-ss", str(start_seconds), self.filepath],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=self.env,
        )
        self.is_playing = True

    def toggle(self):
        if self.process is None or self.process.poll() is not None:
            self._start()
        elif self.is_playing:
            self.process.send_signal(signal.SIGSTOP)
            self.is_playing = False
        else:
            self.process.send_signal(signal.SIGCONT)
            self.is_playing = True
        return self.is_playing

    def restart(self):
        self._start(0)
        return self.is_playing

    def seek(self, seconds):
        self._start(seconds)
        return self.is_playing

    def status(self):
        return self.is_playing
