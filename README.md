
# YBIGTA 26기 2조 팀 프로젝트

## 프로젝트 소개
이 프로젝트는 YBIGTA 26기 2조 구성원들이 협업하여 **교육세션 팀 프로젝트**를 수행하는 것입니다.  
주요 목표는 **빅데이터 및 활용 방안에 대한 이해**를 높이고, 팀원 간의 협업 능력을 강화하는 데 있습니다.

---

## 팀 및 팀원 소개
YBIGTA 26기 2조는 팀장 윤희찬, 팀원 임재민, 정민지 3인으로 구성되어 있습니다.

### 팀장 윤희찬
| 항목                 | 내용                                         |
|----------------------|---------------------------------------------|
| 학과 및 학번          | 응용통계학과 20학번                         |
| 지원 팀              | DA팀 희망                                    |
| 장래희망             | 엔지니어                                     |
| 관심 분야            | 현재로선 YBIGTA                              |
| 특기/장점            | 일단 해본다                                  |
| MBTI                | INFJ                                         |
| 좋아하는 음악        | old castle by the river in the middle of a forest |
| 여가 시간 활동       | 피아노 / 헬스                                |
| 하고 싶은 한마디       | 잘 부탁드립니다!                             |

### 팀원 임재민
| 항목                 | 내용                                         |
|----------------------|---------------------------------------------|
| 학과 및 학번          | 경영학과 19학번                         |
| 지원 팀              | DA팀 희망                                    |
| 장래희망             | 데이터 마케터                                |
| 관심 분야            | 현재로선 YBIGTA                              |
| 특기/장점            | 꼼꼼함, 이해될 때까지 반복                    |
| MBTI                | ESFJ                                         |
| 좋아하는 음악        | 밴드음악, LUCY - 아지랑이, 낙화                |
| 여가 시간 활동       | 게임, 헬스                                |
| 하고 싶은 한마디       | 좋은 분들과 학회를 통해 계속 성장하고 싶습니다! |

### 팀원 정민지
| 항목                 | 내용                                         |
|----------------------|---------------------------------------------|
| 학과 및 학번          | 인공지능학과 23학번                         |
| 지원 팀              | DS팀 희망                                    |
| 장래 희망             | 개발자, 데이터 과학자                        |
| 관심 분야            | 코딩, 딥러닝                                 |
| 특기/장점            | 처음에는 부족하더라도 꾸준히 성장하며 점점 더 나아지는 편 |
| MBTI                | ENFP                                         |
| 좋아하는 음악        | K-Pop, 데이식스 밴드 노래                    |
| 여가 시간 활동        | OTT 시청, 독서                              |
| 하고 싶은 한마디       | 학회를 통해 많은 것을 배우고 싶습니다. 잘 부탁드립니다! |


---

## 설치 및 실행 방법

### 1. Repository 클론
먼저 로컬 환경에 프로젝트를 클론합니다:

```bash
git clone https://github.com/quant-jason/YBIGTA_newbie_team_project.git
```

### 2. 프로젝트 디렉토리로 이동
클론한 디렉토리로 이동합니다:

```bash
cd YBIGTA_newbie_team_project/app
```

### 3. Python 서버 실행
터미널에서 아래 명령어를 실행하여 서버를 실행합니다:

```bash
uvicorn main:app --reload
```

### 4. 웹 애플리케이션 접속
브라우저를 열고 다음 주소로 이동하여 애플리케이션을 확인합니다:

```
http://127.0.0.1:8000
```

---

## 팀원 별 Merge 현황

![윤희찬 merge](github/merged_quant-jason.png)
![임재민 merge](github/merged_jaeminl3.png)
![정민지 merge](github/merged_mjxjung.png)

## 크롤링 및 전처리 설치 및 실행 방법

실행방법 - vscode에서 venv가상환경 실행을 기준으로 설명합니다! 
(windows vscode 기준이므로 Mac/Linux 환경의 경우 명령어가 다를 수 있습니다)

1. 가상환경(venv) 활성화
- 루트 디렉토리에서 다음 명령어 실행 python -m venv venv
- 의존성 설치 : pip install -r requirements.txt

2. PYTHONPATH 설정
Vscode powershell 기준 : $env:PYTHONPATH = "설정하고자하는 경로 -> YBIGTA_newbie_team_project파일을 경로로 설정하시면 됩니다"

3. 크롤링 파일 실행
- 현재 파일 위치 변경 : cd "~/review_analysis/crawling"
- 실행 명령어 : python main.py --all

4. 전처리 파일 실행 
-현재 파일 위치 변경 : cd "~/review_analysis/preprocessing"
- 실행 명령어 : python main.py --all