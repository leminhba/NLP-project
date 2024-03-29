from bs4 import BeautifulSoup
import re
import requests
from sqlalchemy import create_engine
from sqlalchemy.dialects.mssql import NVARCHAR, INTEGER, DATETIME
import pandas as pd
import main.util as util
from main.handle_information import load_keywords_from_excel
import traceback
from main_model.config.read_config import *
from main_model.util.io_util import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

now = datetime.datetime.now()
now = now.strftime("%d/%m/%Y")


def log_error(e, function_name):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Format the current time as a string
    filename = f"error_log_{function_name}_{current_time}.txt"  # Append the current time and function name to the filename
    with open('log/' + filename, 'a') as file:
        file.write(f"Error in {function_name}: {e}\nTraceback:\n{traceback.format_exc()}\n")


def run_with_error_logging(func, func_name):
    try:
        func()
    except Exception as e:
        log_error(e, func_name)


def save_none_type_links_to_file(function_name, none_type_links):
    try:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f'{function_name}_none_type_{current_time}.txt'

        with open('log/' + file_path, 'w', encoding='utf-8') as file:
            for link in none_type_links:
                file.write(link + '\n')
        print(f'Successfully saved {len(none_type_links)} links to {file_path}')
    except Exception as e:
        print(f'Error while saving links: {str(e)}')

def not_relative_uri(href):
    return re.compile('^https://').search(href) is not None

def ends_with_htm_or_html(href):
    return re.compile('\.html?$').search(href) is not None

def compile_keywords(keywords):
    # Biên dịch các từ khóa thành biểu thức chính quy
    return [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in keywords]

def check_title_type(title):
    #preporcessing title


    trong_trot = compile_keywords(load_keywords_from_excel("dictionary/trong_trot.xls"))
    chan_nuoi = compile_keywords(load_keywords_from_excel("dictionary/chan_nuoi.xls"))
    lam_nghiep = compile_keywords(load_keywords_from_excel("dictionary/lam_nghiep.xls"))
    thuy_san = compile_keywords(load_keywords_from_excel("dictionary/thuy_san.xls"))
    nong_thon_moi = compile_keywords(load_keywords_from_excel("dictionary/nong_thon_moi.xls"))
    kinh_te_nong_nghiep = compile_keywords(load_keywords_from_excel("dictionary/kinh_te_nong_nghiep.xls"))
    thuy_loi_pctt = compile_keywords(load_keywords_from_excel("dictionary/thuy_loi_pctt.xls"))
    bdkh = compile_keywords(load_keywords_from_excel("dictionary/bdkh.xls"))

    # Danh sách để lưu trữ các loại tìm thấy
    types_found = set()  # Sử dụng set để tránh trùng lặp
    try:
        # Kiểm tra từng nhóm từ khóa độc lập với biểu thức chính quy
        if any(pattern.search(title) for pattern in trong_trot):
            types_found.add("trong_trot")
        if any(pattern.search(title) for pattern in chan_nuoi):
            types_found.add("chan_nuoi")
        if any(pattern.search(title) for pattern in lam_nghiep):
            types_found.add("lam_nghiep")
        if any(pattern.search(title) for pattern in thuy_san):
            types_found.add("thuy_san")
        if any(pattern.search(title) for pattern in nong_thon_moi):
            types_found.add("nong_thon_moi")
        if any(pattern.search(title) for pattern in kinh_te_nong_nghiep):
            types_found.add("kinh_te_nong_nghiep")
        if any(pattern.search(title) for pattern in thuy_loi_pctt):
            types_found.add("thuy_loi_pctt")
        if any(pattern.search(title) for pattern in bdkh):
            types_found.add("bdkh")

        # Trả về chuỗi phân tách bởi dấu phảy nếu có kết quả
        return ', '.join(types_found) if types_found else 'none'
    except Exception as e:
        return 'none'


def del_duplicate(date):
    config = read_config_file()
    db = config['test_db']
    sp = """DelDuplicateArticle """
    exec_sp(db, sp, date)


