import threading

class ResettableTimer:
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.timer = None

    def start(self):
        self.cancel()  # Cancel any existing timer
        self.timer = threading.Timer(self.interval, self.function, self.args, self.kwargs)
        self.timer.start()

    def cancel(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None