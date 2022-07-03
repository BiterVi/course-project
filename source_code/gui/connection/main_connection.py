from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database import models
from gui.windows import main_window


class MainWindow(QtWidgets.QMainWindow, main_window.Ui_MainWindow):
    def __init__(self, database, config, utils, excel):
        super(MainWindow, self).__init__()
        self.setupUi(self)

        self.database = database
        self.config = config
        self.utils = utils
        self.excel = excel

        self.add_table.clicked.connect(self.show_add_page)
        self.open_table.clicked.connect(self.show_table)
        self.change_table.clicked.connect(self.show_choice_page)

        self.back_button.clicked.connect(self.to_back_page)
        self.back_button_2.clicked.connect(self.to_back_page)
        self.back_button_3.clicked.connect(self.to_back_page)
        self.back_button_4.clicked.connect(self.to_back_page)
        self.back_button_5.clicked.connect(self.to_back_page)
        self.back_button_6.clicked.connect(self.to_back_page)
        self.back_button_7.clicked.connect(self.to_back_page)

        self.select_table.clear()
        self.select_table.addItems(self.database.get_tables_name())

        self.add_cargo_button.clicked.connect(self.add_elements)
        self.add_rack_button.clicked.connect(self.add_elements)
        self.add_position_button.clicked.connect(self.add_elements)

        self.delete_table.clicked.connect(self.fill_list)
        self.delete_button.clicked.connect(self.delete_by_id)

        self.open_change.clicked.connect(self.show_change_page)
        self.change_button.clicked.connect(self.change_elements)

        self.save_table.clicked.connect(self.show_output_page)
        self.output_button.clicked.connect(self.output_to_file)

    def to_back_page(self):
        self.stackedWidget.setCurrentIndex(0)

    def show_output_page(self):
        self.stackedWidget.setCurrentIndex(7)

    def output_to_file(self):
        select_extension = self.select_extension.currentText()
        select_output_type = self.select_output_type.currentText()
        select_table = self.select_table.currentText()
        output_templates = self.config.get_output_templates(self.database, select_table, select_extension,
                                                            select_output_type)

        if select_extension == "EXCEL":
            self.output_to_excel(*output_templates)
        elif select_extension == "JSON":
            self.output_to_json(*output_templates)

    def output_to_json(self, data_from_database, fields):
        data = []

        for row in data_from_database:
            data.append({key: value for key, value in zip(tuple(fields), row)})

        file_path = QFileDialog.getOpenFileName(self, "Выбор JSON-файла", "./", "Image(*.json)")[0]

        if file_path:
            self.utils.save_to_json(file_path, data)
            self.to_back_page()

    def output_to_excel(self, data_from_database, header, fields):
        self.excel.create_workbook()
        file_path = QFileDialog.getOpenFileName(self, "Выбор EXCEL-файла", "./", "Image(*.xlsx)")[0]

        if file_path:
            self.excel.sheet.title = header
            self.excel.sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(data_from_database[0]))

            self.excel.sheet["A1"] = header
            self.excel.set_sheet_styles(1)

            self.excel.sheet.append(fields)
            self.excel.set_sheet_styles(2)

            for index, value in enumerate(data_from_database, 3):
                self.excel.sheet.append(tuple(map(str, value)))

                for cell in self.excel.sheet[index]:
                    cell.border = self.excel.full_border
                    cell.alignment = self.excel.alignment_center

            try:
                self.excel.workbook.save(filename=file_path)
                self.to_back_page()
            except PermissionError:
                QMessageBox.warning(self, "ОШИБКА", "Закройте выбранный файл")

    def change_elements(self):
        table = self.config.get_table_fields(self.select_table.currentText())
        type_change = table[self.type_change.currentText()]
        id_change = int(self.id_change.currentText())
        new_change = self.new_change.toPlainText()

        with Session(self.database.engine) as session:
            session.query(table["default"]).filter(table["default"].id == id_change).update({type_change: new_change})
            session.commit()
        self.to_back_page()

    def show_change_page(self):
        self.id_select_change.clear()
        self.type_select_change.clear()
        self.new_change.clear()

        id_change = self.id_change.currentText()
        select_table = self.select_table.currentText()
        type_change = self.type_change.currentText()
        current_table = self.config.get_table_fields(select_table)
        new_change_text = self.database.select_query(select(current_table[type_change]
                                                            ).where(current_table["default"].id == id_change), 2)

        self.new_change.setText(str(new_change_text))
        self.id_select_change.setText(f"ID: {id_change}")
        self.type_select_change.setText(f"Изменяемое поле: {type_change}")

        self.stackedWidget.setCurrentIndex(6)

    def show_choice_page(self):
        self.id_change.clear()
        self.type_change.clear()

        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]

        ids = [str(index) for index in self.database.select_query(select(current_table.id), 1)]
        types = [column.key for column in current_table.__table__.columns if column.key.find("id") == -1]

        self.id_change.addItems(ids)
        self.type_change.addItems(types)

        self.stackedWidget.setCurrentIndex(5)

    def delete_by_id(self):
        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]
        id_input_delete = self.id_input_delete.text()

        self.database.engine_connect(delete(current_table).where(current_table.id == id_input_delete))
        self.to_back_page()

    def fill_list(self):
        self.id_list_delete.clear()

        select_table = self.select_table.currentText()
        current_table = self.config.get_table_fields(select_table)["default"]

        self.id_list_delete.addItems([str(index) for index in self.database.select_query(select(current_table.id), 1)])
        self.stackedWidget.setCurrentIndex(4)

    def show_table(self):
        if self.select_table.currentText() == "shelving":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Rack.id), 1)
            numbers = self.database.select_query(select(models.Rack.number), 1)
            numbers_cells = self.database.select_query(select(models.Rack.number_cells), 1)
            max_weights = self.database.select_query(select(models.Rack.max_weight), 1)

            self.table_data.setColumnCount(4)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, numbers, 1)
            self.utils.fill_table(self.table_data, numbers_cells, 2)
            self.utils.fill_table(self.table_data, max_weights, 3)

        elif self.select_table.currentText() == "cargo":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Cargo.id), 1)
            names = self.database.select_query(select(models.Cargo.name), 1)

            self.table_data.setColumnCount(2)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, names, 1)

        elif self.select_table.currentText() == "positions":
            self.table_data.clear()

            ids = self.database.select_query(select(models.Position.id), 1)
            cargo_ids = self.database.select_query(select(models.Position.cargo_id), 1)
            rack_ids = self.database.select_query(select(models.Position.rack_id), 1)
            cell_numbers = self.database.select_query(select(models.Position.cell_number), 1)
            weights = self.database.select_query(select(models.Position.weight), 1)
            dates = self.database.select_query(select(models.Position.date), 1)

            self.table_data.setColumnCount(6)
            self.table_data.setRowCount(len(ids))

            self.utils.fill_table(self.table_data, ids, 0)
            self.utils.fill_table(self.table_data, cargo_ids, 1)
            self.utils.fill_table(self.table_data, rack_ids, 2)
            self.utils.fill_table(self.table_data, cell_numbers, 3)
            self.utils.fill_table(self.table_data, weights, 4)
            self.utils.fill_table(self.table_data, dates, 5)

    def show_add_page(self):
        if self.select_table.currentText() == "shelving":
            self.id_rack.clear()
            self.number_rack.clear()
            self.number_cells_rack.clear()
            self.max_weight_rack.clear()

            self.id_rack.setText(self.database.get_last_index(models.Rack.id))

            self.stackedWidget.setCurrentIndex(1)

        elif self.select_table.currentText() == "cargo":
            self.id_cargo.clear()
            self.name_cargo.clear()

            self.id_cargo.setText(self.database.get_last_index(models.Cargo.id))

            self.stackedWidget.setCurrentIndex(2)

        elif self.select_table.currentText() == "positions":
            self.id_position.clear()
            self.id_cargo_position.clear()
            self.id_rack_position.clear()
            self.cell_number_position.clear()
            self.weight_cargo_position.clear()
            self.date_position.clear()

            self.id_position.setText(self.database.get_last_index(models.Position.id))
            self.id_cargo_position.addItems(self.database.select_query(select(models.Cargo.name), 1))
            self.id_rack_position.addItems(list(map(str, self.database.select_query(select(models.Rack.number), 1))))

            self.stackedWidget.setCurrentIndex(3)

    def add_elements(self):
        try:
            if self.select_table.currentText() == "shelving":
                id_rack = self.id_rack.text()
                number = self.number_rack.text()
                number_cells = self.number_cells_rack.text()
                max_weight = self.max_weight_rack.text()

                self.database.insert_query(models.Rack, id_rack, number, number_cells, max_weight)
                self.to_back_page()
                self.show_table()

            elif self.select_table.currentText() == "cargo":
                id_cargo = self.id_cargo.text()
                name = self.name_cargo.text()

                self.database.insert_query(models.Cargo, id_cargo, name)
                self.to_back_page()
                self.show_table()

            elif self.select_table.currentText() == "positions":
                id_position = self.id_position.text()

                id_cargo = int(self.database.select_query(
                    select(models.Cargo.id).where(models.Cargo.name == self.id_cargo_position.currentText()), 2))

                id_rack = int(self.database.select_query(
                    select(models.Rack.id).where(models.Rack.number == self.id_rack_position.currentText()), 2))

                cell_number = self.cell_number_position.text()
                weight_cargo = self.weight_cargo_position.text()
                date = self.date_position.text()

                self.database.insert_query(models.Position, id_position, id_cargo,
                                           id_rack, cell_number, weight_cargo, date)
                self.to_back_page()
                self.show_table()
        except TypeError:
            QMessageBox.warning(self, "ОШИБКА", "Заполните все поля")
