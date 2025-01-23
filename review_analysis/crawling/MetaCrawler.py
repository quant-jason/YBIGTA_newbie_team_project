from review_analysis.crawling.base_crawler import BaseCrawler
# from .base_crawler import BaseCrawler 
from utils.logger import setup_logger 

from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

from typing import Optional
import time
import re
import os

class MetaCrawler(BaseCrawler):
    """
    MetaCrawler 클래스는 Metacritic에서 영화 사용자 리뷰 데이터를 크롤링하는 기능을 가짐.

    Attributes:
        base_url (str): 크롤링 대상 URL.
        output_dir (str): 결과 파일이 저장될 디렉토리.
        chrome_options (Options): 크롬 브라우저 옵션 설정.
        driver (webdriver.Chrome): Selenium WebDriver 인스턴스.
        logger (Logger): 로그 기록을 위한 로거.
        data (Optional[pd.DataFrame]): 크롤링한 데이터를 저장하는 데이터프레임.
    """
    def __init__(self, output_dir: str):
        """
        MetaCrawler 클래스의 초기화 메서드.

        Args:
            output_dir (str): 결과 파일이 저장될 디렉토리.
        """
        super().__init__(output_dir)
        self.base_url = 'https://www.metacritic.com/movie/the-avengers-2012/user-reviews'

        self.output_dir = output_dir

        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])
        self.driver = webdriver.Chrome(options=self.chrome_options)

        self.logger = setup_logger()
        self.logger.info("Meta크롤러 로그 정상작동")

        # 데이터 초기화
        self.data: Optional[pd.DataFrame] = None
        
    def start_browser(self):
        """
        크롬 브라우저를 실행하고 Metacritic URL로 이동.
        """
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(2)
        try:
            self.driver.maximize_window()
        except:
            pass

    def scrape_reviews(self):
        """
        사용자 리뷰 데이터를 크롤링하여 메타데이터로 저장.

        Reviews:
            - date (str): 리뷰 날짜.
            - review (str): 리뷰 텍스트.
            - score (str): 리뷰 점수.
        """
        self.start_browser()
        wait = WebDriverWait(self.driver, 10)

        interval = 2 # scroll 대기시간 증가
        prev_height = self.driver.execute_script("return document.body.scrollHeight")

        columns = ['date', 'review', 'score']
        meta_data = {col: [] for col in columns}

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(interval)  # 대기 시간 증가
            
            try:
                review_load = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-pageProductReviews_row"))
                )
            except TimeoutException:
                print("Can't find newly loading reviews.")
                break

            time.sleep(interval)
            curr_height = self.driver.execute_script("return document.body.scrollHeight")
            if sum(len(meta_data[col]) for col in meta_data.keys()) >= 1000:
                # df = pd.DataFrame(meta_data)
                # self.data = df
                print("Crawling over 1000 done:", df)
                break

            if curr_height == prev_height:
                print("No more contents available.")
                break

            # 지우기 
            print(f"Scroll progress - prev_height: {prev_height}, curr_height: {curr_height}")
            prev_height = curr_height

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        # data_rows = soup.find_all('div', attrs={'class': 'c-pageProductReviews_row'})
        # data_rows = soup.select('div.c-pageProductReviews_row.g-outer-spacing-bottom-xxlarge')
        data_rows = soup.select('div[data-testid="product-review"]')
        print(f"Total review containers found: {len(data_rows)}") # data_rows에 포함된 div의 개수. 지우기

        for row in data_rows:
            # print("Current row:", row)  # 현재 row 정보, 지우기 

            date = 'N/A'
            date_div = row.find('div', attrs={'class': 'c-siteReviewHeader_reviewDate g-color-gray80 u-text-uppercase'})
            if date_div:
                date = date_div.get_text().strip()

            review = 'N/A'
            # c-siteReview_quote g-outer-spacing-bottom-small
            # c-siteReview_quote g-outer-spacing-bottom-medium
            review_div = row.select_one('div > div > div > div > div > span')
            # review_div = row.find('div', attrs={'class': 'c-siteReview_quote g-outer-spacing-bottom-medium'})
            # if review_div:
            #     review_span = review_div.find('span')
            #     if review_span:
            #       review = review_span.get_text().strip()
            #       print("review:", review)
            if review_div:
                review = review_div.get_text(strip=True)

                if "[SPOILER ALERT:" in review:
                    print("Skipped review due to spoler alert:")
                    continue
            else:
                print("Review not found")

            score = 'N/A'
            score_div = row.find('div', attrs={'class': 'c-siteReviewScore_background c-siteReviewScore_background-user'})
            if score_div:
                # score_div 내부의 하위 div를 다시 탐색
                inner_div = score_div.find('div', attrs={'title': True})
                if inner_div:
                    score_title = inner_div.get('title')  # 실제 title 속성을 가져옴
                    if score_title:
                        extract = re.search(r'User score (\d+) out of 10', score_title)
                        if extract:
                            score = extract.group(1)

            if date not in meta_data['date'] or review not in meta_data['review'] or score not in meta_data['score']:
                meta_data['date'].append(date)
                meta_data['review'].append(review)
                meta_data['score'].append(score)

                # current_index = len(meta_data['date']) - 1
                # self.logger.info(f"Crawling success: {current_index}")
                # print(meta_data)  # 크롤링 과정에서 데이터 확인  ## 지우기
                
                
                # **여기서 `self.data` 업데이트**
                self.data = pd.DataFrame(meta_data)
                print(f"Added data: {date}, {review[:10]}, {score}")

                for col in meta_data.keys(): ## 지우기
                    print(f"{col}: {len(meta_data[col])} entries") 
            else:
                print("Data already exists.")

    
    def save_to_database(self):
        """
        크롤링한 데이터를 CSV 파일로 저장.

        File:
            - reviews_metacritic.csv: 결과 데이터를 저장하는 파일.
        """
        file_name = "reviews_metacritic.csv"
        file_path = os.path.join(self.output_dir, file_name)
        if isinstance(self.data, pd.DataFrame):
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")
