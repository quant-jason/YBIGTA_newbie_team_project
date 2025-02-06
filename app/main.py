from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import uvicorn
import os

# 라우터 추가
from app.user.user_router import user
from app.review.review_router import router as review_router  # 리뷰 API 추가

# 환경 변수에서 포트 가져오기 (기본값 8000)
PORT = int(os.getenv("PORT", 8000))

app = FastAPI()

# 정적 파일 제공 (static 폴더 내 파일 제공)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 라우터 등록
app.include_router(user)
app.include_router(review_router)  #전처리 api 추가

@app.get("/")
def root():
    """index.html을 반환하여 웹사이트로 이동"""
    return FileResponse("app/static/index.html")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
