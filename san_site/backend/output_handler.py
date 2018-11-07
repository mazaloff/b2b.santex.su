import os
import subprocess
import threading
from Project import settings_local as settings
from time import sleep


class OutputMonitor(threading.Thread):
    """ Start the subprocess in separate thread and append it's output to a buffer. """

    def __init__(self, cmd):
        super(OutputMonitor, self).__init__()
        self.daemon = True
        self.cmd = cmd
        self.buffer = b''
        self.buflock = threading.Lock()

    def run(self):

        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while popen.poll() is None:
            data = popen.stdout.read(4)
            if data != b"":
                with self.buflock:
                    self.buffer += data

    def get_current_output(self):
        with self.buflock:
            buf = self.buffer
            self.buffer = b""
            return buf


class OutputHandler(threading.Thread):
    """  Start a thread responsible for tracking subprocess output, and periodically
         check if it has produced new output. If so, call handler to process this data.    """

    def __init__(self, cmd, interval, filepath):
        super(OutputHandler, self).__init__()
        self.om = OutputMonitor(cmd)
        self.interval = interval

        # Replace it with your handler init...
        self.filepath = filepath
        if os.path.exists(self.filepath):
            os.unlink(self.filepath)

    def run(self):

        self.om.start()
        while self.om.is_alive():
            sleep(self.interval)
            data = self.om.get_current_output()

            self._handle_data_chunk(data)

    def _handle_data_chunk(self, data):

        # Replace it with you handling.
        with open(self.filepath, 'ab') as f:
            f.write(data)


if __name__ == '__main__':
    logfile_path = "log.txt"

    python_bin = os.path.join(settings.PYTHON_BIN, 'python.exe')
    script_file = os.path.join(settings.BASE_DIR, 'server_nginx.py')

    interval = 5
    cmd = [python_bin, script_file]

    oh = OutputHandler(cmd, interval, logfile_path)
    oh.start()
    oh.join()
