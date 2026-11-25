import streamlit as st
import pandas as pd
import numpy as np

# --- 1. 웹 화면에 제목과 설명 출력하기 ---
st.title("닭강정 팀 프로젝트")
st.header("처벌이 강할수록 범죄가 정말 줄어들까?")
st.write("공소청 2024년 전과자 재범기간 데이터를 전처리한 결과입니다.")

# --- 2. 데이터 불러오기 및 전처리 (기존과 동일) ---
filepath = 'data/전과자_재범기간_및_종류_20261125122139.xlsx'
df_raw = pd.read_excel(filepath, sheet_name='데이터', header=None)
data = df_raw.iloc[3:].copy().reset_index(drop=True)

cols = [
    '범죄별_1', '범죄별_2', '범죄별_3',
    '합계',
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
    leaves['이종_1개월이내'] + float(0) if leaves['합계'].sum() == 0 else
    leaves['이종_3개월이내'] + leaves['이종_6개월이내'] + leaves['이종_1년이내']
) / leaves['합계']

# 위의 식을 더 간결하고 안전하게 계산
leaves['단기1년재범률'] = (
    leaves['동종_1개월이내'] + leaves['동종_3개월이내'] + leaves['동종_6개월이내'] + leaves['동종_1년이내'] +
    leaves['이종_1개월이내'] + leaves['이종_3개월이내'] + leaves['이종_6개월이내'] + leaves['이종_1년이내']
) / leaves['합계']

leaves['장기3년초과재범률'] = (leaves['동종_3년초과'] + leaves['이종_3년초과']) / leaves['합계']

features = ['범죄명', '합계', '동종재범률', '단기1년재범률', '장기3년초과재범률']
df_final = leaves[features].copy()

# --- 3. 웹 화면에 표(데이터프레임) 그려주기 ---
st.subheader("전처리 완료된 데이터 (최종 110개 범죄)")
st.dataframe(df_final)
