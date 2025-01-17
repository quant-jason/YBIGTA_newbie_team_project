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

from bs4 import BeautifulSoup
from utils.logger import setup_logger
import time

class RTCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.rottentomatoes.com/m/marvels_the_avengers/reviews?type=user'
        self.dir = output_dir
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.data: list = [[], [], []]

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
        
        # "Load More" 버튼을 최대 60번 클릭하여 리뷰를 로드
        for _ in range(60):
            try:
                # 버튼이 클릭 가능할 때까지 기다림
                load_more_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "rt-button[data-qa='load-more-btn']"))
                )
                # 버튼이 화면에 보이도록 스크롤
                self.driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                # 버튼 클릭
                load_more_button.click()
                time.sleep(1)  # 버튼 클릭 후 로딩 대기
            except Exception as e:
                print("No more reviews to load or error occurred:", e)
                break

        # 리뷰 데이터 추출
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        review_rows = soup.find_all('div', class_='audience-review-row')

        for row in review_rows:
            try:
                # 별점 추출
                meta = row.find('div', class_='audience-review-meta')
                if meta:
                    score_tag = meta.find('rating-stars-group')
                    score_ = score_tag['score'] if score_tag and score_tag.has_attr('score') else 'N/A'
                else:
                    score_ = 'N/A'

                # 날짜 추출
                date_tag = row.find('span', class_='audience-reviews__duration')
                date_ = date_tag.get_text(strip=True) if date_tag else 'N/A'

                # 리뷰 텍스트 추출
                review_container = row.find('p', class_='audience-reviews__review')
                review_text = review_container.get_text(strip=True) if review_container else ''

                # 영어 판단: 알파벳 비율 >= 70%
                if not self.is_english(review_text):
                    print(f"Non-English review skipped: {review_text}")
                    continue

                # 데이터 저장
                self.data[0].append(date_)
                self.data[1].append(review_text)
                self.data[2].append(score_)
            except Exception as e:
                print(f"Error processing review: {e}")
                continue

        # 데이터프레임 생성
        if any(self.data[0]) and any(self.data[1]) and any(self.data[2]):
            self.data = pd.DataFrame({
                "date": self.data[0],
                "review": self.data[1],
                "score": self.data[2]
            })
        else:
            print("No data collected.")

    def save_to_database(self):
        file_name = "reviews_rotten_tomatoes.csv"
        file_path = os.path.join(self.dir, file_name)
        if isinstance(self.data, pd.DataFrame):
            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")

    def is_english(self, text):
        """
        텍스트가 영어인지 확인하는 간단한 규칙:
        알파벳 문자 비율이 전체 문자 중 70% 이상이면 영어로 간주.
        """
        letters = re.findall(r'[a-zA-Z]', text)
        non_space_chars = re.sub(r'\s', '', text)
        if non_space_chars and (len(letters) / len(non_space_chars)) >= 0.7:
            return True
        return False
