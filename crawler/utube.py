from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

url = "https://www.youtube.com/watch?v=xPwSffZnllQ"

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(url)
time.sleep(6)

# 🔥 핵심 1: body에 PAGE_DOWN 보내기
body = driver.find_element(By.TAG_NAME, "body")

for _ in range(50):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(1.5)

# 🔥 핵심 2: 댓글 DOM 생성 대기
time.sleep(3)

comments = []

comment_boxes = driver.find_elements(
    By.CSS_SELECTOR, "ytd-comment-thread-renderer"
)

print("댓글 박스 개수:", len(comment_boxes))  # 디버그용

for box in comment_boxes:
    try:
        content = box.find_element(By.ID, "content-text").text
    except:
        continue

    try:
        like = box.find_element(By.ID, "vote-count-middle").text.strip()
        if like == "":
            like = 0
        elif "천" in like:
            like = int(float(like.replace("천", "")) * 1000)
        else:
            like = int(like.replace(",", ""))
    except:
        like = 0

    comments.append({
        "댓글": content,
        "좋아요수": like
    })

driver.quit()

df = pd.DataFrame(comments)
print(df.head())
print("총 댓글 수:", len(df))

from datetime import datetime

now = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"data/utube_comments_{now}.csv"

df.to_csv(
    filename,
    index=False,
    encoding="utf-8-sig"
)

print(f"저장 완료: {filename}")