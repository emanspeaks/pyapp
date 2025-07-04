from PySide2.QtWidgets import QApplication

from ..logging import log_exc, log_func_call, DEBUGLOW2


class ExcHandlingQApp(QApplication):
    @log_func_call(DEBUGLOW2)
    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except BaseException as e:
            # Handle exception here (log, show dialog, etc.)
            # print("Exception in Qt event loop:", e)
            log_exc(value=e)
            return False  # or True, depending on your needs
