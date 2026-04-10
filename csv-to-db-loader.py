import pandas as pd
import sqlite3
import os

# 1. 설정
csv_file = 'rfp_summary-manual-edit.csv'
db_path = 'projects.db'

def build_db_from_csv():
    # CSV 파일 존재 확인
    if not os.path.exists(csv_file):
        print(f"오류: {csv_file} 파일을 찾을 수 없습니다.")
        return

    # 2. CSV 읽기
    # 엑셀에서 저장한 CSV일 경우를 대비해 encoding 설정
    df = pd.read_csv(csv_file, encoding='utf-8-sig')

    # 3. 컬럼명 변경 (한글 -> 영어, DB 쿼리 편의용)
    # 기존: 학교, 코드 번호, 제목, Name, Strategic field, Keywords
    df.columns = ['school', 'id', 'title', 'name', 'strategic_field', 'keywords']

    # 4. DB 연결 및 저장
    conn = sqlite3.connect(db_path)
    
    # 기존 테이블이 있으면 삭제하고 새로 생성 (초기화)
    # 만약 데이터가 섞여서 들어가는걸 방지하려면 replace를 사용합니다.
    df.to_sql('projects', conn, if_exists='replace', index=False)
    
    # 인덱스 생성 (검색 속도 향상을 위해 id와 title에 인덱스 추가)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_id ON projects(id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_title ON projects(title)")
    
    conn.commit()
    conn.close()

    print("-" * 30)
    print(f"성공: {len(df)}개의 데이터를 {db_path}의 'projects' 테이블에 저장했습니다.")
    print(f"사용된 컬럼: {list(df.columns)}")

if __name__ == "__main__":
    build_db_from_csv()