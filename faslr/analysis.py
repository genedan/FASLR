from faslr.base_table import (
    FAbstractTableModel,
    FTableView
)

from faslr.constants import (
    MACK_DEVELOPMENT_CRITICAL,
    MACK_VALUATION_CRITICAL,
    VALUE_TYPES,
    VALUE_TYPES_COMBO_BOX_WIDTH
)

from chainladder import Triangle

from faslr.utilities.accessors import get_column

from PyQt5.QtCore import (
    Qt
)

from PyQt5.QtGui import QColor

from PyQt5.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QDoubleSpinBox,
    QStackedWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget
)

from faslr.triangle_model import (
    TriangleModel,
    TriangleView
)

pass_alias = {
    True: "Fail",
    False: "Pass"
}

starting_value_lookup = {
    "valuation correlation": MACK_VALUATION_CRITICAL,
    "development correlation": MACK_DEVELOPMENT_CRITICAL
}


class AnalysisTab(QWidget):
    # should eventually contain the TriangleColumnTab
    def __init__(
            self, triangle: Triangle,
            lob: str = None
    ):
        super().__init__()

        self.triangle = triangle
        self.lob = lob

        self.layout = QVBoxLayout()

        # The combo box is used to switch between values (losses/premiums) and link ratios.
        self.value_box = QComboBox()
        self.value_box.setFixedWidth(VALUE_TYPES_COMBO_BOX_WIDTH)
        self.value_box.addItems(VALUE_TYPES)

        self.column_tab = ColumnTab()
        self.column_tab.setTabPosition(QTabWidget.West)

        self.column_list = list(self.triangle.columns)

        # These dictionaries allow us to keep track of and manipulate the views later.
        # Each view is identified by the column name.
        self.triangle_views = {}
        self.analysis_containers = {}
        self.diagnostic_containers = {}
        self.mack_valuation_groupboxes = {}
        self.mack_valuation_individual_models = {}
        self.mack_valuation_individual_views = {}
        self.mv_max_individual_widths = {}
        self.mack_development_groupboxes = {}
        self.diagnostic_widgets = {}
        self.mack_valuation_padding_widgets = {}
        self.mack_valuation_correlations = {}
        self.mack_development_critical_layouts = {}
        self.mack_development_correlations = {}
        self.mack_valuation_passes = {}
        self.mack_development_passes = {}
        self.mack_valuation_individual_groupboxes = {}
        self.mack_valuation_individual_layouts = {}
        self.mack_valuation_individual_critical_containers = {}
        self.mack_valuation_individual_critical_layouts = {}
        self.mack_valuation_individual_critical_spin_boxes = {}
        self.mack_valuation_individual_container_layouts = {}
        self.mack_valuation_individual_top_containers = {}
        self.mack_individual_model_layouts = {}
        self.mack_individual_model_containers = {}
        self.mack_individual_model_paddings_left = {}
        self.mack_individual_model_paddings_right = {}

        column_count = len(self.column_list)

        # Used to solve some issues with borders not appearing when there's only 1 tab.
        if column_count == 1:
            bottom_border_width = 2
            margin_top = "43"
        else:
            bottom_border_width = 1
            margin_top = "0"

        # For each chainladder column, we create a horizontal tab to the left.
        for i in self.column_list:

            triangle_column = get_column(
                triangle=self.triangle,
                column=i,
                lob=self.lob
            )

            self.triangle_views[i] = TriangleView()
            # We use QStackedWidget to switch between tabular and diagnostic views.
            self.analysis_containers[i] = QStackedWidget()
            self.analysis_containers[i].addWidget(self.triangle_views[i])
            self.diagnostic_containers[i] = QVBoxLayout()
            self.diagnostic_containers[i].setSpacing(30)

            self.mack_valuation_groupboxes[i] = MackAllYearGroupBox(
                title="Mack Valuation Correlation Test - All Years",
                triangle=triangle_column,
                test_type="valuation correlation"
            )
            self.diagnostic_containers[i].addWidget(self.mack_valuation_groupboxes[i])

            self.mack_valuation_individual_groupboxes[i] = MackIndividualGroupBox(
                title="Mack Valuation Correlation Test - Individual Years",
                triangle=triangle_column
            )

            self.diagnostic_containers[i].addWidget(self.mack_valuation_individual_groupboxes[i])

            self.mv_max_individual_widths[i] = self.mack_valuation_individual_groupboxes[i].mv_max_individual_width

            self.mack_development_groupboxes[i] = MackAllYearGroupBox(
                title="Mack Development Correlation Test",
                triangle=triangle_column,
                test_type="development correlation"
            )

            self.diagnostic_containers[i].addWidget(
                self.mack_development_groupboxes[i],
                stretch=0
            )

            self.diagnostic_containers[i].addWidget(
                QWidget(),
                stretch=2
            )

            self.mack_development_view = MackValuationView

            self.diagnostic_widgets[i] = DiagnosticWidget()

            self.diagnostic_widgets[i].setLayout(self.diagnostic_containers[i])
            self.analysis_containers[i].addWidget(self.diagnostic_widgets[i])

            triangle_model = TriangleModel(triangle_column, 'value')
            self.triangle_views[i].setModel(triangle_model)

            self.analysis_containers[i].setStyleSheet(
                """
                DiagnosticWidget {
                    border: 1px solid darkgrey;
                    background: rgb(230, 230, 230);
                }
                """
            )

            self.column_tab.addTab(self.analysis_containers[i], i)

        self.layout.addWidget(
            self.value_box,
            alignment=Qt.AlignRight
        )
        self.layout.addWidget(self.column_tab)

        self.setLayout(self.layout)

        self.column_tab.setStyleSheet(
            """
            QTabBar::tab:first {{
                margin-top: 43px;
            }}
            
            
            QTabBar::tab {{
              margin-top: {}px;
              background: rgb(230, 230, 230); 
              border: 1px solid darkgrey;
              border-bottom: {}px solid darkgrey; 
              padding: 5px;
              padding-left: 10px;
              height: 250px;
              margin-right: -1px;
            }}

            QTabBar::tab:selected {{ 
              background: rgb(245, 245, 245);
              margin-bottom: -1px;
            }}
            
            QTabWidget::pane {{
              border-top: 2px solid darkgrey;
            }}
            """.format(margin_top, bottom_border_width)
        )

        self.setAutoFillBackground(True)
        palette = self.palette()

        palette.setColor(
            self.backgroundRole(),
            QColor.fromRgb(
                240,
                240,
                240
            )
        )

        self.setPalette(palette)

        self.value_box.currentTextChanged.connect(self.update_value_type) # noqa

    def resizeEvent(self, event):

        for i in self.column_list:
            if self.width() >= self.mv_max_individual_widths[i] + 166:
                self.mack_valuation_individual_views[i].setFixedHeight(103)
                self.mack_valuation_padding_widgets[i].setFixedHeight(55)
            else:
                self.mack_valuation_individual_views[i].setFixedHeight(132)
                self.mack_valuation_padding_widgets[i].setFixedHeight(26)

    def update_value_type(self):

        if self.value_box.currentText() == "Link Ratios":
            value_type = 'ratio'
            triangle = self.triangle.link_ratio

        elif self.value_box.currentText() == "Values":
            value_type = 'value'
            triangle = self.triangle

        else:
            value_type = "diagnostics"
            triangle = self.triangle

        for i in range(len(self.column_list)):
            index = i
            tab_name = self.column_tab.tabText(index)

            if value_type != "diagnostics":
                triangle_column = triangle[self.column_list[index]]

                triangle_model = TriangleModel(triangle_column, value_type)
                self.triangle_views[tab_name].setModel(triangle_model)
                self.analysis_containers[tab_name].setCurrentIndex(0)
            else:
                self.analysis_containers[tab_name].setCurrentIndex(1)


