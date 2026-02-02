import requests
import pandas as pd
from datetime import datetime
import time
import os
import re
import json

def get_naver_comments(article_url, max_comments=1000):
    """네이버 뉴스 댓글 수집 (댓글, 공감수만)"""
    
    # URL에서 oid, aid 추출
    match = re.search(r'/article/(\d+)/(\d+)', article_url)
    if not match:
        print("❌ 올바른 네이버 뉴스 URL이 아닙니다.")
        return None
    
    oid = match.group(1)
    aid = match.group(2)
    
    print(f"📰 기사 정보: oid={oid}, aid={aid}")
    
    comments = []
    seen_contents = set()  # 중복 체크용
    page = 1
    no_new_comments = 0  # 새 댓글 없는 횟수
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': article_url
    }
    
    while len(comments) < max_comments:
        api_url = "https://apis.naver.com/commentBox/cbox/web_neo_list_jsonp.json"
        
        params = {
            'ticket': 'news',
            'templateId': 'default_society',
            'pool': 'cbox5',
            'lang': 'ko',
            'country': 'KR',
            'objectId': f'news{oid},{aid}',
            'categoryId': '',
            'pageSize': '100',
            'indexSize': '10',
            'groupId': '',
            'listType': 'OBJECT',
            'pageType': 'more',
            'page': str(page),
            'currentPage': str(page),
            'refresh': 'false',
            'sort': 'FAVORITE'
        }
        
        try:
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"⚠️  페이지 {page} 요청 실패: {response.status_code}")
                break
            
            # JSONP → JSON 변환
            text = response.text
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print("⚠️  JSON 파싱 실패")
                break
            
            data = json.loads(text[json_start:json_end])
            comment_list = data.get('result', {}).get('commentList', [])
            
            if not comment_list:
                print(f"✅ 페이지 {page}에 더 이상 댓글 없음")
                break
            
            # 새로운 댓글 수 카운트
            new_count = 0
            
            # 댓글과 공감수만 저장 (중복 제거)
            for comment in comment_list:
                content = comment.get('contents', '')
                likes = comment.get('sympathyCount', 0)
                
                # 중복 체크 (댓글 내용 기준)
                if content not in seen_contents:
                    seen_contents.add(content)
                    comments.append({
                        '댓글': content,
                        '공감수': likes
                    })
                    new_count += 1
            
            print(f"📄 페이지 {page}: 새로운 댓글 {new_count}개 (총 {len(comments)}개)")
            
            # 새로운 댓글이 없으면 카운트 증가
            if new_count == 0:
                no_new_comments += 1
                if no_new_comments >= 2:  # 2번 연속 새 댓글 없으면 종료
                    print("✅ 모든 댓글 수집 완료")
                    break
            else:
                no_new_comments = 0
            
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ 에러 발생: {e}")
            break
    
    return pd.DataFrame(comments)


# 실행
if __name__ == "__main__":
    article_url = input('📰링크를 입력해주세요:')
    
    df = get_naver_comments(article_url, max_comments=500)
    
    if df is not None and len(df) > 0:
        print("\n=== 수집 결과 ===")
        print(df.head(10))
        print(f"\n총 댓글: {len(df)}개")
        print(f"총 공감수: {df['공감수'].sum()}")
        print(f"평균 공감수: {df['공감수'].mean():.1f}")
        
        # 저장
        os.makedirs("data/naver", exist_ok=True)
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/naver/naver_comments_{now}.csv"
        
        df.to_csv(filename, index=False, encoding="utf-8-sig")
        print(f"\n✅ 저장 완료: {filename}")
    else:
        print("\n❌ 댓글 수집 실패")