"""
Model-view classes for displaying the results of reserve studies.
"""
from __future__ import annotations

import pandas as pd

import typing

from faslr.base_table import (
    FAbstractTableModel,
    FTableView
)

from faslr.constants import (
    ColumnGroupRole,
    ExhibitColumnRole,
    ICONS_PATH
)

from faslr.grid_header import (
    GridTableHeaderView,
    GridTableView
)

from PyQt6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt
)

from PyQt6.QtGui import (
    QIcon,
    QStandardItem,
    QStandardItemModel
)

from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QListView,
    QPushButton,
    QTabWidget,
    QTreeView,
    QWidget
)

from typing import (
    List,
    TYPE_CHECKING
)

if TYPE_CHECKING:
    from chainladder import Triangle

column_alias = {
    'Accident Year': 'Accident\nYear',
    'Age': 'Age'
}


class ExhibitModel(FAbstractTableModel):
    def __init__(self):
        super().__init__()

        self._data = pd.DataFrame(
            # {'hi': [1, 2, 3]}
        )

        # print(self._data)

    def data(
            self,
            index: QModelIndex,
            role: int = None
    ) -> typing.Any:

        # print(self._data)

        if role == Qt.ItemDataRole.DisplayRole:

            value = self._data.iloc[index.row(), index.column()]
            # print(value)

            display_value = str(value)

            return display_value

    def insertColumn(
            self,
            column: int,
            parent: QModelIndex = ...
    ) -> bool:

        idx = QModelIndex()
        new_column = self.columnCount()
        self.beginInsertColumns(
            idx,
            new_column,
            new_column
        )
        self.endInsertColumns()
        self.layoutChanged.emit()

        return True

    def setData(
            self,
            index: QModelIndex,
            value: typing.Any = None,
            role: int = None
    ) -> bool:

        column_name = value[0]
        column_values = value[1]

        self._data[column_name] = column_values
        print(self._data)

        self.dataChanged.emit(index, index)
        self.layoutChanged.emit()

        return True


class ExhibitView(GridTableView):
    def __init__(self):
        super().__init__()


    def insertColumn( # noqa
            self,
            colname: str,
            data
    ) -> None:

        column_count = self.model().columnCount()

        self.hheader.setSpan(
            row=0,
            column=column_count,
            row_span_count=2,
            column_span_count=0
        )

        idx = QModelIndex()
        model = self.model()
        model.setData(
            index=idx,
            value=(colname, data)
        )
        self.hheader.setCellLabel(
            row=0,
            column=column_count,
            label=column_alias[colname])

        column_position = model.columnCount() + 1
        model.insertColumn(column_position)
        self.hheader.model().insertColumn(column_position + 1)
        model.layoutChanged.emit() # noqa
    #
    # def insertColumnGroup(
    #         self
    # ) -> None:


class ExhibitHeaderView(GridTableHeaderView):
    def __init__(
            self,
            rows: int,
            columns: int,
            orientation: Qt.Orientation
    ):
        super().__init__(
            rows=rows,
            columns=columns,
            orientation=orientation
        )


