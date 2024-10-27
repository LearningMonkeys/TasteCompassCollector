import scrapy
from scrapy_playwright.page import PageMethod
from urllib.parse import urljoin
import datetime
import re


def is_restaurant_review(text):  # 키워드 필터링
    keywords = ["맛집", "음식", "메뉴", "식당", "요리"]
    return any(keyword in text for keyword in keywords)


def is_blog_post(url):  # 블로그 포스트 url 확인
    return re.match(r'https://blog\.naver\.com/[^/]+/\d+$', url)


def is_post_content(url):  # 포스트 내용 url 확인
    return url.startswith("https://blog.naver.com/PostView.naver?")


# request 생성
def create_request(url, callback):
    return scrapy.Request(
        url,
        meta={
            'playwright': True,
            'playwright_page_methods': [
                PageMethod("wait_for_load_state", "networkidle")
            ],
        },
        callback=callback
    )


# Spider 클래스
class NaverBlogSpider(scrapy.Spider):
    name = 'naver_blog'
    allowed_domains = ['naver.com']
    start_urls = [
        f'https://section.blog.naver.com/Search/Post.naver?pageNo={pageNo}&rangeType=ALL&orderBy=sim&keyword=영통+맛집+리뷰'
        for pageNo in range(0, 100)
    ]

    # 스파이더 설정 - Playwright, 데이터 저장 파일 포맷 설정
    custom_settings = {
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,  # 최대 타임아웃 60초
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,  # 크롤링 시 브라우저를 헤드리스 모드로 실행
        },
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            f'results/naver_blog/{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json': {
                'format': 'json',
                'encoding': 'utf8',
                'store_empty': True,
                'indent': 4
            }
        }
    }

    # 크롤링 시작 메소드 - 시작 url에 대한 chromium(브라우저) 동작을 시뮬레이션하기 위해 오버라이딩
    def start_requests(self):
        for url in self.start_urls:
            yield create_request(url, self.parse)

    # 검색 결과 페이지 처리
    def parse(self, response):
        print(response.url)
        # 검색 결과 페이지에서 블로그 포스트 링크 추출
        blog_links = response.css('a[href^="https://blog.naver.com"]::attr(href)').getall()

        # https://blog.naver.com/{blog_id}/{logNo}
        valid_blog_links = [
            link for link in blog_links
            if is_blog_post(link)
        ]

        for link in valid_blog_links:
            # 블로그 링크를 절대 URL로 변경하여 요청
            url = urljoin(response.url, link)
            yield create_request(url, self.parse_blog_post)


    def parse_blog_post(self, response):    # 블로그 포스트 페이지 처리 (블로그 포스트의 본문이 다른 html이라 이를 처리해야함)
        print(response.url)
        iframe_src = response.css('iframe#mainFrame::attr(src)').get()
        if iframe_src:
            url = urljoin(response.url, iframe_src)
            if is_post_content(url):
                yield create_request(url, self.parse_post_content)

        # 블로그 포스트 내용 중 다른 블로그 포스트 링크도 추가 탐색
        related_blog_links = response.css('a[href^="https://blog.naver.com"]::attr(href)').getall()
        for link in related_blog_links:
            url = urljoin(response.url, link)
            if is_post_content(url):  # 포스트 내용일 시
                yield create_request(url, self.parse_post_content)

            elif is_blog_post(url):  # 블로그 포스트일 시
                yield create_request(url, self.parse_blog_post)

    def parse_post_content(self, response): # 포스트 내용 페이지 처리 (블로그 포스트 페이지에서 본문의 url에 해당함)
        print(response.url)
        # # 블로그 포스트 페이지에서 모든 span 태그의 텍스트 추출
        # texts = response.css('span::text').getall()

        texts = response.css('.se-main-container *:not(.ssp-adcontent):not(style)::text').getall()

        # 텍스트 정제
        cleaned_texts = [text.strip() for text in texts if text.strip()]

        # 각 텍스트 요소를 연결하여 하나의 문자열로 합치기
        combined_text = " ".join(cleaned_texts)

        # 맛집 리뷰로 판단되는 경우에만 결과를 저장
        if combined_text and is_restaurant_review(combined_text):
            yield {
                'url': response.url,
                'content': combined_text
            }