class MackValuationModel(FAbstractTableModel):
    def __init__(
        self,
        triangle: Triangle,
        critical: QDoubleSpinBox
    ):
        super(
            MackValuationModel,
            self
        ).__init__()

        self.triangle = triangle
        self.spin_box = critical
        self.critical_value = self.spin_box.value()

        corr = self.triangle.valuation_correlation(
            p_critical=self.critical_value,
            total=False
        ).z_critical

        self._data = corr.to_frame(
            origin_as_datetime=False
        )

        self.spin_box.valueChanged.connect(self.recalculate) # noqa

    def data(
        self,
        index,
        role=None
    ):

        if role == Qt.DisplayRole:

            value = pass_alias[
                self._data.iloc[
                    index.row(),
                    index.column()
                ]
            ]

            value = str(value)

            return value

    def headerData(
        self,
        p_int,
        qt_orientation,
        role=None
    ):

        if role == Qt.DisplayRole:
            if qt_orientation == Qt.Horizontal:
                return self._data.columns[p_int]

            if qt_orientation == Qt.Vertical:
                return str(self._data.index[p_int])

    def recalculate(self):
        self.critical_value = self.spin_box.value()
        corr = self.triangle.valuation_correlation(
            p_critical=self.critical_value,
            total=False
        ).z_critical

        self._data = corr.to_frame(
            origin_as_datetime=False
        )

        self.layoutChanged.emit() # noqa


class MackValuationView(FTableView):
    def __init__(self):
        super().__init__()


class DiagnosticWidget(QWidget):
    def __init__(self):
        super().__init__()


class ColumnTab(QTabWidget):
    def __init__(self):
        super().__init__()


