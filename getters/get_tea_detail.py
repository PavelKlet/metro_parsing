from pathlib import Path
import json
from parsers.tea_parser import parser, MetroTeaParsing
import os


class GetTeaInfo:
    def __init__(self, tea_parser: MetroTeaParsing, base_directory: Path):
        self.parser = tea_parser
        self.tea_links = None
        self.base_directory = base_directory

        if (
            not os.path.exists(f"{self.base_directory}/files/links.json")
            or os.stat(f"{self.base_directory}/files/links.json").st_size == 0
        ):
            self.tea_links = self.parser.get_all_tea_links()
        else:
            with open(f"{self.base_directory}/files/links.json", "r") as file:
                data = json.load(file)
                self.tea_links = data.get("links", [])

    def __call__(self):

        product_info = self.parser.get_tea_info(self.tea_links)
        with open(
            f"{self.base_directory}/files/tea_details.json", "w", encoding="utf-8"
        ) as file:
            json.dump(product_info, file, ensure_ascii=False, indent=4)

        return product_info


project_directory = Path(__file__).parent.parent
tea_info_obj = GetTeaInfo(parser, project_directory)
