from parsers.metro_parser import MetroParsing
from getters.get_detail import GetMetroInfo, project_directory

parser = MetroParsing("https://online.metro-cc.ru/category/chaj-kofe-kakao/chay")
get_info_obj = GetMetroInfo(
    parser,
    project_directory,
    "tea_links.json",
    "tea_details.json",
    "Москва",
    "Ул. Пр-т Мира, д. 211, стр. 1 (м. Ростокино)",
)


if __name__ == "__main__":
    get_info_obj.__call__()
