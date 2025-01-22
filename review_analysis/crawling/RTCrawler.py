from review_analysis.crawling.base_crawler import BaseCrawler
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

import re
import os
import sys

from bs4 import BeautifulSoup
from utils.logger import setup_logger
import time

class RTCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        """
        RTCrawler 클래스 초기화 메서드.

        Args:
            output_dir (str): 크롤링한 데이터를 저장할 디렉터리 경로.
        """
        super().__init__(output_dir)
        self.base_url = 'https://www.rottentomatoes.com/m/marvels_the_avengers/reviews?type=user'
        self.dir = output_dir
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.data: list = [[], [], []]
        self.logger = setup_logger()
        self.logger.info("RTC크롤러 로그 정상작동")

    def start_browser(self):
        """
        웹 브라우저를 시작하고 초기 URL로 이동.

        Args:
            None

        Returns:
            None
        """
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(2)
        try:
            self.driver.maximize_window()
        except:
            pass

    def scrape_reviews(self):
        """
        Rotten Tomatoes 웹사이트에서 사용자 리뷰를 크롤링하여 데이터로 저장.

        Args:
            None

        Returns:
            None: 수집된 리뷰 데이터는 self.data 리스트에 저장되며, 이후 DataFrame으로 변환.
        """
        if not os.path.exists(self.dir):
            print(f"Error: The directory '{self.dir}' does not exist. Please create it before running the program.")
            sys.exit(1)  

        self.start_browser()
        wait = WebDriverWait(self.driver, 10)
        
        for i in range(60):
            try:
                load_more_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "rt-button[data-qa='load-more-btn']"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                load_more_button.click()
                time.sleep(1)  
                print(f"{i+1}번째 버튼 클릭 성공")
            except Exception as e:
                print("No more reviews to load or error occurred:", e)
                break

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        review_rows = soup.find_all('div', class_='audience-review-row')

        for row in review_rows:
            try:
                meta = row.find('div', class_='audience-review-meta')
                if meta:
                    score_tag = meta.find('rating-stars-group')
                    score_ = score_tag['score'] if score_tag and score_tag.has_attr('score') else 'N/A'
                else:
                    score_ = 'N/A'

                date_tag = row.find('span', class_='audience-reviews__duration')
                date_ = date_tag.get_text(strip=True) if date_tag else 'N/A'

                review_container = row.find('p', class_='audience-reviews__review')
                review_text = review_container.get_text(strip=True) if review_container else ''

                if not self.is_english(review_text):
                    print(f"Non-English review skipped: {review_text}")
                    continue

                self.data[0].append(date_)
                self.data[1].append(review_text)
                self.data[2].append(score_)
            except Exception as e:
                print(f"Error processing review: {e}")
                continue

        if any(self.data[0]) and any(self.data[1]) and any(self.data[2]):
            self.data = pd.DataFrame({
                "date": self.data[0],
                "review": self.data[1],
                "score": self.data[2]
            })
        else:
            print("No data collected.")

    def save_to_database(self):
        """
        수집된 데이터를 CSV 파일로 저장.

        Args:
            None

        Returns:
            None: 저장 경로는 self.dir 경로의 `reviews_rotten_tomatoes.csv`.
        """
        file_name = "reviews_rotten_tomatoes.csv"
        file_path = os.path.join(self.dir, file_name)
        if isinstance(self.data, pd.DataFrame):
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")

    def is_english(self, text):
        """
        텍스트가 영어인지 확인.

        Args:
            text (str): 영어 여부를 확인할 텍스트.

        Returns:
            bool: 텍스트가 영어일 경우 True, 아닐 경우 False.
        """
        letters = re.findall(r'[a-zA-Z]', text)
        non_space_chars = re.sub(r'\s', '', text)
        if non_space_chars and (len(letters) / len(non_space_chars)) >= 0.3:
            return True
        return False
