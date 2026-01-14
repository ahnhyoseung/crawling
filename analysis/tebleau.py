import pandas as pd
import re
from collections import Counter
import os

# CSV 파일명 입력 (실제 파일명으로 변경하세요)
INPUT_FILE = "data/utube/youtube_comments_20260107_093854.csv"

OUTPUT_DIR = "data"
# CSV 로드
df = pd.read_csv(INPUT_FILE)
print(f"📊 전체 댓글 수: {len(df)}")
print(f"📊 총 좋아요 수: {df['좋아요'].sum()}")

# ===========================================
# 1. 기본 통계 정보 추가
# ===========================================
df['댓글_길이'] = df['댓글'].str.len()
df['단어_수'] = df['댓글'].str.split().str.len()
df['댓글_ID'] = range(1, len(df) + 1)

# ===========================================
# 2. 좋아요 구간 분류
# ===========================================
def categorize_likes(likes):
    if likes >= 100:
        return '100+ 좋아요'
    elif likes >= 50:
        return '50-99 좋아요'
    elif likes >= 10:
        return '10-49 좋아요'
    elif likes >= 1:
        return '1-9 좋아요'
    else:
        return '0 좋아요'

df['좋아요_구간'] = df['좋아요'].apply(categorize_likes)

# ===========================================
# 3. 키워드 추출 및 분석
# ===========================================
stopwords = {
    # 영어
    "the", "is", "to", "and", "of", "a", "in", "that", "it", "for",
    # 한글 불용어
    "이거", "그냥", "진짜", "정말", "너무", "것", "수", "있다", "없다",
    "ㅋㅋ", "ㅋㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㄷㄷ",
    "br", "lt", "gt", "amp", "nbsp",
    "그", "저", "이", "뭐", "왜"
}

# 전체 댓글에서 키워드 추출
all_words = []
for text in df['댓글']:
    text = re.sub(r'<[^>]+>', '', str(text))
    text = re.sub(r'[^\w\s가-힣]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    tokens = text.split()
    tokens = [w for w in tokens if len(w) >= 2 and not w.isdigit() and w not in stopwords]
    all_words.extend(tokens)

# 상위 키워드 추출
top_keywords = [word for word, count in Counter(all_words).most_common(15)]
print(f"\n🔑 상위 15개 키워드: {', '.join(top_keywords)}")

# 각 댓글에 키워드 포함 여부 체크
for keyword in top_keywords:
    df[f'키워드_{keyword}'] = df['댓글'].str.contains(keyword, case=False, na=False).astype(int)

# ===========================================
# 4. 감성 분석 (키워드 방식)
# ===========================================
print("\n💭 키워드 기반 감성 분석 시작...")

positive_words = ['좋', '최고', '대박', '감사', '멋', '훌륭', '완벽', '사랑', '예쁘', '이쁘', '굿', '최고다', '좋네', '좋아']
negative_words = ['별로', '싫', '나쁘', '최악', '실망', '짜증', '화', '이상', '안좋', '나쁘네']

df['긍정단어_수'] = df['댓글'].apply(
    lambda x: sum(1 for word in positive_words if word in str(x))
)
df['부정단어_수'] = df['댓글'].apply(
    lambda x: sum(1 for word in negative_words if word in str(x))
)

def classify_sentiment(row):
    if row['긍정단어_수'] > row['부정단어_수']:
        return '긍정'
    elif row['부정단어_수'] > row['긍정단어_수']:
        return '부정'
    else:
        return '중립'

df['감성'] = df.apply(classify_sentiment, axis=1)

print("✅ 감성 분석 완료!")

# ===========================================
# 5. 파일 저장
# ===========================================

# 메인 데이터
output_main = os.path.join(OUTPUT_DIR, "youtube_comments_tableau.csv")
df.to_csv(output_main, index=False, encoding='utf-8-sig')
print(f"\n✅ '{output_main}' 저장 완료!")

# 키워드별 통계
keyword_stats = []
for keyword in top_keywords:
    keyword_df = df[df[f'키워드_{keyword}'] == 1]
    if len(keyword_df) > 0:
        keyword_stats.append({
            '키워드': keyword,
            '출현_횟수': len(keyword_df),
            '평균_좋아요': round(keyword_df['좋아요'].mean(), 2),
            '최대_좋아요': keyword_df['좋아요'].max(),
            '총_좋아요': keyword_df['좋아요'].sum(),
            '평균_댓글_길이': round(keyword_df['댓글_길이'].mean(), 2)
        })

keyword_df_stats = pd.DataFrame(keyword_stats)
output_keywords = os.path.join(OUTPUT_DIR, "youtube_keywords_tableau.csv")
keyword_df_stats.to_csv(output_keywords, index=False, encoding='utf-8-sig')
print(f"✅ '{output_keywords}' 저장 완료!")

# 좋아요 구간별 통계
likes_stats = df.groupby('좋아요_구간').agg({
    '댓글': 'count',
    '좋아요': ['sum', 'mean', 'max'],
    '댓글_길이': 'mean',
    '단어_수': 'mean'
}).reset_index()

likes_stats.columns = ['좋아요_구간', '댓글_수', '총_좋아요', '평균_좋아요', 
                       '최대_좋아요', '평균_댓글_길이', '평균_단어_수']
likes_stats = likes_stats.round(2)

output_likes = os.path.join(OUTPUT_DIR, "youtube_likes_stats_tableau.csv")
likes_stats.to_csv(output_likes, index=False, encoding='utf-8-sig')
print(f"✅ '{output_likes}' 저장 완료!")

# 감성 분석 통계
sentiment_stats = df.groupby('감성').agg({
    '댓글': 'count',
    '좋아요': ['sum', 'mean'],
    '댓글_길이': 'mean'
}).reset_index()

sentiment_stats.columns = ['감성', '댓글_수', '총_좋아요', '평균_좋아요', '평균_댓글_길이']
sentiment_stats = sentiment_stats.round(2)

output_sentiment = os.path.join(OUTPUT_DIR, "youtube_sentiment_tableau.csv")
sentiment_stats.to_csv(output_sentiment, index=False, encoding='utf-8-sig')
print(f"✅ '{output_sentiment}' 저장 완료!")

# ===========================================
# 6. 요약 정보 출력
# ===========================================
print("\n" + "="*50)
print("📊 데이터 요약")
print("="*50)
print(f"총 댓글 수: {len(df):,}개")
print(f"총 좋아요: {df['좋아요'].sum():,}개")
print(f"평균 좋아요: {df['좋아요'].mean():.2f}개")
print(f"평균 댓글 길이: {df['댓글_길이'].mean():.1f}자")
print(f"평균 단어 수: {df['단어_수'].mean():.1f}개")

print("\n📈 좋아요 구간별 분포:")
print(likes_stats[['좋아요_구간', '댓글_수', '평균_좋아요']].to_string(index=False))

print("\n💭 감성 분포:")
print(sentiment_stats[['감성', '댓글_수', '평균_좋아요']].to_string(index=False))

print("\n🔑 상위 5개 키워드:")
print(keyword_df_stats.head(5)[['키워드', '출현_횟수', '평균_좋아요']].to_string(index=False))

print("\n" + "="*50)
print("✨ 태블로에서 열 파일들:")
print("="*50)
print(f"1. {output_main} - 메인 데이터 (전체 댓글)")
print(f"2. {output_keywords} - 키워드별 통계")
print(f"3. {output_likes} - 좋아요 구간별 통계")
print(f"4. {output_sentiment} - 감성 분석 통계")
print("="*50)