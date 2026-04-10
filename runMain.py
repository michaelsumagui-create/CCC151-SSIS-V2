import sys
import math

import kelwxy_db as db
from model import config_file

from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QDialog, QTableWidgetItem,
    QPushButton, QWidget, QHBoxLayout, QMessageBox, QLabel
)
from PyQt6 import QtWidgets, QtCore

from _addFolder.addCollege import add_College
from _addFolder.addProgram import add_Program
from _addFolder.addStudent import add_Student

from _updateFolder.updateCollege import update_College
from _updateFolder.updateProgram import update_Program
from _updateFolder.updateStudent import update_Student

from _loginFolder.loginDialog import login_Dialog

from deleteConfirm import delete_Confirm
from mainWindow import main_Window


#  Credentials

CREDENTIALS = {
    "Admin": {"username": "admin", "password": "admin123"},
    "User":  {"username": "user",  "password": "user123"},
}


#  Helper: populate a QComboBox from a list of strings

def load_combobox(combobox, items):
    combobox.clear()
    for item in items:
        combobox.addItem(item)


#  Login

class Login_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = login_Dialog()
        self.ui.setupUi(self)
        self.role = None
        self.ui.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        username = self.ui.username_input.text().strip()
        password = self.ui.password_input.text().strip()
        role     = self.ui.role_comboBox.currentText()

        creds = CREDENTIALS.get(role)
        if creds and username == creds["username"] and password == creds["password"]:
            self.role = role
            self.accept()
        else:
            self.ui.error_label.setText("Invalid username or password.")


#  Add dialogs

class Add_College_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = add_College()
        self.ui.setupUi(self)
        self.ui.Save_button.clicked.connect(self.save_college)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_college(self):
        code = self.ui.CollegeCode_input.text().strip()
        name = self.ui.CollegeName_input.text().strip()

        if not code or not name:
            return QMessageBox.warning(self, "Error", "All fields must be filled out.")
        if db.college_exists(code):
            return QMessageBox.warning(self, "Error", "College code already exists.")
        if db.college_name_exists(name):
            return QMessageBox.warning(self, "Error", "College name already exists.")

        db.add_college(code, name)
        self.parent().load_table(self.parent().college_table, "COLLEGES")
        self.accept()


class Add_Program_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = add_Program()
        self.ui.setupUi(self)
        load_combobox(self.ui.college_code_input_comboBox, db.get_all_college_codes())
        self.ui.Save_button.clicked.connect(self.save_program)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_program(self):
        code    = self.ui.ProgramCode_input.text().strip()
        name    = self.ui.ProgramName_input.text().strip()
        college = self.ui.college_code_input_comboBox.currentText()

        if not code or not name or not college:
            return QMessageBox.warning(self, "Error", "All fields must be filled.")
        if db.program_name_exists(name):
            return QMessageBox.warning(self, "Error", "Program name already exists.")
        if db.program_exists(code):
            return QMessageBox.warning(self, "Error", "Program code already exists.")

        db.add_program(code, name, college)
        self.parent().load_table(self.parent().program_table, "PROGRAMS")
        self.accept()


class Add_Student_Dialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = add_Student()
        self.ui.setupUi(self)
        load_combobox(self.ui.program_code_input_comboBox, db.get_all_program_codes())
        self.ui.Save_button.clicked.connect(self.save_student)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_student(self):
        id_number    = self.ui.id_number_input.text().strip()
        first_name   = self.ui.first_name_input.text().strip()
        last_name    = self.ui.last_name_input.text().strip()
        gender       = self.ui.gender_comboBox.currentText()
        year_level   = self.ui.year_level_comboBox.currentText()
        program_code = self.ui.program_code_input_comboBox.currentText()

        if not all([id_number, first_name, last_name, gender, year_level, program_code]):
            return QMessageBox.warning(self, "Input Error", "All fields must be filled out.")
        if db.student_exists(id_number):
            return QMessageBox.warning(self, "Error", "ID Number already exists.")

        db.add_student(id_number, first_name, last_name, gender, int(year_level), program_code)
        self.parent().load_table(self.parent().student_table, "STUDENTS")
        self.accept()


