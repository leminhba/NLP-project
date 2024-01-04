from bs4 import BeautifulSoup
import re
import os


def get_all_file_in_folder(path="D:\\Downloaded Web Sites\\nongnghiep.vn"):
    list_file = []
    for root, dirs, files in os.walk(path):
        for file in files:
            list_file.append(os.path.join(root, file))
    return list_file


def extract_info_and_write_to_txt(html_file):
    with open(html_file, encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')

    detail_content = soup.find("div", class_="detail-content")
    date_content = detail_content.find("span", class_="time-detail").text

    # Trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content bằng regex
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_content)

    if date_match:
        date_content = date_match.group()
        content = detail_content.find("div", class_="content").text

        # Ghi ra file txt có tên trùng với tên file html
        # với nội dung là ngày tháng năm và nội dung
        with open(html_file.replace('.html', '.txt'), 'w', encoding="utf8") as fp:
            fp.write(date_content + '\n')
            fp.write(content)


if __name__ == "__main__":
    list_file = get_all_file_in_folder()
    for file in list_file:
        try:
            extract_info_and_write_to_txt(file)
        except Exception as e:
            print(f"Error processing {file}: {e}")
