from fastapi import APIRouter, HTTPException
from database.mongodb_connection import mongo_db  # MongoDB 연결 가져오기
from review_analysis.preprocessing.IMDBProcessor import DataFrameProcessor
from review_analysis.preprocessing.RTProcessor import DataFrameProcessor
from review_analysis.preprocessing.MetaProcessor import DataFrameProcessor
import pandas as pd  # 🚀 MongoDB 데이터를 DataFrame으로 변환하기 위해 추가

router = APIRouter()

# 사이트별 전처리 클래스 매핑
PREPROCESS_CLASSES = {
    "IMDB": DataFrameProcessor,
    "RottenTomato": DataFrameProcessor,
    "Metacritic": DataFrameProcessor
}

@router.post("/review/preprocess/{site_name}")
def preprocess_reviews(site_name: str):
    """
    영화 사이트의 리뷰 데이터를 가져와 전처리 후 MongoDB에 저장하는 API
    """
    if site_name not in PREPROCESS_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid site name")

    # MongoDB 컬렉션 가져오기
    collection = mongo_db[site_name]

    # MongoDB에서 데이터 불러오기
    reviews = list(collection.find({}, {"_id": 1, "date": 1, "review": 1, "score": 1}))  # 필요한 필드만 가져오기

    if not reviews:
        raise HTTPException(status_code=404, detail=f"No reviews found for {site_name}")

    # 데이터를 DataFrame으로 변환
    df = pd.DataFrame(reviews)

    # `_id`를 문자열로 변환하여 저장
    df["_id"] = df["_id"].astype(str)

    # 전처리 클래스 가져오기
    preprocessor_class = PREPROCESS_CLASSES[site_name]
    
    # 전처리 클래스 인스턴스 생성 (MongoDB 데이터를 직접 전달)
    preprocessor = preprocessor_class(df)  

    # 데이터 전처리 실행
    preprocessor.preprocess()
    preprocessor.feature_engineering()
    
    # 전처리된 데이터프레임 가져오기
    df_cleaned = preprocessor.get_cleaned_dataframe()

    # 기존 데이터 삭제 (특정 사이트에 대한 리뷰 데이터 삭제)
    collection.delete_many({})  # 전체 데이터를 삭제합니다. 필요한 경우 조건을 추가할 수 있습니다.

    # 전처리된 데이터 저장 (MongoDB에 삽입)
    # `_id`를 새로 생성하지 않고, DataFrame의 `_id`를 그대로 사용하려면 다음과 같이 `to_dict()`로 변환
    collection.insert_many(df_cleaned.to_dict(orient='records'))  # 새로운 데이터 삽입

    return {"message": f"Successfully processed and updated reviews for {site_name}."}