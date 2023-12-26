import scrapy
from scrapy.crawler import CrawlerProcess
from urllib.parse import urljoin

class MySpider(scrapy.Spider):
    name = 'myspider'
    allowed_domains = ['nongnghiep.vn']
    start_urls = ['https://nongnghiep.vn']
    visited_urls = set()

    def parse(self, response):
        # Kiểm tra xem URL đã được quét chưa, nếu đã quét thì thoát
        if response.url in self.visited_urls:
            return
        else:
            self.visited_urls.add(response.url)

        # Lấy tiêu đề và nội dung
        title = response.css('title::text').get()
        url = response.url

        # Lưu tiêu đề và nội dung vào file txt
        if title:
            print(f"Title: {title}")
            print(f"URL: {url}\n")

        # Lấy tất cả các liên kết và tiếp tục quét
        for next_page in response.css('a::attr(href)'):
            absolute_next_page = urljoin(response.url, next_page.extract())
            yield response.follow(absolute_next_page, self.parse)



# Tạo một đối tượng CrawlerProcess và cấu hình nó
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

# Chạy Spider
process.crawl(MySpider)
process.start()