#  Edit dialogs

class Edit_College_Dialog(QDialog):
    def __init__(self, parent, row_data):
        super().__init__(parent)
        self.ui = update_College()
        self.ui.setupUi(self)
        self._parent           = parent
        self.old_college_code  = row_data["college_code"]
        self.old_college_name  = row_data["college_name"]
        self.ui.college_code_input.setText(self.old_college_code)
        self.ui.college_name_input.setText(self.old_college_name)
        self.ui.Save_button.clicked.connect(self.save_changes)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_changes(self):
        new_code = self.ui.college_code_input.text().strip()
        new_name = self.ui.college_name_input.text().strip()

        if not new_code or not new_name:
            return QMessageBox.warning(self, "Error", "Fields cannot be empty.")
        if new_code != self.old_college_code and db.college_exists(new_code):
            return QMessageBox.warning(self, "Error", "College code already exists.")
        if new_name != self.old_college_name and db.college_name_exists(new_name):
            return QMessageBox.warning(self, "Error", "College name already exists.")

        db.update_college(self.old_college_code, new_code, new_name)
        self._parent.load_table(self._parent.college_table, "COLLEGES")
        self._parent.load_table(self._parent.program_table, "PROGRAMS")
        self.accept()


class Edit_Program_Dialog(QDialog):
    def __init__(self, parent, row_data):
        super().__init__(parent)
        self.ui = update_Program()
        self.ui.setupUi(self)
        self._parent          = parent
        self.old_program_code = row_data["program_code"]
        self.old_program_name = row_data["program_name"]
        load_combobox(self.ui.college_code_input_comboBox, db.get_all_college_codes())
        self.ui.program_code_input.setText(self.old_program_code)
        self.ui.program_name_input.setText(self.old_program_name)
        self.ui.college_code_input_comboBox.setCurrentText(row_data["college_code"])
        self.ui.Save_button.clicked.connect(self.save_changes)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_changes(self):
        new_code    = self.ui.program_code_input.text().strip()
        new_name    = self.ui.program_name_input.text().strip()
        new_college = self.ui.college_code_input_comboBox.currentText()

        if not new_code or not new_name or not new_college:
            return QMessageBox.warning(self, "Error", "All fields must not be empty.")
        if new_code != self.old_program_code and db.program_exists(new_code):
            return QMessageBox.warning(self, "Error", "Program code already exists.")
        if new_name != self.old_program_name and db.program_name_exists(new_name):
            return QMessageBox.warning(self, "Error", "Program name already exists.")

        db.update_program(self.old_program_code, new_code, new_name, new_college)
        self._parent.load_table(self._parent.program_table, "PROGRAMS")
        self._parent.load_table(self._parent.student_table, "STUDENTS")
        self.accept()


class Edit_Student_Dialog(QDialog):
    def __init__(self, parent, row_data):
        super().__init__(parent)
        self.ui = update_Student()
        self.ui.setupUi(self)
        self._parent      = parent
        self.old_id       = row_data["id_number"]
        load_combobox(self.ui.program_code_input_comboBox, db.get_all_program_codes())
        self.ui.id_number_input.setText(row_data["id_number"])
        self.ui.first_name_input.setText(row_data["first_name"])
        self.ui.last_name_input.setText(row_data["last_name"])
        self.ui.gender_comboBox.setCurrentText(row_data["gender"])
        self.ui.year_level_comboBox.setCurrentText(str(row_data["year_level"]))
        self.ui.program_code_input_comboBox.setCurrentText(row_data["program_code"] or "")
        self.ui.Save_button.clicked.connect(self.save_changes)
        self.ui.Cancel_button.clicked.connect(self.reject)

    def save_changes(self):
        new_id      = self.ui.id_number_input.text().strip()
        new_first   = self.ui.first_name_input.text().strip()
        new_last    = self.ui.last_name_input.text().strip()
        new_gender  = self.ui.gender_comboBox.currentText()
        new_year    = self.ui.year_level_comboBox.currentText()
        new_program = self.ui.program_code_input_comboBox.currentText()

        if not all([new_id, new_first, new_last, new_gender, new_year, new_program]):
            return QMessageBox.warning(self, "Error", "All fields must not be empty.")
        if new_id != self.old_id and db.student_exists(new_id):
            return QMessageBox.warning(self, "Error", "ID Number already exists.")

        db.update_student(self.old_id, new_id, new_first, new_last,
                          new_gender, int(new_year), new_program)
        self._parent.load_table(self._parent.student_table, "STUDENTS")
        self.accept()


