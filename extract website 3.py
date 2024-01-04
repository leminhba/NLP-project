from bs4 import BeautifulSoup
import re
import os
import requests
from urllib.parse import urlparse

def get_all_file_in_folder(path="D:\\Downloaded Web Sites\\tuoitre"):
    list_file = []
    for root, dirs, files in os.walk(path):
        for file in files:
            list_file.append(os.path.join(root, file))
    return list_file

def get_website(html_file):
    with open(html_file, encoding="utf8") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    return soup


def extract_info_and_write_to_txt(html_file):
    new_feeds = get_website(html_file).find('div', class_='box-category-middle').find_all('a',class_='box-category-link-with-avatar')
    for feed in new_feeds:
        title = feed.get('title')
        link = feed.get('href')
        # Phân tích URL để lấy tên file từ đường dẫn
        parsed_url = urlparse(link)
        file_name = parsed_url.path.split("/")[-1]
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        # Xóa tất cả các phần tử hình ảnh từ trang web
        for img in soup.find_all('img'):
            img.extract()
        # Lấy nội dung HTML sau khi đã xóa hình ảnh
        cleaned_html = soup.prettify()
        # Lưu nội dung HTML vào file trên đĩa
        with open(file_name, "w", encoding="utf-8") as file:
            file.write(cleaned_html)



if __name__ == "__main__":
    # Đặt thư mục làm việc hiện tại
    new_directory = "D:/Downloaded Web Sites/tuoitre/extract"
    os.chdir(new_directory)

    list_file = get_all_file_in_folder()
    for file in list_file:
        try:
            extract_info_and_write_to_txt(file)
        except Exception as e:
            print(f"Error processing {file}: {e}")
