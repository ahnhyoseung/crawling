import pandas as pd
from pathlib import Path
import re


def analyze_sentiment(text):
    """간단한 규칙 기반 감성 분석"""
    if pd.isna(text):
        return "중립"

    text = str(text).lower()

    # 감성 키워드 사전
    positive_words = [
        "좋", "최고", "감사", "훌륭", "멋지", "대단", "완벽", "행복",
        "사랑", "예쁘", "아름답", "멋있", "신기", "재밌", "재미있",
        "흥미", "유익", "도움", "응원", "화이팅", "ㅎㅎ", "ㅋㅋ",
        "굿", "good", "great", "nice", "awesome", "amazing"
    ]

    negative_words = [
        "나쁘", "최악", "싫", "짜증", "화", "분노", "미워", "슬프",
        "우울", "지루", "별로", "실망", "후회", "무서", "걱정", "불안",
        "아쉽", "안타까", "ㅠㅠ", "ㅜㅜ", "하", "에휴",
        "bad", "terrible", "worst", "hate", "angry"
    ]

    # 부정 표현 체크
    negation_words = ["안", "못", "없", "말"]
    has_negation = any(neg in text for neg in negation_words)

    # 긍정/부정 단어 카운트
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)

    # 부정 표현이 있으면 감정 반전
    if has_negation:
        pos_count, neg_count = neg_count, pos_count

    # 감성 판단
    if pos_count > neg_count:
        return "긍정"
    elif neg_count > pos_count:
        return "부정"
    else:
        return "중립"


def sentiment_analysis_main():
    """감성 분석 메인 함수"""
    print("=" * 60)
    print("감성 분석 시작")
    print("=" * 60)

    # CSV 파일 읽기
    naver_path = Path("../data/naver_comments_20260102_121759.csv")
    youtube_path = Path("../data/utube_comments_20260102_121947.csv")

    results = []

    # 네이버 댓글 분석
    if naver_path.exists():
        print("\n📊 네이버 댓글 분석 중...")
        df_naver = pd.read_csv(naver_path)

        # 댓글 컬럼 찾기
        text_col = None
        for col in ['댓글', 'comment', 'content', 'text']:
            if col in df_naver.columns:
                text_col = col
                break

        if text_col:
            df_naver['감성'] = df_naver[text_col].apply(analyze_sentiment)
            df_naver['플랫폼'] = 'naver'

            sentiment_counts = df_naver['감성'].value_counts()
            print(f"   긍정: {sentiment_counts.get('긍정', 0)}개")
            print(f"   부정: {sentiment_counts.get('부정', 0)}개")
            print(f"   중립: {sentiment_counts.get('중립', 0)}개")

            results.append(df_naver[[text_col, '감성', '플랫폼']])

    # 유튜브 댓글 분석
    if youtube_path.exists():
        print("\n📊 유튜브 댓글 분석 중...")
        df_youtube = pd.read_csv(youtube_path)

        # 댓글 컬럼 찾기
        text_col = None
        for col in ['댓글', 'comment', 'content', 'text']:
            if col in df_youtube.columns:
                text_col = col
                break

        if text_col:
            df_youtube['감성'] = df_youtube[text_col].apply(analyze_sentiment)
            df_youtube['플랫폼'] = 'youtube'

            sentiment_counts = df_youtube['감성'].value_counts()
            print(f"   긍정: {sentiment_counts.get('긍정', 0)}개")
            print(f"   부정: {sentiment_counts.get('부정', 0)}개")
            print(f"   중립: {sentiment_counts.get('중립', 0)}개")

            results.append(df_youtube[[text_col, '감성', '플랫폼']])

    # 통합 결과 저장
    if results:
        final_df = pd.concat(results, ignore_index=True)

        # 저장
        output_dir = Path("../data/processed")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / "sentiment_analysis.csv"
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print("\n" + "=" * 60)
        print("✓ 감성 분석 완료!")
        print("=" * 60)
        print(f"파일 저장: {output_path}")

        # 전체 통계
        print("\n📈 전체 통계:")
        total_counts = final_df['감성'].value_counts()
        total = len(final_df)
        for sentiment, count in total_counts.items():
            percentage = (count / total) * 100
            print(f"   {sentiment}: {count}개 ({percentage:.1f}%)")

        # 플랫폼별 통계
        print("\n📊 플랫폼별 통계:")
        platform_sentiment = final_df.groupby(['플랫폼', '감성']).size().unstack(fill_value=0)
        print(platform_sentiment)

        return final_df
    else:
        print("⚠️  분석할 데이터가 없습니다.")
        return None


if __name__ == "__main__":
    sentiment_analysis_main()