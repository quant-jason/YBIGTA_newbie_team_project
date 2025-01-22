from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from scipy.stats import zscore  # type: ignore

class MetaProcessor(BaseDataProcessor):
    """
    Processor for cleaning and feature engineering of Meta reviews.

    Attributes:
        input_path (str): Path to the input file.
        output_path (str): Path to save the processed file.
        df (pd.DataFrame): DataFrame containing the raw data.
        df_cleaned (pd.DataFrame): DataFrame containing the cleaned data.
    """
    
    def __init__(self, input_path: str, output_path: str):
        """
        Initializes the MetaProcessor with input and output paths.

        Args:
            input_path (str): Path to the raw input data file.
            output_path (str): Directory path to save the processed data file.
        """
        super().__init__(input_path, output_path)
        self.input_path = input_path
        self.output_path = output_path
        self.df = pd.read_csv(input_path, na_values=["N/A"])

    def preprocess(self):
        """
        Cleans the raw data by handling missing values, filtering outliers, and formatting dates.

        Steps:
            - Removes rows with missing values.
            - Converts date strings to datetime objects.
            - Filters out reviews outside the range of valid scores (1 to 10).
            - Removes reviews with excessively short or long text based on z-scores.
        """

        print("Preprocessing started") # 지우기
        self.df_cleaned = self.df.dropna()
        self.df_cleaned['date'] = pd.to_datetime(self.df_cleaned['date'], format='%b %d, %Y', errors='coerce')
        self.df_cleaned = self.df_cleaned.dropna(subset=['date'])
        self.df_cleaned = self.df_cleaned[(self.df_cleaned['score'] >= 1) & (self.df_cleaned['score'] <= 10)]

        self.df_cleaned['review_length'] = self.df_cleaned['review'].str.split().apply(len)
        self.df_cleaned['review_length_zscore'] = zscore(self.df_cleaned['review_length'])
        self.df_cleaned = self.df_cleaned[
            (self.df_cleaned['review_length_zscore'] >= -3) &
            (self.df_cleaned['review_length_zscore'] <= 3)
        ]
        self.df_cleaned = self.df_cleaned.drop(columns=['review_length', 'review_length_zscore'])
        print("Preprocessing over") # 지우기

    def feature_engineering(self):
        """
        Generate new features for the dataset.

        Steps:
        - Extract month and day from the date column.
        - Apply TF-IDF vectorization to the review text.
        """
        print("feature start") # 지우기
        self.df_cleaned['month'] = self.df_cleaned['date'].dt.strftime('%Y-%m')
        self.df_cleaned['day'] = self.df_cleaned['date'].dt.day_name()

        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform(self.df_cleaned['review'])
        tfidf_feature_names = vectorizer.get_feature_names_out()
        self.df_cleaned['tfidf_features'] = [
            ', '.join(f"{word}:{tfidf:.2f}" for word, tfidf in zip(tfidf_feature_names, row) if tfidf > 0)
            for row in tfidf_matrix.toarray()
        ]
        self.df_cleaned = self.df_cleaned[self.df_cleaned['tfidf_features'] != '']
        print("feature over") # 지우기

    def save_to_database(self):
        """
        Saves the processed data to a CSV file.

        File:
            The file is saved to the specified output directory with the name "preprocessed_reviews_Meta.csv".

        Checks:
            - Ensures the cleaned DataFrame exists before saving.
        """
        print("saving start") # 지우기
        file_name = "preprocessed_reviews_Meta.csv"
        file_path = os.path.join(self.output_path, file_name)
        if isinstance(self.df_cleaned, pd.DataFrame):
            self.df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
            print(f"Saved data to: {file_path}")
        else:
            print("No data to save.")
        print("saving done") # 지우기