def get_website(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup



def soup_get_nongnghiep_vn():
    website = 'Báo Nông nghiệp Việt Nam'
    url = 'https://nongnghiep.vn'
    new_feeds = get_website(url).find('section', class_='box-page-first').find_all('a', class_='',href=not_relative_uri)
    for feed in new_feeds:
        title = feed.get('title')
        link = feed.get('href')
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        detail_content = soup.find("div", class_="detail-content")
        # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
        try:
            date_content = detail_content.find("span", class_="time-detail").text
            # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
            date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
            # lấy thời gian hiện tại theo dạng dd/mm/yyyy
            now = datetime.datetime.now()
            now = now.strftime("%d/%m/%Y")
            if date_content == now:
                content = detail_content.find("div", class_="content").text
                #nếu content > 50   thì mới insert vào db
                if len(content) > 50:
                    #print(title)
                    insert_db(website, link, title, content, date_content)
        except Exception as e: print(e)

def get_nongnghiep_vn():
    # Khởi tạo WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=chrome_options)
    website = 'Báo Nông nghiệp Việt Nam'
    url = 'https://nongnghiep.vn'
    driver.get(url)
    content = WebDriverWait(driver, 1).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "box-page-first"))
    )
    elements = content[0].find_elements(By.CSS_SELECTOR, "a.expthumb")
    links = []
    for e in elements:
        link = e.get_attribute('href')
        links.append(link)

    for link in links:
        if ends_with_htm_or_html(link):
            driver.get(link)
            try:
                title = driver.title
                article_type = check_title_type(title)
                now = datetime.datetime.now().strftime("%d/%m/%Y")
                if "nongsanviet" in link:
                    date_content = driver.find_element(By.CLASS_NAME, "time-detail").text
                    date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                    if date_content == now:
                        content = driver.find_element(By.CLASS_NAME, "content_detail").text
                        intro = detail_content.find_element(By.CLASS_NAME, "sapo").text
                        insert_db(website, link, title, content, date_content)
                        print(title)
                else:
                    detail_content = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "detail-content")))
                    date_content = detail_content.find_element(By.CLASS_NAME, "time-detail").text
                    date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                    if date_content == now:
                        content = detail_content.find_element(By.CLASS_NAME, "content").text
                        intro = detail_content.find_element(By.CLASS_NAME, "detail-intro").text
                        # kiem tra them ca phan gioi thieu
                        if article_type == 'none':
                            article_type = check_title_type(intro)
                        insert_db(website, link, title, content, date_content, article_type, intro)
                        print(title)

            except Exception as e:
                print(f"Lỗi: {link}")
    driver.quit()


