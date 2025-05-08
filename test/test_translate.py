# 파일 위치: test/test_translate.py

import logging
import sys
sys.path.append('.')  # 루트 경로에 접근 가능하게 설정

from utils.translator import translate_to_korean

# 로그 설정
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

if __name__ == '__main__':
    sample_texts = [
        "This domain is for use in illustrative examples in documents.",
        "Artificial Intelligence is transforming the world.",
        "오늘 날씨가 참 좋네요.",  # 한글 → 번역되지 않음 (테스트용)
    ]

    for i, text in enumerate(sample_texts, 1):
        print(f"\n🔸 Sample {i}: 원문\n{text}")
        translated = translate_to_korean(text)
        print(f"✅ 번역 결과:\n{translated}")