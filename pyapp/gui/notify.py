from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QObject, QEvent

from ..logging import log_exc
# from ..logging import log_func_call, DEBUGLOW2


class ExcHandlingQApp(QApplication):
    # only log user code, but can uncomment if you want to log all Qt events
    # @log_func_call(DEBUGLOW2)
    def notify(self, receiver: QObject, event: QEvent):
        try:
            return super().notify(receiver, event)
        except BaseException as e:
            log_exc(e)
            return False
