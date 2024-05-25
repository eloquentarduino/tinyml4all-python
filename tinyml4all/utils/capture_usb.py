import os.path
from datetime import datetime
from time import time
from typing import Self

from durations import Duration
from serial import Serial
from tqdm.auto import tqdm

from tinyml4all.typing import ListOfStrings, as_list_of_strings, Filename
from tinyml4all.utils.countdown import countdown


class CaptureUSB:
    """
    Read data from a serial port and save to file.
    """
    def __init__(self, duration: str):
        """

        :param duration: how much time to collect data
        """
        self._config = {
            "duration": Duration(duration),
            "port": None,
            "baudrate": None,
            "columns": None,
            "dest": None,
            "mode": "a"
        }

    def from_port(self, port: str, baudrate: int = 115200) -> Self:
        """
        Set serial port
        :param port: COM?, /dev/tty.USB?, etc.
        :param baudrate:
        :return:
        """
        self._config["port"] = port
        self._config["baudrate"] = baudrate
        return self

    def with_names(self, names: ListOfStrings) -> Self:
        """
        Set column names
        :param names: either a comma-separated string or a list
        :return:
        """
        self._config["columns"] = as_list_of_strings(names)
        return self

    def to_file(self, dest: Filename) -> Self:
        """
        Set destination file
        :param dest: a string or a Path
        :return:
        """
        self._config["dest"] = dest

        if os.path.isfile(dest):
            ans = input(f"File {dest} already exists. Do you want to wipe its contents before appending new data? (y|n) ").strip()
            self._config["mode"] = "w" if ans.startswith("y") else "a"

            if self._config["mode"] == "w":
                with open(dest, "w"):
                    pass

        return self

    def run(self):
        """
        Start the collection
        :return:
        """
        port = self._config["port"]
        baudrate = self._config["baudrate"]
        columns = self._config["columns"]
        dest = self._config["dest"]
        duration = self._config["duration"]
        mode = self._config["mode"]

        assert duration.seconds > 0, "duration must be greater than 1 second"
        assert port is not None, "you must set a port"
        assert baudrate is not None and baudrate > 0, "you must set a baudrate"
        assert columns is not None, "you must set the columns' names"
        assert dest is not None, "you must set a destination file"

        count = 0
        write_header = os.path.isfile(dest) is False or os.stat(dest).st_size < 2

        with Serial(port, baudrate, timeout=3) as serial:
            with open(dest, mode, encoding="utf-8") as file:
                if write_header:
                    file.write(",".join(["timestamp"] + columns))
                    file.write("\n")

                countdown()
                serial.reset_input_buffer()

                updated_at = time()
                now = updated_at
                timeout = now + duration.seconds

                with tqdm(total=int(duration.seconds)) as progress:
                    while now < timeout:
                        now = time()

                        if int(now) > int(updated_at):
                            delta = int(now) - int(updated_at)
                            updated_at = now
                            progress.update(delta)

                        try:
                            line = serial.readline().decode("utf-8").strip()

                            if len(line) > 0:
                                timestamp = str(datetime.now())
                                values = as_list_of_strings(line)

                                assert len(values) == len(columns), f"size mismatch: expected {len(columns)}, got {len(values)}"
                                file.write(f"{timestamp},{line}\n")
                                file.flush()
                                count += 1
                        except UnicodeDecodeError:
                            pass

        print(f"Collected {count} lines of data")


def capture_usb(duration: str) -> CaptureUSB:
    """
    Factory method to initiate a new USB capture session
    :param duration: how much time to collect data
    :return:
    """
    return CaptureUSB(duration)