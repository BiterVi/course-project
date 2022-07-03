from sqlalchemy import select

from database import models


class Config:
    @staticmethod
    def get_fields(table):
        table_fields = {
            "shelving": ["Код", "Номер", "Количество ячеек", "Допустимая масса"],
            "cargo": ["№", "Название"],
            "positions": ["№", "№ груза", "№ стеллажа", "№ ячейки", "Масса", "Дата укладки"],
            "free_cells": ["Свободные ячейки"],
            "filling_shelving": ["№ стеллажа", "Заполненность (%)"]
        }

        return table_fields[table]

    @staticmethod
    def get_table_fields(table):
        table_field_models = {
            "shelving": {
                "default": models.Rack,
                "number": models.Rack.number,
                "number_cells": models.Rack.number_cells,
                "max_weight": models.Rack.max_weight
            },
            "cargo": {
                "default": models.Cargo,
                "name": models.Cargo.name
            },
            "positions": {
                "default": models.Position,
                "cargo_id": models.Position.cargo_id,
                "rack_id": models.Position.rack_id,
                "cell_number": models.Position.cell_number,
                "weight": models.Position.weight,
                "date": models.Position.date
            }
        }

        return table_field_models[table]

    def get_output_templates(self, database, select_table, select_extension, select_output_type):
        stmt = select(self.get_table_fields(select_table)["default"])

        output_templates = {
            "JSON": {
                "Количество свободных ячеек": (database.get_free_cells(),
                                               self.get_fields("free_cells")),

                "Заполненность стеллажей": (database.get_filling_shelving(), self.get_fields("filling_shelving")),

                "Таблица": (database.select_query(stmt, 3), self.get_fields(select_table))
            },
            "EXCEL": {
                "Количество свободных ячеек": (database.get_free_cells(), "Количество свободных ячеек",
                                               self.get_fields("free_cells")),

                "Заполненность стеллажей": (database.get_filling_shelving(), "Заполненность стеллажей",
                                            self.get_fields("filling_shelving")),

                "Таблица": (database.select_query(stmt, 3), "Таблица", self.get_fields(select_table))
            }
        }

        return output_templates[select_extension][select_output_type]
