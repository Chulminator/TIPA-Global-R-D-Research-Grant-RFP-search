import os
import re
import csv
import fitz  # PyMuPDF
import pandas as pd
from datetime import datetime

# 1. 설정
base_path = r"G:\My Drive\TIPA-USA-Chulmin\12-global-cooperation-searching-engine\RFP목록"
output_csv = "rfp_summary.csv"
log_file = "log.txt"

def write_log(message):
    """오류 내용을 log.txt 파일에 추가 기록"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")

def extract_pdf_content(pdf_path):
    """PDF 내부에서 Name, Strategic Field, Keywords를 추출하는 함수"""
    try:
        doc = fitz.open(pdf_path)
        first_page_text = doc[0].get_text() + "\n" + doc[1].get_text()
        doc.close()
        
        # (1) 제안자 이름 (Name) 추출
        name_match = re.search(r"Name\s*\n\s*([^\n,]+)", first_page_text)
        proposer_name = name_match.group(1).strip() if name_match else "Not Found"

        # (2) 전략 기술 분야 (Strategic Field) 추출
        target_list = [
            "Semiconductor/Display", "Secondary Battery", "Advanced Mobility", 
            "Next-gen Nuclear Power", "Advanced Bio", "Aerospace/Marine", 
            "Hydrogen", "Cybersecurity", "AI", "Next-gen Communication", 
            "Advanced Robotics & Manufacturing", "Quantum", "Others"
        ]
        tech_matches = re.findall(r"([^,(\n]+)\s*\(([^)]*)\)", first_page_text)
        selected_tech = []
        for name, mark in tech_matches:
            clean_name = name.strip()
            if clean_name in target_list and mark.strip():
                selected_tech.append(clean_name)
        if selected_tech == []:
            selected_tech = "None"
        selected_tech_str = ", ".join(selected_tech)

        # (3) 세부 카테고리 (Keywords) 추출
        pattern = r"Technology Field 1.*?Concept of"
        section_match = re.search(pattern, first_page_text, re.DOTALL)
        keywords_list = []
        if section_match:
            extracted_section = section_match.group()
            exclude_list = ["Technology", "Medium", "Small", "Proposed", "Concept"]
            lines = extracted_section.split('\n')
            for line in lines:
                clean_line = line.strip()            
                if clean_line and clean_line.split()[0] not in exclude_list:
                    keywords_list.append(clean_line)
        
        keywords_str = ", ".join(keywords_list)
        return proposer_name, selected_tech_str, keywords_str

    except Exception as e:
        # PDF 읽기 또는 파싱 중 발생하는 모든 에러를 로그에 기록
        write_log(f"오류 발생 파일: {pdf_path} | 내용: {str(e)}")
        return "Error", "Error", "Error"

def main():
    # 로그 파일 초기화 (새로 시작할 때마다 이전 로그 삭제하려면 'w', 누적하려면 'a')
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"=== 작업 시작: {datetime.now()} ===\n")

    if not os.path.exists(base_path):
        error_msg = f"오류: 경로를 찾을 수 없습니다 -> {base_path}"
        print(error_msg)
        write_log(error_msg)
        return

    school_map = {
        "GT": "Georgia Tech",
        "MGB": "Mass General Brigham",
        "UIUC": "UIUC",
        "JHU": "Johns Hopkins University",
        "PD": "Purdue University",
        "FH": "Fraunhofer",
        "SB": "Steinbeis",
        "TN": "TNO",
        "CS": "CSEM",
        "UT": "University of Toronto",
        "RPI": "RPI",
    }

    results = []
    print(f"작업 시작: {base_path}")

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if not filename.endswith(".pdf"): continue

            match = re.match(r"\[(.*?)\]\s*(.*)", filename)
            if match:
                p_id = match.group(1).strip()
                p_title = match.group(2).strip() # 파일명에서 제목 추출 
                p_title = os.path.splitext(p_title)[0] # 확장자(.pdf) 제거
                
                school_code = p_id.split('-')[0]
                school = school_map.get(school_code, "Other")
                
                full_path = os.path.join(root, filename)
                
                # PDF 정보 추출
                name, strategic_field, keywords = extract_pdf_content(full_path)
                
                # 추출 결과가 Error가 아닌 경우에만 리스트에 추가 (필요시 수정 가능)
                results.append({
                    "학교": school,
                    "코드 번호": p_id,
                    "제목": p_title,
                    "Name": name,
                    "Strategic field": strategic_field,
                    "Keywords": keywords
                })
                print(f"처리 완료: {p_id}")
            else:
                # 파일명 형식이 [ID] 형식이 아닐 경우 로그 기록
                write_log(f"파일명 형식 불일치 무시됨: {filename}")

    # CSV 저장
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print("-" * 30)
        final_msg = f"성공: 총 {len(results)}개의 데이터를 {output_csv}에 저장했습니다."
        print(final_msg)
        write_log(final_msg)
    else:
        print("추출된 데이터가 없습니다.")
        write_log("추출된 데이터 없음.")

if __name__ == "__main__":
    main()