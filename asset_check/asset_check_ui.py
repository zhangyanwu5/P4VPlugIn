from PyQt5 import QtWidgets, QtCore
from asset_check.ui.asset_check_dialog import Ui_AssetCheckDialog


class AssetCheckDialog(QtWidgets.QDialog, Ui_AssetCheckDialog):
    def __init__(self, parent=None):
        super(AssetCheckDialog, self).__init__(parent)
        self.setupUi(self)

        self.output_plain_text_edit.setReadOnly(True)  # 设置为只读

    # 输出日志
    def output_log(self, log):
        _translate = QtCore.QCoreApplication.translate
        self.output_plain_text_edit.appendPlainText(_translate("AssetCheckDialog", log))


def create_application(args=[]) -> QtWidgets.QApplication:
    app = QtWidgets.QApplication(args)
    return app


def create_dialog() -> AssetCheckDialog:
    dialog = AssetCheckDialog()
    return dialog
