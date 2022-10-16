import numpy as np
import pandas as pd

from faslr.base_table import (
    FAbstractTableModel,
    FTableView
)

from faslr.constants import (
    QT_FILEPATH_OPTION
)

from PyQt6.QtCore import (
    QAbstractTableModel,
    Qt
)

from PyQt6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget
)


class DataPane(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.wizard = None

        self.layout = QVBoxLayout()
        self.upload_btn = QPushButton("Upload")
        self.setLayout(self.layout)
        self.layout.addWidget(
            self.upload_btn,
            alignment=Qt.AlignmentFlag.AlignRight
        )
        filler = QWidget()
        self.layout.addWidget(filler)
        self.upload_btn.pressed.connect(self.start_wizard) # noqa

    def start_wizard(self):

        self.wizard = DataImportWizard()

        self.wizard.show()


class DataImportWizard(QWidget):
    def __init__(
            self,
            parent=None
    ):
        super().__init__()

        self.setWindowTitle("Import Wizard")

        self.layout = QVBoxLayout()
        self.upload_form = QFormLayout()
        self.file_path = QLineEdit()
        self.upload_btn = QPushButton("Upload File")
        self.upload_container = QWidget()
        self.upload_container.setLayout(self.upload_form)

        self.file_path_layout = QHBoxLayout()
        self.file_path_container = QWidget()
        self.file_path_container.setLayout(self.file_path_layout)
        self.file_path_layout.addWidget(self.upload_btn)
        self.file_path_layout.addWidget(self.file_path)

        self.upload_form.addRow(
            self.file_path_container
        )

        self.layout.addWidget(self.upload_container)
        self.setLayout(self.layout)

        self.upload_btn.pressed.connect(self.load_file) # noqa

        self.upload_sample_model = UploadSampleModel()
        self.upload_sample_view = UploadSampleView()
        self.upload_sample_view.setModel(self.upload_sample_model)

        self.layout.addWidget(self.upload_sample_view)

    def load_file(self):

        filename = QFileDialog.getOpenFileName(
            parent=self,
            caption='Open File',
            filter='CSV (*.csv)',
            options=QT_FILEPATH_OPTION
        )[0]

        self.file_path.setText(filename)


class UploadSampleModel(FAbstractTableModel):
    def __init__(self):
        super().__init__()

        self._data = pd.DataFrame(
            data={'A': [np.nan, np.nan, np.nan],
                  'B': [np.nan, np.nan, np.nan],
                  'C': [np.nan, np.nan, np.nan],
                  '': [np.nan, np.nan, np.nan]
            })



class UploadSampleView(FTableView):
    def __init__(self):
        super().__init__()

        # self.horizontalHeader().setStretchLastSection(True)
        # self.verticalHeader().setStretchLastSection(True)