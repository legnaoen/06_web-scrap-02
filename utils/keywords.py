# utils/keywords.py

import logging
from konlpy.tag import Okt

# 로깅 설정
logger = logging.getLogger(__name__)

# 불용어 불러오기
def load_stopwords(path="utils/stopwords_ko.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return set(word.strip() for word in f.readlines() if word.strip())
    except Exception as e:
        logger.warning(f"[keywords.py] ❌ 불용어 파일 로드 실패: {e}")
        return set()

# 키워드 추출 함수 (한글 텍스트 기반)
def extract_keywords(text, top_k=15):
    logger.info("[keywords.py] 키워드 추출 시작")

    stopwords = load_stopwords()
    okt = Okt()

    # 형태소 분석으로 명사 추출
    nouns = okt.nouns(text)

    # 불용어 제거 및 2자 이상만 사용
    filtered = [word for word in nouns if word not in stopwords and len(word) > 1]

    # 빈도수 계산
    freq = {}
    for word in filtered:
        freq[word] = freq.get(word, 0) + 1

    # 상위 키워드 선택
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_keywords[:top_k]]

    logger.info(f"[keywords.py] 키워드 추출 완료: {keywords}")
    return keywords