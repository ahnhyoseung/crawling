from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

url = "https://n.news.naver.com/mnews/article/comment/421/0008691259"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(url)
time.sleep(3)

# 더보기 눌러서 계속 확장
while True:
    try:
        more_btn = driver.find_element(By.CSS_SELECTOR, "a.u_cbox_btn_more")
        more_btn.click()
        time.sleep(1)
    except:
        break

comments = []

# 댓글 리스트 가져오기
comment_boxes = driver.find_elements(By.CSS_SELECTOR, "li.u_cbox_comment")

for box in comment_boxes:
    # 댓글 내용
    try:
        content = box.find_element(By.CSS_SELECTOR, "span.u_cbox_contents").text
    except:
        content = ""

    # 공감수
    try:
        like = box.find_element(By.CSS_SELECTOR, "em.u_cbox_cnt_recomm").text
    except:
        like = "0"

    # 비공감수
    try:
        dislike = box.find_element(By.CSS_SELECTOR, "em.u_cbox_cnt_unrecomm").text
    except:
        dislike = "0"

    comments.append({
        "댓글": content,
        "공감수": int(like.replace(",", "")) if like else 0,
        "비공감수": int(dislike.replace(",", "")) if dislike else 0
    })

driver.quit()

df = pd.DataFrame(comments)
print(df.head())
print("총 댓글 수:", len(df))

from datetime import datetime

now = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"data/naver_comments_{now}.csv"

df.to_csv(
    filename,
    index=False,
    encoding="utf-8-sig"
)

print(f"저장 완료: {filename}")