class MackResultLabel(QLabel):
    def __init__(
            self,
            spin: QDoubleSpinBox,
            triangle: Triangle,
            test_type: str
    ):
        super().__init__()

        self.spin = spin
        self.triangle = triangle
        self.test_type = test_type
        self.test_bool = None

        self.update_result()

        self.spin.valueChanged.connect(self.update_result) # noqa

    def update_result(self):

        if self.test_type == "valuation correlation":
            self.test_bool = self.triangle.valuation_correlation(
                p_critical=self.spin.value(),
                total=True
            ).z_critical.values[0][0]

        elif self.test_type == "development correlation":
            self.test_bool = self.triangle.development_correlation(
                p_critical=self.spin.value()
            ).t_critical.values[0][0]

        else:
            raise ValueError("Invalid test-type indicated.")

        self.setText("Status: " + pass_alias[self.test_bool])


class MackCriticalSpinBox(QDoubleSpinBox):
    def __init__(
            self,
            starting_value: float,
            maximum: float = 1,
            minimum: float = 0,
            step: float = .01,
            width: int = 100
    ):
        super().__init__()

        self.setMaximum(maximum)
        self.setMinimum(minimum)
        self.setValue(starting_value)
        self.setSingleStep(step)
        self.setFixedWidth(width)


class MackAllYearGroupBox(QGroupBox):
    def __init__(
            self,
            title: str,
            triangle: Triangle,
            test_type: str
    ):
        super().__init__()

        self.setTitle(title)
        self.triangle = triangle
        self.test_type = test_type

        starting_value = starting_value_lookup[self.test_type]

        # Holds the critical container and test status, horizontally
        self.horizontal_layout = QHBoxLayout()
        self.setLayout(self.horizontal_layout)

        # Critical layout holds the spinbox as a form
        self.critical_container = QWidget()
        self.critical_layout = QFormLayout()
        self.critical_container.setLayout(self.critical_layout)
        self.spin_box = MackCriticalSpinBox(starting_value=starting_value)

        self.test_result_label = MackResultLabel(
            spin=self.spin_box,
            triangle=triangle,
            test_type=self.test_type
        )

        self.critical_layout.addRow(
            "Critical Value: ",
            self.spin_box
        )

        # This configuration of stretch values is to keep the widgets fixed aligned to the left
        self.horizontal_layout.addWidget(
            self.critical_container,
            stretch=0
        )

        self.horizontal_layout.addWidget(
            self.test_result_label,
            stretch=0
        )

        self.horizontal_layout.addWidget(
            QWidget(),
            stretch=2
        )

        self.horizontal_layout.setAlignment(Qt.AlignTop)


class MackIndividualGroupBox(QGroupBox):
    def __init__(
        self,
        title: str,
        triangle: Triangle
    ):
        super().__init__()

        self.setTitle(title)
        self.triangle=triangle

        # Holds 2 levels, one for the critical spin box,
        # the other for the individual years results
        self.vertical_layout = QVBoxLayout()
        self.setLayout(self.vertical_layout)
        self.vertical_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        # Holds the spin box
        self.top_container = QWidget()
        self.vertical_layout.addWidget(self.top_container)
        self.top_horizontal_layout = QHBoxLayout()
        self.top_container.setLayout(self.top_horizontal_layout)

        self.critical_container = QWidget()
        self.critical_layout = QFormLayout()
        self.critical_container.setLayout(self.critical_layout)
        self.spin_box = MackCriticalSpinBox(
            starting_value=MACK_VALUATION_CRITICAL
        )

        self.critical_layout.addRow(
            "Critical Value: ",
            self.spin_box
        )

        self.top_horizontal_layout.addWidget(
            self.critical_container,
            stretch=0
        )

        # Holds the individual years results
        self.individual_layout = QHBoxLayout()
        self.individual_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )
        self.individual_container = QWidget()
        self.individual_container.setLayout(self.individual_layout)
        self.individual_right_padding = QWidget()
        self.individual_left_padding = QWidget()
        self.individual_left_padding.setFixedWidth(20)
        self.individual_model = MackValuationModel(
            triangle=self.triangle,
            critical=self.spin_box
        )

        self.individual_view = MackValuationView()
        self.individual_view.setModel(self.individual_model)

        self.mv_max_individual_width = self.individual_view.horizontalHeader().length() + \
            self.individual_view.verticalHeader().width() + 2

        self.individual_view.setFixedHeight(132)
        self.individual_view.setMaximumWidth(
            self.mv_max_individual_width
        )

        self.individual_layout.addWidget(
            self.individual_left_padding,
            stretch=0
        )

        self.individual_layout.addWidget(
            self.individual_view,
            stretch=0
        )

        self.individual_layout.addWidget(
            self.individual_right_padding,
            stretch=0
        )

        self.vertical_layout.addWidget(
            self.individual_container
        )

        self.vertical_padding_widget = QWidget()
        self.vertical_layout.addWidget(
            self.vertical_padding_widget
        )