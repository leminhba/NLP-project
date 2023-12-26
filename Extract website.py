from bs4 import BeautifulSoup
import re
import requests

def get_website(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def not_relative_uri(href):
    return re.compile('^https://').search(href) is not None


# viết hàm mở và đọc tất cả các file trong thư mục D:\\Downloaded Web Sites\\nongnghiep.vn
default_path = "D:\\Downloaded Web Sites\\nongnghiep.vn"
def get_all_file_in_folder(path=default_path):
    import os
    list_file = []
    for root, dirs, files in os.walk(path):
        for file in files:
            list_file.append(os.path.join(root, file))
    return list_file

# duyệt từng file trong list_file
# với mỗi file, đọc nội dung file và trích xuất ngày tháng năm và nội dung
# in ra màn hình ngày tháng năm và nội dung
list_file = get_all_file_in_folder()
for file in list_file:
    with open(file, encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    detail_content = soup.find("div", class_="detail-content")
    try:
        date_content = detail_content.find("span", class_="time-detail").text
        # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
        date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
        content = detail_content.find("div", class_="content").text
        # ghi ra file txt có tên trùng với tên file html
        # với nội dung là ngày tháng năm và nội dung
        with open(file.replace('.html', '.txt'), 'w', encoding="utf8") as fp:
            fp.write(date_content + '\n')
            fp.write(content)
    except:
        pass