#  Delete confirmation

class DeleteItemConfirmation(QDialog):
    def __init__(self, count=1):
        super().__init__()
        self.ui = delete_Confirm()
        self.ui.setupUi(self)
        if count > 1:
            self.ui.Text.setText(f"Are you sure you want to delete {count} selected row(s)?")
        self.ui.Confirm.clicked.connect(self.accept)
        self.ui.Cancel.clicked.connect(self.reject)


#  Main window

class MainWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()
        self.role     = role
        self.is_admin = role == "Admin"
        self.ui       = main_Window()
        self.ui.setupUi(self)

        # Sort state per table
        self.student_sort_col  = "id_number";    self.student_sort_order = "ASC"
        self.program_sort_col  = "program_code"; self.program_sort_order = "ASC"
        self.college_sort_col  = "college_code"; self.college_sort_order = "ASC"

        # Pagination state per table
        self.student_page = 1;  self.student_total_pages = 1
        self.program_page = 1;  self.program_total_pages = 1
        self.college_page = 1;  self.college_total_pages = 1

        # Active search state per table (preserved across page turns)
        self.student_search = "";  self.student_search_field = "id_number"
        self.program_search = "";  self.program_search_field = "program_code"
        self.college_search = "";  self.college_search_field = "college_code"

        # Table aliases
        self.student_table = self.ui.tableWidget
        self.program_table = self.ui.tableWidget_2
        self.college_table = self.ui.tableWidget_3

        # Table settings
        for table in [self.student_table, self.program_table, self.college_table]:
            table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
            table.itemSelectionChanged.connect(self.update_bulk_buttons)
            table.mousePressEvent = lambda event, t=table: self._handle_table_click(event, t)

        # Sidebar navigation
        self.ui.students_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.programs_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.colleges_button.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(2))
        self.ui.stackedWidget.currentChanged.connect(self.on_page_changed)
        self.ui.exit_button.clicked.connect(QApplication.instance().quit)

        # Search
        self.ui.search_text.textChanged.connect(self.search_table)

        # Sort combos
        self.ui.comboBox.currentIndexChanged.connect(self.sort_table)
        self.ui.comboBox_2.currentIndexChanged.connect(self.sort_table)
        self.ui.comboBox_3.currentIndexChanged.connect(self.sort_table)

        # Pagination signals — Students
        self.ui.student_first_button.clicked.connect(lambda: self._go_to_page("STUDENTS", 1))
        self.ui.student_prev_button.clicked.connect(lambda: self._go_to_page("STUDENTS", self.student_page - 1))
        self.ui.student_next_button.clicked.connect(lambda: self._go_to_page("STUDENTS", self.student_page + 1))
        self.ui.student_last_button.clicked.connect(lambda: self._go_to_page("STUDENTS", self.student_total_pages))
        self.ui.student_page_size_comboBox.currentTextChanged.connect(lambda: self._on_page_size_changed("STUDENTS"))

        # Pagination signals — Programs
        self.ui.program_first_button.clicked.connect(lambda: self._go_to_page("PROGRAMS", 1))
        self.ui.program_prev_button.clicked.connect(lambda: self._go_to_page("PROGRAMS", self.program_page - 1))
        self.ui.program_next_button.clicked.connect(lambda: self._go_to_page("PROGRAMS", self.program_page + 1))
        self.ui.program_last_button.clicked.connect(lambda: self._go_to_page("PROGRAMS", self.program_total_pages))
        self.ui.program_page_size_comboBox.currentTextChanged.connect(lambda: self._on_page_size_changed("PROGRAMS"))

        # Pagination signals — Colleges
        self.ui.college_first_button.clicked.connect(lambda: self._go_to_page("COLLEGES", 1))
        self.ui.college_prev_button.clicked.connect(lambda: self._go_to_page("COLLEGES", self.college_page - 1))
        self.ui.college_next_button.clicked.connect(lambda: self._go_to_page("COLLEGES", self.college_page + 1))
        self.ui.college_last_button.clicked.connect(lambda: self._go_to_page("COLLEGES", self.college_total_pages))
        self.ui.college_page_size_comboBox.currentTextChanged.connect(lambda: self._on_page_size_changed("COLLEGES"))

        # Admin-only: Add buttons + bulk action buttons
        if self.is_admin:
            self.ui.addstudent_button.clicked.connect(self.open_add_student_dialog)
            self.ui.addprogram_button.clicked.connect(self.open_add_program_dialog)
            self.ui.addcollege_button.clicked.connect(self.open_add_college_dialog)
            self._setup_bulk_buttons()
        else:
            self.ui.addstudent_button.setVisible(False)
            self.ui.addprogram_button.setVisible(False)
            self.ui.addcollege_button.setVisible(False)

        # Initial table load
        self.load_table(self.student_table, "STUDENTS")
        self.load_table(self.program_table,  "PROGRAMS")
        self.load_table(self.college_table,  "COLLEGES")

    #  Pagination helpers

    def _page_size(self, table_type):
        return int({
            "STUDENTS": self.ui.student_page_size_comboBox,
            "PROGRAMS": self.ui.program_page_size_comboBox,
            "COLLEGES": self.ui.college_page_size_comboBox,
        }[table_type].currentText())

    def _go_to_page(self, table_type, page):
        total = {
            "STUDENTS": self.student_total_pages,
            "PROGRAMS": self.program_total_pages,
            "COLLEGES": self.college_total_pages,
        }[table_type]

        page = max(1, min(page, total))  # clamp within valid range

        if table_type == "STUDENTS":
            self.student_page = page
        elif table_type == "PROGRAMS":
            self.program_page = page
        elif table_type == "COLLEGES":
            self.college_page = page

        search, search_field = {
            "STUDENTS": (self.student_search, self.student_search_field),
            "PROGRAMS": (self.program_search, self.program_search_field),
            "COLLEGES": (self.college_search, self.college_search_field),
        }[table_type]

        table = {
            "STUDENTS": self.student_table,
            "PROGRAMS": self.program_table,
            "COLLEGES": self.college_table,
        }[table_type]

        self.load_table(table, table_type, search=search, search_field=search_field)

    def _on_page_size_changed(self, table_type):
        """Reset to page 1 when the rows-per-page selector changes."""
        if table_type == "STUDENTS":
            self.student_page = 1
        elif table_type == "PROGRAMS":
            self.program_page = 1
        elif table_type == "COLLEGES":
            self.college_page = 1
        self._go_to_page(table_type, 1)

    def _update_pagination_controls(self, table_type, current_page, total_pages, total_records):
        """Refresh page label, total label, and enabled state of nav buttons."""
        if table_type == "STUDENTS":
            self.student_total_pages = total_pages
            self.ui.student_page_label.setText(f"Page {current_page} of {total_pages}")
            self.ui.student_total_label.setText(f"Total: {total_records}")
            self.ui.student_first_button.setEnabled(current_page > 1)
            self.ui.student_prev_button.setEnabled(current_page > 1)
            self.ui.student_next_button.setEnabled(current_page < total_pages)
            self.ui.student_last_button.setEnabled(current_page < total_pages)
        elif table_type == "PROGRAMS":
            self.program_total_pages = total_pages
            self.ui.program_page_label.setText(f"Page {current_page} of {total_pages}")
            self.ui.program_total_label.setText(f"Total: {total_records}")
            self.ui.program_first_button.setEnabled(current_page > 1)
            self.ui.program_prev_button.setEnabled(current_page > 1)
            self.ui.program_next_button.setEnabled(current_page < total_pages)
            self.ui.program_last_button.setEnabled(current_page < total_pages)
        elif table_type == "COLLEGES":
            self.college_total_pages = total_pages
            self.ui.college_page_label.setText(f"Page {current_page} of {total_pages}")
            self.ui.college_total_label.setText(f"Total: {total_records}")
            self.ui.college_first_button.setEnabled(current_page > 1)
            self.ui.college_prev_button.setEnabled(current_page > 1)
            self.ui.college_next_button.setEnabled(current_page < total_pages)
            self.ui.college_last_button.setEnabled(current_page < total_pages)

    #  Core table loader

    def load_table(self, table_widget, table_type, search="", search_field=None):
        list_fn_map = {
            "STUDENTS": db.list_students,
            "PROGRAMS": db.list_programs,
            "COLLEGES": db.list_colleges,
        }
        sort_map = {
            "STUDENTS": (self.student_sort_col, self.student_sort_order),
            "PROGRAMS": (self.program_sort_col, self.program_sort_order),
            "COLLEGES": (self.college_sort_col, self.college_sort_order),
        }
        page_map = {
            "STUDENTS": self.student_page,
            "PROGRAMS": self.program_page,
            "COLLEGES": self.college_page,
        }

        sort_col, sort_order = sort_map[table_type]
        page      = page_map[table_type]
        page_size = self._page_size(table_type)

        fields = [h[0] for h in config_file.header_names[table_type]]
        sf     = search_field if search_field else fields[0]

        result        = list_fn_map[table_type](
            search=search, search_field=sf,
            sort_col=sort_col, sort_order=sort_order,
            page=page, page_size=page_size
        )
        total_records = result["total"]
        total_pages   = max(1, math.ceil(total_records / page_size))

        # If current page exceeds total (e.g. after delete), clamp and reload
        if page > total_pages:
            if table_type == "STUDENTS":
                self.student_page = total_pages
            elif table_type == "PROGRAMS":
                self.program_page = total_pages
            elif table_type == "COLLEGES":
                self.college_page = total_pages
            return self.load_table(table_widget, table_type, search=search, search_field=sf)

        self._update_pagination_controls(table_type, page, total_pages, total_records)

        readable_headers = [h[1] for h in config_file.header_names[table_type]]
        table_widget.setHorizontalHeaderLabels(readable_headers + ["Actions"])
        table_widget.setRowCount(len(result["data"]))

        for row_index, row in enumerate(result["data"]):
            for col_index, key in enumerate(fields):
                value = row.get(key)
                table_widget.setItem(
                    row_index, col_index,
                    QTableWidgetItem(str(value) if value is not None else "")
                )

            action_widget = QWidget()
            layout = QHBoxLayout(action_widget)
            layout.setContentsMargins(0, 0, 0, 0)

            if self.is_admin:
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(
                    lambda _, r=dict(row), tt=table_type: self.edit_row_db(r, tt)
                )
                del_btn = QPushButton("Delete")
                del_btn.clicked.connect(
                    lambda _, r=dict(row), tt=table_type, tw=table_widget: self.confirm_delete_db([r], tt, tw)
                )
                layout.addWidget(edit_btn)
                layout.addWidget(del_btn)
            else:
                lbl = QLabel("View Only")
                lbl.setStyleSheet("color: gray; font-style: italic;")
                layout.addWidget(lbl)

            table_widget.setCellWidget(row_index, len(readable_headers), action_widget)

    #  Edit

    def edit_row_db(self, row_data, table_type):
        dialog_map = {
            "STUDENTS": Edit_Student_Dialog,
            "PROGRAMS": Edit_Program_Dialog,
            "COLLEGES": Edit_College_Dialog,
        }
        dialog_map[table_type](self, row_data).exec()

    #  Delete

    def confirm_delete_db(self, rows_data, table_type, table_widget):
        if DeleteItemConfirmation(count=len(rows_data)).exec() != QDialog.DialogCode.Accepted:
            return

        pk_map  = {"STUDENTS": "id_number", "PROGRAMS": "program_code", "COLLEGES": "college_code"}
        del_map = {"STUDENTS": db.delete_student, "PROGRAMS": db.delete_program, "COLLEGES": db.delete_college}

        for row in rows_data:
            del_map[table_type](row[pk_map[table_type]])

        self.load_table(table_widget, table_type)
        if table_type == "COLLEGES":
            self.load_table(self.program_table, "PROGRAMS")
            self.load_table(self.student_table, "STUDENTS")
        elif table_type == "PROGRAMS":
            self.load_table(self.student_table, "STUDENTS")

        self.update_bulk_buttons()

    #  Bulk action button setup

    def _setup_bulk_buttons(self):
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(4, 0, 4, 0)

        self.selection_label = QLabel("0 selected")
        self.selection_label.setStyleSheet("color: gray; font-style: italic;")

        self.bulk_edit_btn = QPushButton("✏ Edit Selected")
        self.bulk_edit_btn.setEnabled(False)
        self.bulk_edit_btn.setStyleSheet(
            "QPushButton { background-color: #2980b9; color: white; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:disabled { background-color: #95a5a6; }"
        )
        self.bulk_edit_btn.clicked.connect(self.bulk_edit_selected)

        self.bulk_delete_btn = QPushButton("🗑 Delete Selected")
        self.bulk_delete_btn.setEnabled(False)
        self.bulk_delete_btn.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: white; border-radius: 4px; padding: 4px 10px; }"
            "QPushButton:disabled { background-color: #95a5a6; }"
        )
        self.bulk_delete_btn.clicked.connect(self.bulk_delete_selected)

        status_layout.addWidget(self.selection_label)
        status_layout.addWidget(self.bulk_edit_btn)
        status_layout.addWidget(self.bulk_delete_btn)
        self.statusBar().addPermanentWidget(status_widget)

    #  Bulk helpers

    def _active_table_info(self):
        index = self.ui.stackedWidget.currentIndex()
        return {
            0: (self.student_table, "STUDENTS"),
            1: (self.program_table, "PROGRAMS"),
            2: (self.college_table, "COLLEGES"),
        }.get(index, (None, None))

    def _selected_rows(self, table_widget):
        return sorted(set(idx.row() for idx in table_widget.selectedIndexes()))

    def _row_data_from_table(self, table_widget, row_index, table_type):
        fields = [h[0] for h in config_file.header_names[table_type]]
        return {
            fields[col]: (table_widget.item(row_index, col).text()
                          if table_widget.item(row_index, col) else "")
            for col in range(len(fields))
        }

    def update_bulk_buttons(self):
        if not self.is_admin:
            return
        table, _ = self._active_table_info()
        if table is None:
            return
        count = len(self._selected_rows(table))
        self.selection_label.setText(f"{count} selected" if count else "0 selected")
        self.bulk_edit_btn.setEnabled(count > 0)
        self.bulk_delete_btn.setEnabled(count > 0)

    def _handle_table_click(self, event, table):
        from PyQt6.QtCore import Qt
        index     = table.indexAt(event.pos())
        modifiers = event.modifiers()
        ctrl  = Qt.KeyboardModifier.ControlModifier
        shift = Qt.KeyboardModifier.ShiftModifier

        if index.isValid() and not (modifiers & ctrl) and not (modifiers & shift):
            selected = self._selected_rows(table)
            if index.row() in selected and len(selected) == 1:
                table.clearSelection()
                return
            if index.row() in selected and len(selected) > 1:
                for col in range(table.columnCount()):
                    item = table.item(index.row(), col)
                    if item:
                        item.setSelected(False)
                return

        QtWidgets.QTableWidget.mousePressEvent(table, event)

    def bulk_edit_selected(self):
        table, table_type = self._active_table_info()
        if table is None:
            return
        rows = self._selected_rows(table)
        if not rows:
            return

        if len(rows) > 1:
            reply = QMessageBox.question(
                self, "Edit Multiple Rows",
                f"You selected {len(rows)} row(s). An edit dialog will open for each. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        for row_index in rows:
            row_data = self._row_data_from_table(table, row_index, table_type)
            self.edit_row_db(row_data, table_type)

        self.load_table(table, table_type)
        self.update_bulk_buttons()

    def bulk_delete_selected(self):
        table, table_type = self._active_table_info()
        if table is None:
            return
        rows = self._selected_rows(table)
        if not rows:
            return

        rows_data = [self._row_data_from_table(table, r, table_type) for r in rows]
        self.confirm_delete_db(rows_data, table_type, table)

    #  Open Add dialogs

    def open_add_student_dialog(self):
        Add_Student_Dialog(self).exec()

    def open_add_program_dialog(self):
        Add_Program_Dialog(self).exec()

    def open_add_college_dialog(self):
        Add_College_Dialog(self).exec()

    #  Search

    def search_table(self):
        search_text   = self.ui.search_text.text().strip()
        current_index = self.ui.stackedWidget.currentIndex()

        table_map = {
            0: (self.student_table, "STUDENTS",
                ["id_number", "first_name", "last_name", "gender", "year_level", "program_code"]),
            1: (self.program_table, "PROGRAMS",
                ["program_code", "program_name", "college_code"]),
            2: (self.college_table, "COLLEGES",
                ["college_code", "college_name"]),
        }
        if current_index not in table_map:
            return

        table_widget, table_type, fields = table_map[current_index]
        offset_map   = {0: 1, 1: 4, 2: 6}
        col          = self.ui.SearchFilters.currentIndex() - offset_map[current_index]
        search_field = fields[col] if 0 <= col < len(fields) else fields[0]

        # Save search state and reset to page 1
        if table_type == "STUDENTS":
            self.student_search = search_text
            self.student_search_field = search_field
            self.student_page = 1
        elif table_type == "PROGRAMS":
            self.program_search = search_text
            self.program_search_field = search_field
            self.program_page = 1
        elif table_type == "COLLEGES":
            self.college_search = search_text
            self.college_search_field = search_field
            self.college_page = 1

        self.load_table(table_widget, table_type,
                        search=search_text, search_field=search_field)

    #  Sort

    def sort_table(self):
        current_index = self.ui.stackedWidget.currentIndex()

        config_map = {
            0: (self.student_table, "STUDENTS", self.ui.comboBox, {
                1: ("first_name",   "ASC"),  2: ("first_name",   "DESC"),
                3: ("last_name",    "ASC"),  4: ("last_name",    "DESC"),
                5: ("id_number",    "ASC"),  6: ("id_number",    "DESC"),
            }),
            1: (self.program_table, "PROGRAMS", self.ui.comboBox_2, {
                1: ("program_code", "ASC"),  2: ("program_code", "DESC"),
                3: ("program_name", "ASC"),  4: ("program_name", "DESC"),
                5: ("college_code", "ASC"),  6: ("college_code", "DESC"),
            }),
            2: (self.college_table, "COLLEGES", self.ui.comboBox_3, {
                1: ("college_code", "ASC"),  2: ("college_code", "DESC"),
                3: ("college_name", "ASC"),  4: ("college_name", "DESC"),
            }),
        }

        if current_index not in config_map:
            return

        table_widget, table_type, combo, sort_mapping = config_map[current_index]
        selected = combo.currentIndex()

        if selected in sort_mapping:
            col, order = sort_mapping[selected]
            if table_type == "STUDENTS":
                self.student_sort_col, self.student_sort_order = col, order
                self.student_page = 1
            elif table_type == "PROGRAMS":
                self.program_sort_col, self.program_sort_order = col, order
                self.program_page = 1
            elif table_type == "COLLEGES":
                self.college_sort_col, self.college_sort_order = col, order
                self.college_page = 1

        self.load_table(table_widget, table_type)

    #  Page change (tab switch)

    def on_page_changed(self, index):
        self.ui.SearchFilters.setCurrentIndex({0: 1, 1: 4, 2: 6}.get(index, 0))
        self.update_bulk_buttons()

#  Entry point

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Initialise database (creates kelwxy.db and seeds it on first run)
    db.setup()

    login = Login_Dialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow(role=login.role)
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)