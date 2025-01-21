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

import time
import re
import os

class MetaCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
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
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(2)
        try:
            self.driver.maximize_window()
        except:
            pass

    def scrape_reviews(self):
        self.start_browser() 
        wait = WebDriverWait(self.driver, 10)

        # scroll만 하면 새로 loading되는 구조
        interval = 2 # 1초에 한 번 스크롤
        prev_height = self.driver.execute_script("return document.body.scrollHeight")

        columns = ['date', 'review', 'score']
        meta_data = {col: [] for col in columns}

        # 초기 로드된 데이터 개수
        prev_data_count = 0

        while True:
            # scrolling work
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

            # new review_load
            try:
                review_load = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.c-pageProductReviews_row.g-outer-spacing-bottom-xxlarge"))
                )
            except TimeoutException:
                print("No new reviews loaded after scrolling.")
                break

            # 현재 로드된 데이터 개수
            curr_data_count = len(
                self.driver.find_elements(By.CSS_SELECTOR, "div.c-pageProductReviews_row.g-outer-spacing-bottom-xxlarge > div")
            )    

            # 새로운 데이터가 로드되지 않았을 경우 종료
            if curr_data_count == prev_data_count:
                print("No more new reviews loaded.")
                break

            # 업데이트된 데이터 개수 기록   
            prev_data_count = curr_data_count
            print(f"Loaded {curr_data_count} reviews so far.")
                    
            # # 대기 후 페이지 소스 bring
            # time.sleep(interval)
            # # 현재 문서 높이를 가져와서 저장
            # curr_height = self.driver.execute_script("return document.body.scrollHeight")
            # if sum(len(meta_data[col]) for col in meta_data.keys()) >= 1000:
            #     df = pd.DataFrame(meta_data)
            #     self.data = df
            #     print("crawling over 1000 done:", df)
            #     # self.save_to_database()
            #     break

            # if curr_height == prev_height:
            #     print("no more contents available.")
            #     break

            # prev_height = curr_height 

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        data_rows = soup.select("div.c-pageProductReviews_row.g-outer-spacing-bottom-xxlarge > div")

        for row in data_rows[prev_data_count:]:
            date = 'N/A'
            date_div = row.find('div', attrs={'class': 'c-siteReviewHeader_reviewDate g-color-gray80 u-text-uppercase'})
            if date_div:
                date = date_div.get_text().strip()
 
            review = 'N/A'
            review_div = row.find('div', attrs={'class': 'c-siteReview_quote g-outer-spacing-bottom-medium'})
            
            if review_div:
                review_span = review_div.find('span')
                if review_span:
                    review = review_span.get_text().strip()
                
            score = 'N/A'
            score_div = row.find('div', attrs={'class': 'c-siteReviewScore_background c-siteReviewScore_background-user'})
            
            if score_div:
                score_title = score_div.get('title')
                if score_title:
                    extract = re.search(r'User score (\d+) out of 10', score_title)
                    if extract:
                        score = extract.group(1)

            self.logger.info(f"meta_data size: {len(meta_data['date'])}")

            if (date, review, score) not in zip(meta_data['date'], meta_data['review'], meta_data['score']):
                meta_data['date'].append(date)
                meta_data['review'].append(review)
                meta_data['score'].append(score)

                # logging debug
                current_index = len(meta_data['date']) - 1
                self.logger.info(f"crawling success: {current_index}")
            else:
                print('data already exists')
            
        # if all(len(meta_data[col]) > 0 for col in columns):
        #     df = pd.DataFrame(meta_data)
        #     self.data = df
        #     print("crawling done:", df)
        # else:
        #     print("no data collected")   

        # DataFrame으로 변환
        df = pd.DataFrame(meta_data)
        if not df.empty:
            self.data = df
            print("Crawling completed. DataFrame created.")
            self.save_to_database()
        else:
            print("No valid data collected.")

    
    def save_to_database(self):
        file_name = "reviews_metacritic.csv"
        file_path = os.path.join(self.output_dir, file_name)
        if isinstance(self.data, pd.DataFrame):
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")
