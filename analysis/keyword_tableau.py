import pandas as pd
from collections import Counter
import re
from pathlib import Path


def extract_keywords(csv_path, platform, text_col=None):
    """CSV 파일에서 키워드를 추출하고 빈도를 계산"""

    # 파일 존재 확인
    if not Path(csv_path).exists():
        print(f"⚠️  파일을 찾을 수 없습니다: {csv_path}")
        return pd.DataFrame(columns=["keyword", "count", "platform"])

    try:
        df = pd.read_csv(csv_path)
        print(f"\n📊 {platform} 파일 정보:")
        print(f"   컬럼: {df.columns.tolist()}")
        print(f"   행 수: {len(df)}")

        # 텍스트 컬럼 자동 감지
        if text_col is None:
            possible_cols = ['댓글', 'comment', 'content', 'text', '내용']
            text_col = None

            for col in possible_cols:
                if col in df.columns:
                    text_col = col
                    break

            if text_col is None:
                # 첫 번째 컬럼을 사용
                text_col = df.columns[0]
                print(f"   ⚠️  텍스트 컬럼을 찾지 못해 '{text_col}' 사용")

        print(f"   사용 컬럼: '{text_col}'")

    except Exception as e:
        print(f"⚠️  CSV 읽기 오류: {e}")
        return pd.DataFrame(columns=["keyword", "count", "platform"])

    # 확장된 불용어 리스트
    stopwords = {
        # 기존
        "이거", "그냥", "진짜", "정말", "너무",
        "사람", "영상", "뉴스", "기사", "댓글",
        "것", "수",
        # 추가
        "이게", "저게", "요거", "그거", "이건", "저건",
        "있다", "없다", "하다", "되다", "이다", "아니다",
        "그리고", "그런데", "하지만", "그래서", "왜냐하면",
        "이렇게", "저렇게", "어떻게", "뭔가", "약간",
        "좀", "더", "안", "못", "다", "또", "및", "등",
        "있는", "없는", "하는", "되는", "이런", "저런",
        "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅜㅜ"
    }

    words = []

    for text in df[text_col]:
        # NaN 처리
        if pd.isna(text):
            continue

        text = str(text)

        # 특수문자 제거 (한글, 영문, 숫자만 남김)
        text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)

        # 공백 기준 분리
        tokens = text.split()

        # 필터링: 길이 2 이상, 불용어 제외, 숫자만 있는 단어 제외
        filtered = [
            w for w in tokens
            if len(w) > 1
               and w not in stopwords
               and not w.isdigit()
        ]

        words.extend(filtered)

    # 빈도 계산
    counter = Counter(words)

    # 상위 100개만 추출 (옵션)
    top_keywords = counter.most_common(100)

    # 데이터프레임 생성
    result = pd.DataFrame(top_keywords, columns=["keyword", "count"])
    result["platform"] = platform

    print(f"   ✓ {len(result)}개 키워드 추출 완료\n")

    return result


if __name__ == "__main__":
    print("=" * 60)
    print("키워드 추출 시작")
    print("=" * 60)

    # 키워드 추출 (analysis 폴더에서 한 단계 위로 올라가서 data 폴더 접근)
    naver_df = extract_keywords(
        "../data/naver_comments_20260102_121759.csv",
        "naver"
    )

    youtube_df = extract_keywords(
        "../data/utube_comments_20260102_121947.csv",
        "youtube"
    )

    # 통합
    final_df = pd.concat([naver_df, youtube_df], ignore_index=True)

    # processed 폴더 생성 (없으면)
    output_dir = Path("../data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 저장
    output_path = output_dir / "keyword_for_tableau.csv"
    final_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("=" * 60)
    print("✓ 완료!")
    print("=" * 60)
    print(f"파일 저장: {output_path}")
    print(f"전체 키워드 수: {len(final_df)}")
    print(f"  - 네이버: {len(naver_df)}개")
    print(f"  - 유튜브: {len(youtube_df)}개")

    if len(final_df) > 0:
        print(f"\n상위 10개 키워드:")
        print(final_df.nlargest(10, 'count')[['keyword', 'count', 'platform']])
