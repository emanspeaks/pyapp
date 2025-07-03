from PySide2.QtWidgets import QApplication

from ..logging import log_exc


class ExcHandlingQApp(QApplication):
    def notify(self, receiver, event):
        try:
            return super().notify(receiver, event)
        except Exception as e:
            # Handle exception here (log, show dialog, etc.)
            # print("Exception in Qt event loop:", e)
            log_exc(value=e)
            return False  # or True, depending on your needs
