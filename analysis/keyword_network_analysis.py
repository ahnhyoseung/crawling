import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter
from itertools import combinations
import re
from pathlib import Path

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False


def extract_keyword_pairs(text, stopwords, min_length=2):
    """텍스트에서 키워드 쌍 추출"""
    if pd.isna(text):
        return []

    text = str(text)

    # 특수문자 제거
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)

    # 토큰화
    tokens = text.split()

    # 필터링
    keywords = [
        w for w in tokens
        if len(w) >= min_length
           and w not in stopwords
           and not w.isdigit()
    ]

    # 중복 제거하면서 순서 유지
    seen = set()
    unique_keywords = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique_keywords.append(k)

    # 키워드 쌍 생성 (같은 댓글 내에서 함께 등장)
    if len(unique_keywords) >= 2:
        return list(combinations(unique_keywords, 2))
    return []


def create_network_graph(pairs, top_n=30, min_weight=2):
    """네트워크 그래프 생성"""
    # 쌍의 빈도 계산
    pair_counts = Counter(pairs)

    # 최소 빈도 필터링
    filtered_pairs = {pair: count for pair, count in pair_counts.items() if count >= min_weight}

    if not filtered_pairs:
        print("⚠️  네트워크를 만들 수 있는 키워드 쌍이 충분하지 않습니다.")
        return None

    # 그래프 생성
    G = nx.Graph()

    for (word1, word2), weight in filtered_pairs.items():
        G.add_edge(word1, word2, weight=weight)

    # 연결성이 높은 노드만 선택
    if len(G.nodes()) > top_n:
        # 차수(degree)가 높은 노드 선택
        degrees = dict(G.degree())
        top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
        top_node_names = [node for node, _ in top_nodes]
        G = G.subgraph(top_node_names).copy()

    return G


def visualize_network(G, platform_name, output_path):
    """네트워크 시각화"""
    if G is None or len(G.nodes()) == 0:
        print(f"⚠️  {platform_name}: 시각화할 네트워크가 없습니다.")
        return

    plt.figure(figsize=(16, 12))

    # 레이아웃 설정
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

    # 노드 크기 (연결 수에 비례)
    degrees = dict(G.degree())
    node_sizes = [degrees[node] * 300 for node in G.nodes()]

    # 엣지 두께 (가중치에 비례)
    edges = G.edges()
    weights = [G[u][v]['weight'] for u, v in edges]
    max_weight = max(weights) if weights else 1
    edge_widths = [w / max_weight * 5 for w in weights]

    # 노드 그리기
    nx.draw_networkx_nodes(
        G, pos,
        node_size=node_sizes,
        node_color='lightblue',
        alpha=0.7,
        edgecolors='navy',
        linewidths=2
    )

    # 엣지 그리기
    nx.draw_networkx_edges(
        G, pos,
        width=edge_widths,
        alpha=0.3,
        edge_color='gray'
    )

    # 라벨 그리기
    nx.draw_networkx_labels(
        G, pos,
        font_size=10,
        font_family='Malgun Gothic',
        font_weight='bold'
    )

    plt.title(f'{platform_name} 키워드 네트워크\n(함께 등장하는 키워드)',
              fontsize=16, fontweight='bold', pad=20)
    plt.axis('off')
    plt.tight_layout()

    # 저장
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   ✓ 네트워크 그래프 저장: {output_path}")
    plt.close()


def analyze_network_statistics(G, platform_name):
    """네트워크 통계 분석"""
    if G is None or len(G.nodes()) == 0:
        return

    print(f"\n📊 {platform_name} 네트워크 통계:")
    print(f"   노드 수: {G.number_of_nodes()}개")
    print(f"   엣지 수: {G.number_of_edges()}개")

    # 중심성이 높은 키워드 (가장 많이 연결된)
    degrees = dict(G.degree())
    top_central = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:5]

    print(f"\n   🔗 가장 많이 연결된 키워드:")
    for word, degree in top_central:
        print(f"      {word}: {degree}개 연결")

    # 가중치가 높은 연결 (자주 함께 등장)
    edges_with_weights = [(u, v, G[u][v]['weight']) for u, v in G.edges()]
    top_pairs = sorted(edges_with_weights, key=lambda x: x[2], reverse=True)[:5]

    print(f"\n   💬 자주 함께 등장하는 키워드 쌍:")
    for word1, word2, weight in top_pairs:
        print(f"      {word1} ↔ {word2}: {weight}회")


