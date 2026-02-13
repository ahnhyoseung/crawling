import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# 저장 폴더 생성
OUTPUT_DIR = "anal_data/word_c"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# CSV 로드
df = pd.read_csv("C:/Users/User/crawll/crawling/crawler/data/utube/youtube_comments_20260105_095113.csv")

print("전체 댓글 수:", len(df))

# 좋아요 상위 N개
TOP_N = 50
df_top = df.sort_values("좋아요", ascending=False).head(TOP_N)

# 텍스트 전처리
words = []
stopwords = {
    "the", "is", "to", "and",
    "이거", "그냥", "진짜", "정말",
    "너무", "사람", "영상", "것", "수", "br"
}

for text in df_top["댓글"]:
    tokens = str(text).replace("\n", " ").split()
    words.extend(tokens)

words = [w for w in words if len(w) > 1 and w not in stopwords]
text = " ".join(words)

# 워드클라우드 생성
wc = WordCloud(
    font_path="C:/Windows/Fonts/malgun.ttf",
    background_color="white",
    width=800,
    height=400
).generate(text)

# 시각화
plt.figure(figsize=(12,6))
plt.imshow(wc)
plt.axis("off")
plt.title("🔥 유튜브 좋아요 상위 댓글 워드클라우드")

# 파일 저장
output_path = os.path.join(OUTPUT_DIR, "wordcloud_top50.png")
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"✅ 워드클라우드 저장 완료: {output_path}")

# 화면에 표시
plt.show()