class ExhibitBuilder(QWidget):
    def __init__(
            self,
            triangles=None
    ):
        """
        Dialog box used to create exhibits.
        """
        super().__init__()

        #### filler for example, delete this later #####

        self.preview_model = ExhibitModel()

        self.exhibit_preview = ExhibitView()
        self.exhibit_preview.verticalHeader().hide()

        self.exhibit_preview.setModel(self.preview_model)

        self.exhibit_preview.setGridHeaderView(
            orientation=Qt.Orientation.Horizontal,
            levels=2
        )

        self.triangles = triangles
        self.n_triangles = len(self.triangles)

        self.input_models = []

        self.setWindowTitle("Exhibit Builder")

        self.layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.ly_build = QHBoxLayout()
        self.main_widget.setLayout(self.ly_build)

        self.setLayout(self.layout)
        self.layout.addWidget(self.main_widget)

        # Each tab holds the available columns for a model.
        self.model_tabs = QTabWidget()
        for i in range(self.n_triangles):
            self.input_models.append(ModelTab())
            self.model_tabs.addTab(self.input_models[i], "Model " + str(i + 1))

        self.ly_build.addWidget(self.model_tabs)

        # Buttons to select and combine columns.
        self.input_btns = QWidget()
        self.ly_input_btns = QVBoxLayout()
        self.ly_input_btns.setSpacing(4)
        self.ly_input_btns.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.input_btns.setLayout(self.ly_input_btns)

        self.add_column_btn = make_middle_button(
            path=ICONS_PATH + 'arrow-right.svg'
        )

        self.remove_column_btn = make_middle_button(
            path=ICONS_PATH + 'arrow-left.svg'
        )

        self.add_link_btn = make_middle_button(
            path=ICONS_PATH + 'link.svg'
        )

        self.remove_link_btn = make_middle_button(
            path=ICONS_PATH + 'no-link.svg'
        )

        for btn in [
            self.add_column_btn,
            self.remove_column_btn,
            self.add_link_btn,
            self.remove_link_btn
        ]:
            self.ly_input_btns.addWidget(
                btn,
                stretch=0
            )

        self.ly_build.addWidget(self.input_btns)
        self.output_label = QLabel("Exhibit Columns")

        # Use a container to pad alignment.
        self.output_container = QWidget()
        self.ly_output = QVBoxLayout()
        self.ly_output.setContentsMargins(
            0,
            3,
            0,
            0
        )

        # Output columns selected by the user.
        self.output_container.setLayout(self.ly_output)
        self.output_model = QStandardItemModel()
        self.output_root = self.output_model.invisibleRootItem()
        self.output_view = ExhibitOutputTreeView()
        self.output_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.output_view.setModel(self.output_model)
        self.ly_output.addWidget(self.output_label)
        self.ly_output.addWidget(self.output_view)

        self.ly_build.addWidget(self.output_container)

        self.output_buttons = ExhibitOutputButtonBox()

        self.ly_build.addWidget(self.output_buttons)

        # Add bottom button box.
        self.ok_btn = QDialogButtonBox.StandardButton.Ok
        self.cancel_btn = QDialogButtonBox.StandardButton.Cancel
        self.button_layout = self.ok_btn | self.cancel_btn
        self.button_box = QDialogButtonBox(self.button_layout)

        self.preview_label = QLabel("Exhibit Preview")
        self.layout.addWidget(self.preview_label)
        self.layout.addWidget(self.exhibit_preview)
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.map_header)  # noqa
        self.button_box.rejected.connect(self.close)  # noqa

        self.add_column_btn.pressed.connect( # noqa
            self.add_output
        )

        self.remove_column_btn.pressed.connect( # noqa
            self.remove_output
        )
        self.add_link_btn.pressed.connect( # noqa
            self.group_columns
        )

        self.output_buttons.col_rename_btn.pressed.connect( # noqa
            self.rename_column
        )

    def rename_column(self) -> None:

        selected_indexes = self.output_view.selectedIndexes()
        print(selected_indexes)

        if len(selected_indexes) == 1:

            idx = selected_indexes[0]

            dialog = RenameColumnDialog(
                index=idx,
                parent=self
            )

            dialog.exec()


    def add_output(
            self,
            group_name: str = None
    ) -> None:

        selected_indexes = self.model_tabs.currentWidget().list_view.selectedIndexes()

        if group_name is None:
            for index in selected_indexes:
                colname = index.data(Qt.ItemDataRole.DisplayRole)
                output_item = ExhibitOutputTreeItem(
                    text=colname,
                    role=ExhibitColumnRole
                )
                self.output_root.appendRow(output_item)

                if colname == "Accident Year":
                    data = self.triangles[0].X_.origin.to_frame().index.astype(str).tolist()
                else:
                    data = list(self.triangles[0].X_.development.sort_values(ascending=False))

                self.exhibit_preview.insertColumn(
                    colname=colname,
                    data=data
                )
        else:
            group_item = ExhibitOutputTreeItem(
                text=group_name,
                role=ColumnGroupRole
            )
            for index in selected_indexes:
                colname = index.data(Qt.ItemDataRole.DisplayRole)
                output_item = ExhibitOutputTreeItem(
                    text=colname,
                    role=ExhibitColumnRole
                )
                group_item.appendRow(output_item)

                if colname == 'Reported Claims':
                    idx = QModelIndex()
                    data = list(self.triangles[0].X_.latest_diagonal.to_frame().iloc[:,0])
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, colname)
                    self.preview_model.layoutChanged.emit()

                if colname == 'Paid Claims':
                    idx = QModelIndex()
                    data = list(self.triangles[1].X_.latest_diagonal.to_frame().iloc[:, 0])
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, colname)
                    self.preview_model.layoutChanged.emit()

                if colname == 'Reported CDF':
                    idx = QModelIndex()
                    data = list(self.triangles[0].X_.cdf_.to_frame().iloc[0, :].values.flatten())
                    data.pop()
                    print(data)
                    data.reverse()
                    print(data)
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, colname)
                    self.preview_model.layoutChanged.emit()

                if colname == 'Paid CDF':
                    idx = QModelIndex()
                    data = list(self.triangles[1].X_.cdf_.to_frame().iloc[0, :].values.flatten())
                    data.pop()
                    data.reverse()
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, colname)
                    self.preview_model.layoutChanged.emit()

                if colname == 'Ultimate Reported Claims':
                    idx = QModelIndex()
                    data = list(self.triangles[0].ultimate_.to_frame().iloc[:, 0])
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, 'Reported')
                    self.preview_model.layoutChanged.emit()

                if colname == 'Ultimate Paid Claims':
                    idx = QModelIndex()
                    data = list(self.triangles[1].ultimate_.to_frame().iloc[:, 0])
                    self.preview_model.setData(idx, value=(colname, data))
                    self.preview_model.insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.model().insertColumn(self.preview_model.columnCount() + 1)
                    self.exhibit_preview.hheader.setCellLabel(1, self.preview_model.columnCount() - 1, 'Paid')
                    self.preview_model.layoutChanged.emit()

            self.output_root.appendRow(group_item)

            self.exhibit_preview.hheader.setSpan(
                row=0,
                column=self.preview_model.columnCount()-2,
                row_span_count=1,
                column_span_count=2
            )

            self.exhibit_preview.hheader.setCellLabel(0, self.preview_model.columnCount() - 2, group_name)

    def remove_output(self):

        selected_indexes = self.output_view.selectedIndexes()
        for index in selected_indexes:
            self.output_model.removeRow(index.row(), index.parent())

    def group_columns(
            self
    ) -> None:

        group_dialog = ExhibitGroupDialog(parent=self)

        group_dialog.exec()

    def map_header(self) -> None:
        root = self.output_root
        for row in range(self.output_root.rowCount()):
            item = root.child(row)
            print(item.text())
            if item.role == ColumnGroupRole:
                for subitem in range(item.rowCount()):
                    print(item.child(subitem).text())

        self.close()


