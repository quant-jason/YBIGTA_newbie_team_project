from fastapi import APIRouter, HTTPException
from database.mongodb_connection import mongo_db  # MongoDB 연결 가져오기
from review_analysis.preprocessing.IMDBProcessor import IMDBProcessor
from review_analysis.preprocessing.RTProcessor import RTProcessor
from review_analysis.preprocessing.MetaProcessor import MetaProcessor
import pandas as pd  # 🚀 MongoDB 데이터를 DataFrame으로 변환하기 위해 추가

router = APIRouter()

# 사이트별 전처리 클래스 매핑
PREPROCESS_CLASSES = {
    "IMDB": IMDBProcessor,
    "RottenTomato": RTProcessor,  
    "Metacritic": MetaProcessor
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
    preprocessor = preprocessor_class(df, output_path=None)  # ✅ `input_path` 없이 직접 DataFrame 전달

    # 데이터 전처리 실행
    preprocessor.preprocess()
    preprocessor.feature_engineering()

    # MongoDB 업데이트
    for _, row in preprocessor.df_cleaned.iterrows():
        collection.update_one({"_id": row["_id"]}, {"$set": row.to_dict()})

    return {"message": f"{site_name} 리뷰 전처리 완료", "processed_count": len(preprocessor.df_cleaned)}