def get_tuoitre_vn():
    website = 'Báo Tuổi trẻ'
    url = 'https://tuoitre.vn'
    #new_feeds = get_website(url).find('div', class_='box-category-middle').find_all('a', class_='box-category-link-with-avatar')
    new_feeds = get_website(url).find('div', class_='main').find_all('a', class_='box-category-link-title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'tuoitre'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.get('title')
        article_type = check_title_type(title)
        if article_type != 'none':
            link = 'https://tuoitre.vn' + feed.get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
            try:
                date_content = soup.find("div", class_="detail-time").text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find("h2", class_="detail-sapo").text
                    content = soup.find("div", class_="detail-content").text
                    insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e: print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_thanhnien_vn():
    website = 'Báo Thanh niên'
    url = 'https://thanhnien.vn'
    new_feeds = get_website(url).find('div', class_='main').find_all('a', class_='box-category-link-title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'thanhnien'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.get('title')
        a = feed.get('href')
        article_type = check_title_type(title)
        if article_type != 'none':
            link = 'https://thanhnien.vn' + feed.get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                date_content = soup.find("div", class_="detail-time").text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find("h2", class_="detail-sapo").text
                    content = soup.find("div", class_="detail-content").text
                    insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e: print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_dantri_vn():
    website = 'Báo Dân trí'
    url = 'https://dantri.com.vn'
    # Extracting all links and titles
    new_feeds = get_website(url).find_all("h3", class_='article-title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'dantri'
    count_none_type = 0
    for feed in new_feeds:
        # đọc link và title từ feed
        title = feed.find('a').text
        article_type = check_title_type(title)# sau này khi phan loai duoc thi se chuyen xuong duoi
        if article_type != 'none':
            link = 'https://dantri.com.vn' + feed.find('a').get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
            try:
                date_content = soup.find("div", class_="dt-news__time").text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find("div", class_="dt-news__sapo").text
                    content = soup.find("div", class_="dt-news__content").text
                    # nếu content > 50   thì mới insert vào db
                    if len(content) > 50:
                        #print(title)
                        insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e: print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)


def get_tienphong():
    website = 'Báo Tiền Phong'
    url = 'https://tienphong.vn'
    new_feeds = get_website(url).find('div', class_='site-body').find_all('article', class_='story')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'tienphong'
    count_none_type = 0
    for feed in new_feeds:
        #title = feed.find('h2', class_='story__heading').find('a', class_='cms-link').text
        story_heading = feed.find(class_='story__heading').find('a', class_='cms-link')
        if story_heading is not None:
            title = story_heading.text
            link = story_heading.get('href')
            article_type = check_title_type(title)
            # nếu khác none thì lấy link, nếu không thì bỏ qua
            if article_type != 'none':
                response = requests.get(link)
                soup = BeautifulSoup(response.content, "html.parser")
                try:
                    date_content = soup.find('span', class_='time').find('time').text
                    # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                    date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                    if date_content == now:
                        intro = soup.find("div", class_="article__sapo").text
                        content = soup.find("div", class_="article__body").text
                        # nếu content > 50   thì mới insert vào db
                        if len(content) > 50:
                            # print(title)
                            insert_db(website, link, title, content, date_content, article_type, intro)
                except Exception as e:
                    print(e)
            else:
                count_none_type += 1
                log_content = f" {count_none_type}: {title}"
                none_type_links.append(log_content)  # Lưu liên kết vào danh sách


    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_vnexpress():
    website = 'Báo vnexpress'
    url = 'https://vnexpress.net/'
    new_feeds = get_website(url).find('div', class_='col-left').find_all('h3', class_='title-news')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'vnexpress'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.find('a').text
        article_type = check_title_type(title)
        # nếu khác none thì lấy link, nếu không thì bỏ qua
        if article_type != 'none':
            link = feed.find('a').get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                date_content = soup.find('div', class_='header-content').find('span', class_='date').text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_content)
                if match:
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = match.group(3)
                    date_content = f"{day:02d}/{month:02d}/{year}"
                if date_content == now:
                    intro = soup.find('div', class_='sidebar-1').find('p', class_='description').text
                    content = soup.find('div', class_='sidebar-1').find('article', class_='fck_detail').text
                    # nếu content > 50   thì mới insert vào db
                    if len(content) > 50:
                        # print(title)
                        insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_vietnamnet():
    website = 'Báo vietnamnet'
    url = 'https://vietnamnet.vn/thoi-su'
    new_feeds = get_website(url).find_all('h3', class_='vnn-title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'vietnamnet'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.text.strip()
        article_type = check_title_type(title)
        # nếu khác none thì lấy link, nếu không thì bỏ qua
        if article_type != 'none':
            link = 'https://vietnamnet.vn' + feed.a['href']
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                date_content = soup.find('div', class_='bread-crumb-detail__time').text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_content)
                if match:
                    day = int(match.group(1))
                    month = int(match.group(2))
                    year = match.group(3)
                    date_content = f"{day:02d}/{month:02d}/{year}"
                if date_content == now:
                    intro = soup.find('h2', class_='content-detail-sapo').text
                    content = soup.find('div', class_='main-content').text
                    insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_nhandan():
    website = 'Báo Nhân dân'
    url = 'https://nhandan.vn/tin-moi.html'
    new_feeds = get_website(url).find_all('h3', class_='story__heading')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'nhandan'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.text.strip()
        article_type = check_title_type(title)
        # nếu khác none thì lấy link, nếu không thì lưu link vào danh sách
        if article_type != 'none':
            link = feed.a['href']
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                date_content = soup.find('time', class_='time').text
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find('div', class_='article__sapo').text
                    content = soup.find('div', class_='article__body').text
                    insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_danviet():
    website = 'Báo Dân việt'
    url = 'https://danviet.vn/nha-nong.htm'
    new_feeds = get_website(url).find_all('div', class_='wrap-title-news')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'danviet'
    count_none_type = 0
    for feed in new_feeds:
        title = feed.text.strip()
        article_type = check_title_type(title)
        # nếu khác none thì lấy link, nếu không thì lưu link vào danh sách
        if article_type != 'none':
            link = 'https://danviet.vn' + feed.find('a', class_='title')['href']
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            try:
                date_content = soup.find('div', class_='line-datetime').text
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find('div', class_='sapo').text
                    content = soup.find('div', class_='entry-body').text
                    insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_hanoimoi():
    website = 'Báo Hà Nội mới'
    url = 'https://hanoimoi.vn/nong-nghiep-nong-thon'
    # Extracting all links and titles
    new_feeds = get_website(url).find_all(class_='b-grid__title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'hanoimoi'
    count_none_type = 0
    for feed in new_feeds:
        # đọc link và title từ feed
        title = feed.find('a').text
        article_type = check_title_type(title)# sau này khi phan loai duoc thi se chuyen xuong duoi
        if article_type != 'none':
            link = feed.find('a').get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
            try:
                date_content = soup.find(class_="block-sc-publish-time").text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find(class_="block-sc-sapo").text
                    content = soup.find("div", class_="entry-no-padding").text
                    # nếu content > 50   thì mới insert vào db
                    if len(content) > 50:
                        # print(title)
                        insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)

def get_laodong():
    website = 'Báo Lao động'
    url = 'https://laodong.vn'
    # Extracting all links and titles
    new_feeds = get_website(url).find_all(class_='link-title')
    none_type_links = []  # Tạo danh sách để lưu các liên kết
    log_file_base_name = 'laodong'
    count_none_type = 0
    for feed in new_feeds:
        # đọc link và title từ feed
        title = feed.find('h2').text
        article_type = check_title_type(title)# sau này khi phan loai duoc thi se chuyen xuong duoi
        if article_type != 'none':
            link = feed.get('href')
            response = requests.get(link)
            soup = BeautifulSoup(response.content, "html.parser")
            # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
            try:
                date_content = soup.find(class_="time").text
                # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
                date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
                if date_content == now:
                    intro = soup.find(class_="chappeau").text
                    content = soup.find("div", class_="art-body").text
                    # nếu content > 50   thì mới insert vào db
                    if len(content) > 50:
                        # print(title)
                        insert_db(website, link, title, content, date_content, article_type, intro)
            except Exception as e:
                print(e)
        else:
            count_none_type += 1
            log_content = f" {count_none_type}: {title}"
            none_type_links.append(log_content)  # Lưu liên kết vào danh sách

    save_none_type_links_to_file(log_file_base_name, none_type_links)


def insert_db(website, link, title, content, date_content,article_type, article_intro):
    config = util.get_config()
    custom_uri = config['uri_database']
    engine = create_engine(custom_uri, encoding='utf8')
    df = pd.DataFrame([{
        "website": website,
        "article_link": link,
        "article_title": title,
        "article_content": content,
        "article_date": date_content,
        "article_type": article_type,
        "article_intro": article_intro,
        "article_update_date": datetime.datetime.now()
    }])
    dict_type = {col: NVARCHAR if col != "update_date" else DATETIME for col in df}
    df.to_sql(config['article_table_name'], engine, method='multi', if_exists='append', index=False, dtype=dict_type)


run_with_error_logging(get_laodong, "get_laodong")
run_with_error_logging(get_hanoimoi, "get_hanoimoi")
run_with_error_logging(get_nongnghiep_vn, "get_nongnghiep_vn")
run_with_error_logging(get_thanhnien_vn, "get_thanhnien_vn")
run_with_error_logging(get_tuoitre_vn, "get_tuoitre_vn")
run_with_error_logging(get_dantri_vn, "get_dantri_vn")
run_with_error_logging(get_tienphong, "get_tienphong")
run_with_error_logging(get_vnexpress, "get_vnexpress")
run_with_error_logging(get_vietnamnet, "get_vietnamnet")
run_with_error_logging(get_nhandan, "get_nhandan")
run_with_error_logging(get_danviet, "get_danviet")


#article_type = check_title_type("Hỗ trợ nông dân chuyển đổi số, ‘chuyến tàu’ không thể lỡ")

del_duplicate(now)
# 1 ngay thi chay 2 lan ham get_nongnghiep_vn
# neu article_link da ton tai thi khong insert vao db

