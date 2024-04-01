from pathlib import Path
import json
from parsers.metro_parser import MetroParsing
import os


class GetMetroInfo:
    def __init__(
        self,
        metro_parser: MetroParsing,
        base_directory: Path,
        filename: str,
        file_detail: str,
        city: str,
        address: str
    ):
        self.filename = filename
        self.parser = metro_parser
        self.base_directory = base_directory
        self.file_detail = file_detail
        self.address = address
        self.city = city

        if (
            not os.path.exists(f"{self.base_directory}/files/{self.filename}")
            or os.stat(f"{self.base_directory}/files/{self.filename}").st_size == 0
        ):
            self.links = self.parser.get_all_links(
                self.filename, self.address, self.city)
        else:
            with open(f"{self.base_directory}/files/{self.filename}", "r") as file:
                data = json.load(file)
                self.links = data.get("links", [])

    def __call__(self):

        product_info = self.parser.get_info(self.links)
        with open(
            f"{self.base_directory}/files/{self.file_detail}", "w", encoding="utf-8"
        ) as file:
            json.dump(product_info, file, ensure_ascii=False, indent=4)

        return product_info


project_directory = Path(__file__).parent.parent
