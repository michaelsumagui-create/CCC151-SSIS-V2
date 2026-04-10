from PyQt6 import QtCore, QtGui, QtWidgets


class main_Window(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowTitle("KELWXY - Student Information System")
        MainWindow.resize(1100, 749)
        MainWindow.setMinimumSize(QtCore.QSize(768, 576))

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)

        # ── LEFT SIDEBAR ──────────────────────────────────────────────────────
        self.sidebar_icon_with_description_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.sidebar_icon_with_description_widget)

        self.app_name_label = QtWidgets.QLabel("KELWXY")
        self.app_name_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: black; letter-spacing: 1px;"
        )
        self.verticalLayout_4.addWidget(self.app_name_label)

        self.divider_line = QtWidgets.QFrame()
        self.divider_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.divider_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.divider_line.setStyleSheet("color: black; margin-top: 4px; margin-bottom: 4px;")
        self.verticalLayout_4.addWidget(self.divider_line)

        self.students_button = QtWidgets.QPushButton("Students")
        self.verticalLayout_4.addWidget(self.students_button)

        self.programs_button = QtWidgets.QPushButton("Programs")
        self.verticalLayout_4.addWidget(self.programs_button)

        self.colleges_button = QtWidgets.QPushButton("Colleges")
        self.verticalLayout_4.addWidget(self.colleges_button)

        spacer = QtWidgets.QSpacerItem(
            20, 400,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        self.verticalLayout_4.addItem(spacer)

        self.exit_button = QtWidgets.QPushButton("Exit")
        self.exit_button.setStyleSheet("background-color: white; color: black;")
        self.verticalLayout_4.addWidget(self.exit_button)

        self.gridLayout.addWidget(self.sidebar_icon_with_description_widget, 0, 0, 1, 1)

        # ── MAIN CONTENT ──────────────────────────────────────────────────────
        self.information_display_widget = QtWidgets.QWidget(parent=self.centralwidget)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.information_display_widget)

        # Search bar
        self.search_text = QtWidgets.QLineEdit()
        self.search_text.setPlaceholderText("Search")
        self.verticalLayout_6.addWidget(self.search_text)

        self.SearchFilters = QtWidgets.QComboBox()
        self.SearchFilters.addItems([
            "--Search Filters--", "ID Number", "First Name", "Last Name",
            "Program Code", "Program Name", "College Code", "College Name"
        ])
        self.verticalLayout_6.addWidget(self.SearchFilters)

        # ── STACKED WIDGET ────────────────────────────────────────────────────
        self.stackedWidget = QtWidgets.QStackedWidget()

        # ── STUDENT PAGE ──────────────────────────────────────────────────────
        self.student_page = QtWidgets.QWidget()
        student_layout = QtWidgets.QVBoxLayout(self.student_page)

        self.students_label = QtWidgets.QLabel("Students Information")
        student_layout.addWidget(self.students_label)

        self.comboBox = QtWidgets.QComboBox()
        self.comboBox.addItems([
            "---Sort By---",
            "By First Name (A-Z)", "By First Name (Z-A)",
            "By Last Name (A-Z)",  "By Last Name (Z-A)",
            "By Student ID (Ascending)", "By Student ID (Descending)"
        ])
        student_layout.addWidget(self.comboBox)

        self.addstudent_button = QtWidgets.QPushButton("Add Student")
        self.addstudent_button.setStyleSheet("background-color: white; color: black;")
        student_layout.addWidget(self.addstudent_button)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnCount(7)
        student_layout.addWidget(self.tableWidget)

        # Student pagination controls
        self.student_pagination_widget = QtWidgets.QWidget()
        student_pagination_layout = QtWidgets.QHBoxLayout(self.student_pagination_widget)
        student_pagination_layout.setContentsMargins(0, 4, 0, 4)

        self.student_first_button = QtWidgets.QPushButton("⏮ First")
        self.student_prev_button  = QtWidgets.QPushButton("◀ Prev")
        self.student_page_label   = QtWidgets.QLabel("Page 1 of 1")
        self.student_page_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.student_next_button  = QtWidgets.QPushButton("Next ▶")
        self.student_last_button  = QtWidgets.QPushButton("Last ⏭")
        self.student_total_label  = QtWidgets.QLabel("Total: 0")
        self.student_total_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.student_page_size_comboBox = QtWidgets.QComboBox()
        self.student_page_size_comboBox.addItems(["20", "50", "100", "200"])
        self.student_page_size_comboBox.setCurrentText("20")
        self.student_page_size_comboBox.setFixedWidth(70)

        student_pagination_layout.addWidget(self.student_first_button)
        student_pagination_layout.addWidget(self.student_prev_button)
        student_pagination_layout.addWidget(self.student_page_label)
        student_pagination_layout.addWidget(self.student_next_button)
        student_pagination_layout.addWidget(self.student_last_button)
        student_pagination_layout.addStretch()
        student_pagination_layout.addWidget(QtWidgets.QLabel("Rows per page:"))
        student_pagination_layout.addWidget(self.student_page_size_comboBox)
        student_pagination_layout.addWidget(self.student_total_label)

        student_layout.addWidget(self.student_pagination_widget)
        self.stackedWidget.addWidget(self.student_page)

        # ── PROGRAMS PAGE ─────────────────────────────────────────────────────
        self.programs_page = QtWidgets.QWidget()
        program_layout = QtWidgets.QVBoxLayout(self.programs_page)

        self.programs_label = QtWidgets.QLabel("Programs")
        program_layout.addWidget(self.programs_label)

        self.comboBox_2 = QtWidgets.QComboBox()
        self.comboBox_2.addItems([
            "---Sort By---",
            "By Program Code (A-Z)", "By Program Code (Z-A)",
            "By Program Name (A-Z)", "By Program Name (Z-A)",
            "By College Code (A-Z)", "By College Code (Z-A)"
        ])
        program_layout.addWidget(self.comboBox_2)

        self.addprogram_button = QtWidgets.QPushButton("Add Program")
        self.addprogram_button.setStyleSheet("background-color: white; color: black;")
        program_layout.addWidget(self.addprogram_button)

        self.tableWidget_2 = QtWidgets.QTableWidget()
        self.tableWidget_2.setColumnCount(4)
        program_layout.addWidget(self.tableWidget_2)

        # Program pagination controls
        self.program_pagination_widget = QtWidgets.QWidget()
        program_pagination_layout = QtWidgets.QHBoxLayout(self.program_pagination_widget)
        program_pagination_layout.setContentsMargins(0, 4, 0, 4)

        self.program_first_button = QtWidgets.QPushButton("⏮ First")
        self.program_prev_button  = QtWidgets.QPushButton("◀ Prev")
        self.program_page_label   = QtWidgets.QLabel("Page 1 of 1")
        self.program_page_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.program_next_button  = QtWidgets.QPushButton("Next ▶")
        self.program_last_button  = QtWidgets.QPushButton("Last ⏭")
        self.program_total_label  = QtWidgets.QLabel("Total: 0")
        self.program_total_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.program_page_size_comboBox = QtWidgets.QComboBox()
        self.program_page_size_comboBox.addItems(["20", "50", "100", "200"])
        self.program_page_size_comboBox.setCurrentText("20")
        self.program_page_size_comboBox.setFixedWidth(70)

        program_pagination_layout.addWidget(self.program_first_button)
        program_pagination_layout.addWidget(self.program_prev_button)
        program_pagination_layout.addWidget(self.program_page_label)
        program_pagination_layout.addWidget(self.program_next_button)
        program_pagination_layout.addWidget(self.program_last_button)
        program_pagination_layout.addStretch()
        program_pagination_layout.addWidget(QtWidgets.QLabel("Rows per page:"))
        program_pagination_layout.addWidget(self.program_page_size_comboBox)
        program_pagination_layout.addWidget(self.program_total_label)

        program_layout.addWidget(self.program_pagination_widget)
        self.stackedWidget.addWidget(self.programs_page)

        # ── COLLEGES PAGE ─────────────────────────────────────────────────────
        self.colleges_page = QtWidgets.QWidget()
        college_layout = QtWidgets.QVBoxLayout(self.colleges_page)

        self.colleges_label = QtWidgets.QLabel("Colleges")
        college_layout.addWidget(self.colleges_label)

        self.comboBox_3 = QtWidgets.QComboBox()
        self.comboBox_3.addItems([
            "---Sort By---",
            "By College Code (A-Z)", "By College Code (Z-A)",
            "By College Name (A-Z)", "By College Name (Z-A)"
        ])
        college_layout.addWidget(self.comboBox_3)

        self.addcollege_button = QtWidgets.QPushButton("Add College")
        self.addcollege_button.setStyleSheet("background-color: white; color: black;")
        college_layout.addWidget(self.addcollege_button)

        self.tableWidget_3 = QtWidgets.QTableWidget()
        self.tableWidget_3.setColumnCount(3)
        college_layout.addWidget(self.tableWidget_3)

        # College pagination controls
        self.college_pagination_widget = QtWidgets.QWidget()
        college_pagination_layout = QtWidgets.QHBoxLayout(self.college_pagination_widget)
        college_pagination_layout.setContentsMargins(0, 4, 0, 4)

        self.college_first_button = QtWidgets.QPushButton("⏮ First")
        self.college_prev_button  = QtWidgets.QPushButton("◀ Prev")
        self.college_page_label   = QtWidgets.QLabel("Page 1 of 1")
        self.college_page_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.college_next_button  = QtWidgets.QPushButton("Next ▶")
        self.college_last_button  = QtWidgets.QPushButton("Last ⏭")
        self.college_total_label  = QtWidgets.QLabel("Total: 0")
        self.college_total_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.college_page_size_comboBox = QtWidgets.QComboBox()
        self.college_page_size_comboBox.addItems(["20", "50", "100", "200"])
        self.college_page_size_comboBox.setCurrentText("20")
        self.college_page_size_comboBox.setFixedWidth(70)

        college_pagination_layout.addWidget(self.college_first_button)
        college_pagination_layout.addWidget(self.college_prev_button)
        college_pagination_layout.addWidget(self.college_page_label)
        college_pagination_layout.addWidget(self.college_next_button)
        college_pagination_layout.addWidget(self.college_last_button)
        college_pagination_layout.addStretch()
        college_pagination_layout.addWidget(QtWidgets.QLabel("Rows per page:"))
        college_pagination_layout.addWidget(self.college_page_size_comboBox)
        college_pagination_layout.addWidget(self.college_total_label)

        college_layout.addWidget(self.college_pagination_widget)
        self.stackedWidget.addWidget(self.colleges_page)

        # ─────────────────────────────────────────────────────────────────────
        self.verticalLayout_6.addWidget(self.stackedWidget)
        self.gridLayout.addWidget(self.information_display_widget, 0, 1, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        # Navigation signals
        self.students_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.programs_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.colleges_button.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.exit_button.clicked.connect(MainWindow.close)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = main_Window()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())