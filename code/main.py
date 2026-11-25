import streamlit as st
import pandas as pd
import numpy as np

st.title("닭강정 팀 프로젝트")
st.header("처벌이 강할수록 범죄가 정말 줄어들까?")

# --- 1. 데이터 불러오기 ---
filepath = 'data/전과자_재범기간_및_종류_20261125122139.xlsx'
df_raw = pd.read_excel(filepath, sheet_name='데이터', header=None)
data = df_raw.iloc[3:].copy().reset_index(drop=True)

# --- 2. 데이터 개요 (체크리스트 1번) ---
st.subheader("1. 원본 데이터 개요")
st.write(f"- **총 데이터 크기:** {data.shape[0]}행(Row) × {data.shape[1]}열(Column)")

# 열마다 자료형과 빈 값(결측치) 개수 보여주기
summary_df = pd.DataFrame({
    '자료형': data.dtypes.astype(str),
    '빈 값(결측치) 개수': data.isna().sum()
})
st.dataframe(summary_df)

# --- 3. 데이터 전처리 ---
cols = [
    '범죄별_1', '범죄별_2', '범죄별_3', '합계',
    '동종_소계', '동종_1개월이내', '동종_3개월이내', '동종_6개월이내', '동종_1년이내', '동종_2년이내', '동종_3년이내', '동종_3년초과',
    '이종_소계', '이종_1개월이내', '이종_3개월이내', '이종_6개월이내', '이종_1년이내', '이종_2년이내', '이종_3년이내', '이종_3년초과'
]
data.columns = cols

data['범죄별_1'] = data['범죄별_1'].ffill()
data['범죄별_2'] = data['범죄별_2'].ffill()

for c in cols[3:]:
    data[c] = pd.to_numeric(data[c].replace('-', 0), errors='coerce').fillna(0)

is_leaf = (
    ((data['범죄별_1'] == '형법범') & (data['범죄별_3'] != '소계')) |
    ((data['범죄별_1'] == '특별법범') & (data['범죄별_2'] != '소계'))
)

leaves = data[is_leaf & (data['합계'] > 0)].copy().reset_index(drop=True)
leaves['범죄명'] = np.where(leaves['범죄별_3'] != '소계', leaves['범죄별_3'], leaves['범죄별_2'])

leaves['동종재범률'] = leaves['동종_소계'] / leaves['합계']
leaves['단기1년재범률'] = (
    leaves['동종_1개월이내'] + leaves['동종_3개월이내'] + leaves['동종_6개월이내'] + leaves['동종_1년이내'] +
    leaves['이종_1개월이내'] + leaves['이종_3개월이내'] + leaves['이종_6개월이내'] + leaves['이종_1년이내']
) / leaves['합계']
leaves['장기3년초과재범률'] = (leaves['동종_3년초과'] + leaves['이종_3년초과']) / leaves['합계']

features = ['범죄명', '합계', '동종재범률', '단기1년재범률', '장기3년초과재범률']
df_final = leaves[features].copy()

# --- 4. 전처리 결과 및 기준 (체크리스트 5번) ---
st.subheader("2. 데이터 전처리 결과")
st.write("- **처리 기준:** 중복 집계를 막기 위해 '소계' 행을 빼고 세부 범죄만 남겼으며, 재범자가 0명인 빈 데이터 1건을 삭제했습니다.")
st.write(f"- **처리 전:** {data.shape[0]}행 ➔ **처리 후:** {df_final.shape[0]}행")
st.dataframe(df_final)

# --- 5. 탐색적 데이터 분석 그래프 (체크리스트 2번) ---
st.subheader("3. 탐색적 데이터 분석 (EDA)")
st.write("#### 📊 동종재범률 상위 10개 범죄")
st.caption("X축: 범죄명 / Y축: 동종재범률 (예: 0.5 = 50%)")

# 동종재범률 기준 내림차순 정렬 후 상위 10개 추출
top10 = df_final.sort_values('동종재범률', ascending=False).head(10)
chart_data = top10.set_index('범죄명')[['동종재범률']]

# 바 차트 그리기
st.bar_chart(chart_data)
