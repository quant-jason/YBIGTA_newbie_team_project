from review_analysis.crawling.base_crawler import BaseCrawler
from utils.logger import setup_logger

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import os
import time
import pandas as pd

class IMDBCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://m.imdb.com/title/tt0848228/reviews/?ref_=tt_ururv_sm' 
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.chrome_options.add_experimental_option("excludeSwitches",["enable-logging"])
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.logger = setup_logger()
        self.logger.info("IDMB크롤러 로그 정상작동")

    def start_browser(self):
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(2)

        #All 버튼 찾아서 클릭
        all_button = self.driver.find_element(By.XPATH, "//*[@id='__next']/main/div/section/div/section/div/div[1]/section[1]/div[3]/div/span[2]/button/span/span")
        prev_height = all_button.location['y']
        while True:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", all_button)
            time.sleep(1)            
            curr_height = self.driver.execute_script("return document.body.scrollHeight")
            if curr_height == prev_height:
                break
            prev_height = curr_height
        all_button.click()
        #다시 가장 위로 스크롤하기기
        to_top_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/button")
        to_top_button.click()
        time.sleep(5)

    
    def scrape_reviews(self):

        self.start_browser()
        wait = WebDriverWait(self.driver, 10)

        interval = 7
        prev_height = self.driver.execute_script("return document.body.scrollHeight-2000")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-2000)")
            time.sleep(interval)
            curr_height = self.driver.execute_script("return document.body.scrollHeight-2000")
            if curr_height == prev_height:
                break
            prev_height = curr_height

        columns = ['review', 'date', 'score']         # 리뷰, 리뷰날짜, 평점 크롤링
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        data_rows = soup.find_all('article', class_='sc-d59f276d-1') 
        values = []

        for row in data_rows:                     
            blank = []
            #리뷰 가져오기
            review = row.find('div', attrs={'class': 'ipc-html-content-inner-div'})     
            if review:
                review = review.get_text().strip()
                blank.append(review)
            else:                                                                     
                blank.append('N/A')
                continue
            # 리뷰날짜 가져오기
            date = row.find('li', attrs={'class': 'ipc-inline-list__item review-date'})      
            if date:                                                                    
                date = date.get_text().strip()                                          
                blank.append(date)
            else:                                                                      
                blank.append('N/A')
            # 평점 가져오기
            score = row.find('span', attrs={'class': 'ipc-rating-star--rating'})        
            if score:
                score = score.get_text().strip()
                blank.append(score)
            else:
                blank.append('N/A')
            
            values.append(blank)
        
        df = pd.DataFrame(values, columns = columns)
        df = df[[df.columns[1], df.columns[0]] + list(df.columns[2:])]
        self.data = df
        print("크롤링 완료")

        
    def save_to_database(self):
        file_name = "reviews_IMDB.csv"
        file_path = os.path.join(self.output_dir, file_name)
        if isinstance(self.data, pd.DataFrame):
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")
