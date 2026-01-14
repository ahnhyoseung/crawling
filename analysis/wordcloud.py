import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False
# CSV 로드
df = pd.read_csv("data/naver_comments_20260108_104841.csv")

print("전체 댓글 수:", len(df))

# 좋아요 상위 N개
TOP_N = 50
df_top = df.sort_values("좋아요수", ascending=False).head(TOP_N)

# 텍스트 전처리
words = []
stopwords = {
    "the", "is", "to", "and",
    "이거", "그냥", "진짜", "정말",
    "너무", "사람", "영상", "것", "수"
}

for text in df_top["댓글"]:
    tokens = str(text).replace("\n", " ").split()
    words.extend(tokens)

words = [w for w in words if len(w) > 1 and w not in stopwords]
text = " ".join(words)

# 워드클라우드
wc = WordCloud(
    font_path="C:/Windows/Fonts/malgun.ttf",
    background_color="white",
    width=800,
    height=400
).generate(text)

plt.figure(figsize=(12,6))
plt.imshow(wc)
plt.axis("off")
plt.title("🔥좋아요 상위 댓글 워드클라우드")
plt.show()
