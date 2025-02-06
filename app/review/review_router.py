from fastapi import APIRouter, HTTPException
from database.mongodb_connection import mongo_db  # MongoDB 연결 가져오기
from review_analysis.preprocessing.IMDBProcessor import IMDBProcessor
from review_analysis.preprocessing.RTProcessor import RTProcessor
from review_analysis.preprocessing.MetaProcessor import MetaProcessor

router = APIRouter()

# 사이트별 전처리 클래스 매핑
PREPROCESS_CLASSES = {
    "IMDB": IMDBProcessor,
    "RottenTomato": RTProcessor,  # 컬렉션 이름과 일치하도록 수정
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

    # 해당 사이트의 전처리 클래스 가져오기
    preprocessor_class = PREPROCESS_CLASSES[site_name]
    
    # 전처리 클래스 인스턴스 생성
    preprocessor = preprocessor_class()

    # 데이터 전처리 실행
    processed_reviews = preprocessor.preprocess()
    preprocessor.feature_engineering()

    # MongoDB 업데이트
    for review_id, processed_review in processed_reviews.items():
        collection.update_one({"_id": review_id}, {"$set": {"processed_review": processed_review}})

    return {"message": f"{site_name} 리뷰 전처리 완료"}