def keyword_network_main():
    """키워드 네트워크 분석 메인 함수"""
    print("=" * 60)
    print("키워드 네트워크 분석 시작")
    print("=" * 60)

    # 불용어 설정
    stopwords = {
        "이거", "그냥", "진짜", "정말", "너무",
        "사람", "영상", "뉴스", "기사", "댓글",
        "것", "수", "이게", "저게", "요거", "그거",
        "이건", "저건", "있다", "없다", "하다", "되다",
        "이다", "아니다", "그리고", "그런데", "하지만",
        "그래서", "왜냐하면", "이렇게", "저렇게", "어떻게",
        "뭔가", "약간", "좀", "더", "안", "못", "다",
        "또", "및", "등", "있는", "없는", "하는", "되는",
        "이런", "저런", "ㅋㅋ", "ㅎㅎ", "ㅠㅠ", "ㅜㅜ"
    }

    # 출력 디렉토리
    output_dir = Path("../data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 네이버 댓글 분석
    naver_path = Path("../data/naver_comments_20260102_121759.csv")
    if naver_path.exists():
        print("\n🔍 네이버 댓글 분석 중...")
        df_naver = pd.read_csv(naver_path)

        # 댓글 컬럼 찾기
        text_col = None
        for col in ['댓글', 'comment', 'content', 'text']:
            if col in df_naver.columns:
                text_col = col
                break

        if text_col:
            # 키워드 쌍 추출
            all_pairs = []
            for text in df_naver[text_col]:
                pairs = extract_keyword_pairs(text, stopwords)
                all_pairs.extend(pairs)

            print(f"   추출된 키워드 쌍: {len(all_pairs)}개")

            # 네트워크 생성 및 시각화
            G_naver = create_network_graph(all_pairs, top_n=30, min_weight=2)
            if G_naver:
                visualize_network(
                    G_naver,
                    "네이버",
                    output_dir / "network_naver.png"
                )
                analyze_network_statistics(G_naver, "네이버")

                # 네트워크 데이터 저장
                edge_data = [(u, v, G_naver[u][v]['weight'])
                             for u, v in G_naver.edges()]
                edge_df = pd.DataFrame(edge_data,
                                       columns=['keyword1', 'keyword2', 'weight'])
                edge_df['platform'] = 'naver'
                edge_df.to_csv(
                    output_dir / "network_edges_naver.csv",
                    index=False,
                    encoding='utf-8-sig'
                )

    # 유튜브 댓글 분석
    youtube_path = Path("../data/utube_comments_20260102_121947.csv")
    if youtube_path.exists():
        print("\n🔍 유튜브 댓글 분석 중...")
        df_youtube = pd.read_csv(youtube_path)

        # 댓글 컬럼 찾기
        text_col = None
        for col in ['댓글', 'comment', 'content', 'text']:
            if col in df_youtube.columns:
                text_col = col
                break

        if text_col:
            # 키워드 쌍 추출
            all_pairs = []
            for text in df_youtube[text_col]:
                pairs = extract_keyword_pairs(text, stopwords)
                all_pairs.extend(pairs)

            print(f"   추출된 키워드 쌍: {len(all_pairs)}개")

            # 네트워크 생성 및 시각화
            G_youtube = create_network_graph(all_pairs, top_n=30, min_weight=2)
            if G_youtube:
                visualize_network(
                    G_youtube,
                    "유튜브",
                    output_dir / "network_youtube.png"
                )
                analyze_network_statistics(G_youtube, "유튜브")

                # 네트워크 데이터 저장
                edge_data = [(u, v, G_youtube[u][v]['weight'])
                             for u, v in G_youtube.edges()]
                edge_df = pd.DataFrame(edge_data,
                                       columns=['keyword1', 'keyword2', 'weight'])
                edge_df['platform'] = 'youtube'
                edge_df.to_csv(
                    output_dir / "network_edges_youtube.csv",
                    index=False,
                    encoding='utf-8-sig'
                )

    print("\n" + "=" * 60)
    print("✓ 키워드 네트워크 분석 완료!")
    print("=" * 60)
    print(f"결과 저장 위치: {output_dir}")


if __name__ == "__main__":
    keyword_network_main()