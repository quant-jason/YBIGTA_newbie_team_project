from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.stats import zscore

class RTProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_path: str):
        super().__init__(input_path, output_path)
        self.input_path = input_path
        self.output_path = output_path
        self.df = pd.read_csv(input_path, na_values=["N/A"])

    def preprocess(self):
        self.df = self.df.dropna()

        self.df["date"] = pd.to_datetime(self.df["date"], format='%b %d, %Y', errors='coerce')
        release_date = pd.to_datetime("2012-04-26")
        self.df = self.df[self.df["date"] >= release_date]
        self.df = self.df.dropna(subset=["date"])

        self.df = self.df[(self.df["score"] >= 1) & (self.df["score"] <= 10)]

        self.df['review_length'] = self.df['review'].str.split().apply(len)
        self.df['review_length_zscore'] = zscore(self.df['review_length'])
        self.df = self.df[(self.df['review_length_zscore'] >= -3) & (self.df['review_length_zscore'] <= 3)]
        self.df = self.df.drop(columns=['review_length', 'review_length_zscore'])

    def feature_engineering(self):
        self.df['month'] = self.df["date"].dt.strftime('%Y-%m')
        self.df['day'] = self.df["date"].dt.day

        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df['review'])
        tfidf_feature_names = vectorizer.get_feature_names_out()
        self.df['tfidf_features'] = [
            ', '.join(f"{word}:{tfidf:.2f}" for word, tfidf in zip(tfidf_feature_names, row) if tfidf > 0)
            for row in tfidf_matrix.toarray()
        ]
        self.df = self.df[self.df['tfidf_features'] != '']

    def save_to_database(self):
        file_name = "preprocessed_reviews_RTC.csv"
        file_path = os.path.join(self.output_path, file_name)
        if isinstance(self.df, pd.DataFrame):
            self.df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")
