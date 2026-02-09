from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

# ==========================================
# 1. 데이터베이스 설정 (원래 database.py 있던 내용)
# ==========================================
# 본인 DB 정보에 맞게 수정하세요 (사용자명:비번@주소:포트/DB명)
DATABASE_URL = "postgresql+asyncpg://korea:rose100!@localhost:5432/homework_20260206"

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)

# 세션 생성기
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 의존성 주입 함수 (DB 연결을 빌려주고 반납하는 역할)
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# ==========================================
# 2. API 설정 (원래 main.py 있던 내용)
# ==========================================
app = FastAPI()

allowed_origins = [
    "http://localhost:3000",
    #"http://localhost:3001",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 제품 조회 API
@app.get("/productList")
async def get_products(db: AsyncSession = Depends(get_db)):
    # 쿼리 안에 :param 같은 변수가 없다면 text()로 감싸서 바로 실행 가능
    query = text("""
        SELECT
            prod_cate.제품분류명 AS categoryname,
            prod.제품코드 AS productcode,
            prod.제품명 as productname,
            CASE prod.색상
                WHEN 'Red'   THEN '빨간색'
                WHEN 'Grey'  THEN '회색'
                WHEN 'Black' THEN '검정색'
                WHEN 'Pink'  THEN '분홍색'
                WHEN 'Blue'  THEN '파란색'
                WHEN 'Green' THEN '초록색'
                WHEN 'Gold'  THEN '금색'
                WHEN 'White' THEN '흰색'
                WHEN 'Brown' THEN '갈색'
                ELSE prod.색상
            END AS color,
            prod.원가 AS costprice,
            prod.단가 AS unitprice
        FROM products prod
        LEFT OUTER JOIN product_categories prod_cate
        ON prod.제품분류코드 = prod_cate.제품분류코드
        ORDER BY prod_cate.제품분류명 COLLATE "und-x-icu" ASC,
                 prod.제품명 COLLATE "und-x-icu" ASC
    """)
    result = await db.execute(query)
    return result.mappings().all()

# 고객 조회 API
@app.get("/customerList")
async def get_customers(db: AsyncSession = Depends(get_db)):
    query = text("""SELECT
            t2.시도 || ' ' || t2.구군시 AS region,
            t1.고객코드 AS customerCode,
            t1.고객명 AS  customerName,
            t1.성별 AS gender,
            TO_CHAR(t1.생년월일, 'YYYY.MM.DD') AS brithDate
        FROM purchasing_customers t1
        LEFT OUTER JOIN regions t2
        ON t1.지역코드 = t2.지역코드
        order by region desc , 고객명 asc
    """)
    result = await db.execute(query)
    return result.mappings().all()