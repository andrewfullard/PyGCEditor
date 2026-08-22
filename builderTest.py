import logging

from PyQt6.QtWidgets import QApplication

from ui.qtformbuilder import FormBuilder


logger = logging.getLogger(__name__)

app = QApplication([])

builder = FormBuilder()

builder.form()
builder.add_input("Test1", "str")
builder.add_input("Test2", "str")
widget = builder.finish()

widget.onConfirm.connect(lambda: logger.info(widget.getContent("Test1")))
widget.onCancel.connect(lambda: logger.info(widget.getContent("Test2")))
widget.show()

app.exec()
