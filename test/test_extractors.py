# test/test_extractors.py

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from utils.fetcher import fetch_html
from utils.translator import translate_to_korean
from utils.keywords import extract_keywords
from extractors.soup_extractor import SoupExtractor
from extractors.readability import ReadabilityExtractor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [test_extractors.py] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def test_extractors(url: str):
    logging.info(f"🔍 테스트 시작: {url}")

    try:
        html = fetch_html(url)
        logging.info("✅ HTML 가져오기 완료")
    except Exception as e:
        logging.error(f"❌ HTML 가져오기 실패: {e}")
        return

    # SoupExtractor 테스트
    try:
        soup_extractor = SoupExtractor(html)
        soup_title = soup_extractor.get_title()
        soup_text = soup_extractor.get_text()
        soup_image = soup_extractor.get_image()
        soup_translated = translate_to_korean(soup_text)
        soup_keywords = extract_keywords(soup_text)
        logging.info("✅ SoupExtractor 실행 완료")
    except Exception as e:
        logging.error(f"❌ SoupExtractor 오류: {e}")
        soup_title = soup_text = soup_image = soup_translated = "ERROR"
        soup_keywords = []

    # ReadabilityExtractor 테스트
    try:
        read_extractor = ReadabilityExtractor(html)
        read_title = read_extractor.get_title()
        read_text = read_extractor.get_text()
        read_image = read_extractor.get_image()
        read_translated = translate_to_korean(read_text)
        read_keywords = extract_keywords(read_text)
        logging.info("✅ ReadabilityExtractor 실행 완료")
    except Exception as e:
        logging.error(f"❌ ReadabilityExtractor 오류: {e}")
        read_title = read_text = read_image = read_translated = "ERROR"
        read_keywords = []

    # 결과 비교 출력
    print("\n========== 결과 비교 ==========")
    print(f"[URL] {url}\n")

    print("[SoupExtractor]")
    print(f"제목: {soup_title}")
    print(f"이미지: {soup_image}")
    print(f"본문 미리보기:\n{soup_text[:300]}...\n")
    print(f"번역문 미리보기:\n{soup_translated[:300]}...\n")
    print(f"키워드 미리보기: {soup_keywords}\n")

    print("[ReadabilityExtractor]")
    print(f"제목: {read_title}")
    print(f"이미지: {read_image}")
    print(f"본문 미리보기:\n{read_text[:300]}...")
    print(f"번역문 미리보기:\n{read_translated[:300]}...")
    print(f"키워드 미리보기: {read_keywords}")
    print("================================\n")


if __name__ == "__main__":
    urls = [
        "https://example.com",
        "https://www.bbc.com/sport/articles/cglxwrj2501o",
        "https://blog.naver.com/PostView.naver?blogId=ronalee&logNo=223856131195&redirect=Dlog&widgetTypeCall=true&from=section&topReferer=https%3A%2F%2Fsection.blog.naver.com%2FBlogHome.naver%3FdirectoryNo%3D0%26currentPage%3D1%26groupId%3D0&trackingCode=blog_sectionhome_pc&directAccess=false"
    ]

    for url in urls:
        test_extractors(url)