class ExhibitGroupDialog(QDialog):
    def __init__(
            self,
            parent: ExhibitBuilder = None
    ):
        super().__init__()

        self.parent = parent

        self.setWindowTitle("Add Column Group")

        self.layout = QFormLayout()

        self.group_edit = QLineEdit()
        self.layout.addRow("Column Group Name:", self.group_edit)

        self.button_layout = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(self.button_layout)
        self.button_box.accepted.connect(self.add_group)
        self.button_box.rejected.connect(self.close)

        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def add_group(self) -> None:

        text = self.group_edit.text()

        self.parent.add_output(group_name=text)

        self.close()


class ModelTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.list_model = ExhibitInputListModel(
            input_columns=[
                'Accident Year',
                'Age',
                'Reported Claims',
                'Paid Claims',
                'Reported CDF',
                'Paid CDF',
                'Ultimate Reported Claims',
                'Ultimate Paid Claims'
            ]
        )
        self.list_view = QListView()
        self.list_view.setModel(self.list_model)
        self.layout.addWidget(self.list_view)
        # Enable user to select multiple list items
        self.list_view.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setLayout(self.layout)


class ExhibitInputListModel(QAbstractListModel):
    """
    Model for the list of settings that appears in the left-hand pane. Selecting an item should change the
    corresponding layout in the right-hand pane.
    """
    def __init__(self, input_columns=None):
        super().__init__()
        self.input_columns = input_columns or []

    def data(self, index, role=None):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.input_columns[index.row()]

    def rowCount(self, parent=None):
        return len(self.input_columns)


class ExhibitOutputTreeItem(QStandardItem):
    def __init__(
            self,
            text: str,
            role: int
    ):
        super().__init__()

        self.setText(text)
        self.role = role

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsEditable)


class ExhibitOutputTreeView(QTreeView):
    def __init__(self):
        super().__init__()

        self.setHeaderHidden(True)


class ExhibitOutputButtonBox(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.col_up_btn = make_middle_button(
            path=ICONS_PATH + 'nav-arrow-up.svg'
        )

        self.col_dwn_btn = make_middle_button(
            path=ICONS_PATH + 'nav-arrow-down.svg'
        )

        self.col_rename_btn = make_middle_button(
            path=ICONS_PATH + 'text-alt.svg'
        )

        for widget in [
            self.col_up_btn,
            self.col_dwn_btn,
            self.col_rename_btn
        ]:
            self.layout.addWidget(
                widget,
                stretch=0
            )

        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.setLayout(self.layout)


class RenameColumnDialog(QDialog):
    def __init__(
            self,
            index: QModelIndex,
            parent: ExhibitBuilder = None
    ):
        super().__init__()

        self.setWindowTitle("Rename Column")

        self.index = index
        self.parent = parent

        self.layout = QFormLayout()
        self.new_name = QLineEdit()
        self.layout.addRow("Rename Column:", self.new_name)

        self.button_layout = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.button_box = QDialogButtonBox(self.button_layout)
        self.button_box.accepted.connect(self.send_name)
        self.button_box.rejected.connect(self.close)

        self.layout.addWidget(self.button_box)

        self.setLayout(self.layout)

    def send_name(self) -> None:

        text = self.new_name.text()
        self.parent.output_model.setData(
            index=self.index,
            value=text,
            role=Qt.ItemDataRole.EditRole
        )
        self.close()


def make_middle_button(
        path: str
) -> QPushButton:
    btn = QPushButton()
    btn.setIcon(QIcon(path))

    return btn
