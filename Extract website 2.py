from bs4 import BeautifulSoup
import re
import requests
from sqlalchemy import create_engine
from sqlalchemy.dialects.mssql import NVARCHAR, DATE
import pandas as pd
import main.util as util
import datetime


def not_relative_uri(href):
    return re.compile('^https://').search(href) is not None

def get_website(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def get_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.text
    detail_content = soup.find("div", class_="detail-content")
    # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
    try:
        date_content = detail_content.find("span", class_="time-detail").text
        # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
        date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
        content = detail_content.find("div", class_="content").text
    except:
        date_content = ''
        content = ''

    return title, content, date_content

def get_nongnghiep_vn():
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

def get_tuoitre_vn():
    website = 'Báo Tuổi trẻ'
    url = 'https://tuoitre.vn/nong-nghiep.html'
    new_feeds = get_website(url).find('div', class_='box-category-middle').find_all('a', class_='box-category-link-with-avatar')
    for feed in new_feeds:
        title = feed.get('title')
        link = 'https://tuoitre.vn' + feed.get('href')
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
        try:
            content = soup.find("div", class_="detail-content").text
            date_content = soup.find("div", class_="detail-time").text
            # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
            date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
            # lấy thời gian hiện tại theo dạng dd/mm/yyyy
            now = datetime.datetime.now()
            now = now.strftime("%d/%m/%Y")
            if date_content < now:
                #nếu content > 50   thì mới insert vào db
                if len(content) > 50:
                    #print(title)
                    insert_db(website, link, title, content, date_content)
        except Exception as e: print(e)

def get_thanhnien_vn():
    website = 'Báo Thanh niên'
    url = 'https://thanhnien.vn/kinh-te/kinh-te-xanh.htm'
    new_feeds = get_website(url).find('div', class_='main').find_all('a', class_='box-category-link-title')
    for feed in new_feeds:
        title = feed.get('title')
        link = 'https://thanhnien.vn' + feed.get('href')
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")

        # nếu có lỗi thì bỏ qua dòng lệnh dưới đây
        try:
            content = soup.find("div", class_="detail-content").text
            date_content = soup.find("div", class_="detail-time").text
            # trích xuất ngày tháng năm có dạng dd/mm/yyyy từ date_content
            date_content = re.search(r'\d{2}/\d{2}/\d{4}', date_content).group()
            # lấy thời gian hiện tại theo dạng dd/mm/yyyy
            now = datetime.datetime.now()
            now = now.strftime("%d/%m/%Y")
            if date_content < now:
                #nếu content > 50   thì mới insert vào db
                if len(content) > 50:
                    #print(title)
                    insert_db(website, link, title, content, date_content)
        except Exception as e: print(e)


def insert_db(website, link, title, content, date_content):
    config = util.get_config()
    custom_uri = config['uri_database']
    print("connection {}".format(custom_uri))
    engine = create_engine(custom_uri, encoding='utf8')
    df = pd.DataFrame([{"website": website,
                        "article_link": link,
                        "article_title": title,
                        "article_content": content,
                        "article_date": date_content}])
    dict_type = {}
    for col_temp in df:
        dict_type[col_temp] = NVARCHAR
    df.to_sql(config['article_table_name'], engine, method='multi', if_exists='append', index=False, dtype=dict_type)

#get_nongnghiep_vn()
get_thanhnien_vn()
# 1 ngay thi chay 2 lan ham get_nongnghiep_vn
# neu article_link da ton tai thi khong insert vao db

