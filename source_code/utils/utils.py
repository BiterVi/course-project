import json

from PyQt5.QtWidgets import QTableWidgetItem


class Utils:
    @staticmethod
    def save_to_json(file_path: str, data):
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    @staticmethod
    def fill_table(table, data, column_index):
        for index, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            table.setItem(index, column_index, item)
