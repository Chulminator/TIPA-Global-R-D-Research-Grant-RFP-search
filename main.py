import inspect
import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(page_title="RFP 검색 엔진", layout="wide")
st.title("글로벌 협력형 과제 RFP 통합 검색 시스템")

# 1. DB에서 데이터 가져오는 함수 (필드 추가)
def get_filtered_data(school_filter, keyword):
    conn = sqlite3.connect("projects.db")
    
    # 데이터 추가: name, strategic_field, keywords 포함
    query = "SELECT id, school, title, name, strategic_field, keywords FROM projects WHERE 1=1"
    params = []

    if school_filter != "전체":
        query += " AND school = ?"
        params.append(school_filter)
    
    if keyword:
        query += " AND (title LIKE ? OR keywords LIKE ? OR name LIKE ? OR strategic_field LIKE ?)"
        search_param = f"%{keyword}%"
        params.append(search_param)
        params.append(search_param)
        params.append(search_param)
        params.append(search_param)
        
    df = pd.read_sql(query, conn, params=params)
    if "pi" not in df.columns and "name" in df.columns:
        df["pi"] = df["name"]
    conn.close()
    return df

# --- 기존 유틸리티 함수 유지 (수정 없음) ---
_TITLE_WIDTH_SAFETY_CAP_PX = 25000
# Title column max width (px); long text uses horizontal scroll in the grid.
_TITLE_COL_MAX_PX = 480
_DF_MAX_HEIGHT_BEFORE_SCROLL_PX = 420
_DF_APPROX_HEADER_PX = 56
_DF_APPROX_ROW_PX = 36

def _dataframe_height_for_row_count(n_rows: int):
    approx = _DF_APPROX_HEADER_PX + n_rows * _DF_APPROX_ROW_PX
    if approx <= _DF_MAX_HEIGHT_BEFORE_SCROLL_PX: return "content"
    return _DF_MAX_HEIGHT_BEFORE_SCROLL_PX

def _autosize_column_width_px(series, header: str, *, char_px: float = 8.2, padding_px: float = 0.0, min_px: int = 72, max_px: int | None = 400, safety_cap_px: int = _TITLE_WIDTH_SAFETY_CAP_PX) -> int:
    lengths = [len(str(v)) for v in series.dropna().tolist()]
    max_cells = max(lengths) if lengths else 0
    max_len = max(max_cells, len(header))
    w = int(max_len * char_px + padding_px)
    w = max(w, min_px)
    if max_px is not None: w = min(w, max_px)
    else: w = min(w, safety_cap_px)
    return w

def _text_column_aligned(label: str, width: int, alignment: str = "left"):
    tc = st.column_config.TextColumn
    if "alignment" in inspect.signature(tc).parameters:
        return tc(label, width=width, alignment=alignment)
    return tc(label, width=width)

# 2. UI 레이아웃 구성
st.write("### 🔍 필터링 조건")
col1, col2 = st.columns([1, 3])

with col1:
    # 확장된 학교 리스트
    school_list = ["전체", "Georgia Tech", "Mass General Brigham", "UIUC", "Johns Hopkins University", "Purdue University", "Fraunhofer", "Steinbeis", "TNO", "CSEM", "University of Toronto", "RPI"]
    selected_school = st.selectbox("학교 선택", school_list)

with col2:
    search_title = st.text_input("RFP 검색", placeholder="예: AI, Robotic, Semiconductor")

# 3. 검색 로직
if selected_school != "전체" or search_title:
    df = get_filtered_data(selected_school, search_title)

    if not df.empty:
        st.write(f"📊 총 {len(df)}건의 검색 결과")

        # 기존 컬럼 너비 설정 유지
        id_w = _autosize_column_width_px(df["id"], "ID", max_px=360)
        school_w = _autosize_column_width_px(df["school"], "School", max_px=None, safety_cap_px=900)
        title_w = _autosize_column_width_px(
            df["title"], "Title", max_px=_TITLE_COL_MAX_PX, safety_cap_px=_TITLE_COL_MAX_PX
        )
        
        # 추가된 컬럼 너비 자동 설정
        pi_w = _autosize_column_width_px(df["pi"], "PI", max_px=220)

        df_height = _dataframe_height_for_row_count(len(df))
        
        event = st.dataframe(
            df,
            width="content",
            height=df_height,
            hide_index=True,
            column_order=["id", "school", "pi", "title"],
            column_config={
                "id": _text_column_aligned("ID", id_w, "center"),
                "school": _text_column_aligned("School", school_w, "center"),
                "pi": _text_column_aligned("PI", pi_w, "center"),
                "title": _text_column_aligned("Title", title_w, "left"),
                "name": None,
                "strategic_field": None,
                "keywords": None,
            },
            on_select="rerun",
            selection_mode="single-row",
        )

        selected_rows = event.selection.rows if hasattr(event, "selection") else []
        
        if selected_rows:
            row_index = selected_rows[0]
            selected_data = df.iloc[row_index]
            
            st.divider()
            st.success(f"선택됨: **[{selected_data['id']}] {selected_data['title']}**")
            
            # 상세 정보 표시
            col_info1, col_info2 = st.columns([1, 1]) # 1:1 비율로 분할
            
            with col_info1:
                st.write(f"**👤 PI:** {selected_data['pi']}")
            
            with col_info2:
                st.write(f"**🛡️ 전략기술분야:** {selected_data['strategic_field']}")
            
            # 학교별 링크 설정
            SCHOOL_ZIP_URLS = {
                "Georgia Tech": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C45013B69C5221F38A",
                "Mass General Brigham": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C4FECBE682DAA8AA28",
                "UIUC": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C41FDEB5EE4AB0C2DC",
                "Johns Hopkins University": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C4B61B4C9998FBD128",
                "Purdue University": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C43886E343AC7E602D",
                "Fraunhofer": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C49B6CA82A926D3EF9",
                "Steinbeis": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C43E38D3947F4AF9EF",
                "TNO": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C4A47E0BB60C18CAD0",
                "CSEM": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C434EBD1ED9432C9DA",
                "University of Toronto": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C414856E3B770732A5",
                "RPI": "https://www.smtech.go.kr/front/comn/AtchFileDownload.do?atchFileId=A63D835ABC54F9C4F81A562B2F44B84D",
            }
            download_url = SCHOOL_ZIP_URLS.get(selected_data['school'], "#")
            st.link_button(f"📄 {selected_data['school']} RFP 전체 다운로드", download_url, type="primary")
            
    else:
        st.warning("일치하는 결과가 없습니다.")