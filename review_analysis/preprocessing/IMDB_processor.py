from review_analysis.preprocessing.base_processor import BaseDataProcessor

import pandas as pd
import os

from datetime import datetime
from scipy.stats import zscore
from sklearn.feature_extraction.text import TfidfVectorizer

class IMDB_processor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.df = pd.read_csv(input_path, na_values=["N/A"])

    def preprocess(self):
        # 결측값 제거
        self.df_cleaned = self.df.dropna()

        # 날짜 형식 변경 및 이상치 제거 & 평점 이상치 제거 
        self.df_cleaned['date'] = pd.to_datetime(self.df_cleaned['date'], format='%b %d, %Y', errors='coerce')
        self.df_cleaned = self.df_cleaned.dropna(subset=['date'])
        self.df_cleaned = self.df_cleaned[(self.df['score'] >= 1) & (self.df_cleaned['score'] <= 10)]

        # 지나치게 짧거나 긴 리뷰 탐색 및 제거
        self.df_cleaned['review_length'] = self.df_cleaned['review'].str.split().apply(len)
        self.df_cleaned['review_length_zscore'] = zscore(self.df_cleaned['review_length'])
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['review_length_zscore'] >= -3) & (self.df_cleaned['review_length_zscore'] <= 3)]
        self.df_cleaned = self.df_cleaned.drop(columns=['review_length', 'review_length_zscore'])

    def feature_engineering(self):
        # 날짜 파생 변수 추출
        self.df_cleaned['month'] = self.df_cleaned['date'].dt.strftime('%Y-%m')
        self.df_cleaned['day'] = self.df_cleaned['date'].dt.day_name()


        #TF-IDF 벡터화 수행
        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df_cleaned['review'])
        tfidf_feature_names = vectorizer.get_feature_names_out()
        self.df_cleaned['tfidf_features'] = [
            ', '.join(f"{word}:{tfidf:.2f}" for word, tfidf in zip(tfidf_feature_names, row) if tfidf > 0)
            for row in tfidf_matrix.toarray()]

    def save_to_database(self):
        file_name = "preprocessed_reviews_IMDB.csv"
        file_path = os.path.join(self.output_dir, file_name)
        if isinstance(self.df_cleaned, pd.DataFrame):
            self.df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")