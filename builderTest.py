from PyQt6.QtWidgets import QApplication

from ui.qtformbuilder import FormBuilder

app = QApplication([])

builder = FormBuilder()

builder.form()
builder.add_input("Test1", "str")
builder.add_input("Test2", "str")
widget = builder.finish()

widget.onConfirm.connect(lambda: print(widget.getContent("Test1")))
widget.onCancel.connect(lambda: print(widget.getContent("Test2")))
widget.show()

app.exec()