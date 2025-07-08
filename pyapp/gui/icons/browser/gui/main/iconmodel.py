from PySide2.QtCore import Qt, QStringListModel

from ..utils import iconstring_to_iconspec


class IconModel(QStringListModel):
    def flags(self, index: int):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def data(self, index: int, role: int):
        if role == Qt.DecorationRole:
            iconString = self.data(index, role=Qt.DisplayRole)
            if iconString:
                spec = iconstring_to_iconspec(iconString)
                return spec.icon()
            return None
        return super().data(index, role)
