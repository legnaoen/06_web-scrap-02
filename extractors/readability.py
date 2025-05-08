# extractors/readability.py

import logging
from bs4 import BeautifulSoup
from readability import Document
from extractors.base_extractor import BaseExtractor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [readability.py] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class ReadabilityExtractor(BaseExtractor):
    """
    readability-lxml 기반 추출기
    HTML을 정제하고 주요 콘텐츠 및 제목을 추출
    """

    def __init__(self, html: str):
        super().__init__(html)
        self.doc = Document(html)
        self.summary_html = self.doc.summary()
        self.soup = BeautifulSoup(self.summary_html, "lxml")
        self.meta_soup = BeautifulSoup(html, "lxml")
        logging.info("ReadabilityExtractor 초기화 완료")

    def get_title(self) -> str:
        title = self.doc.short_title()
        logging.info(f"제목 추출 완료: {title}")
        return title

    def get_text(self) -> str:
        text = self.soup.get_text(separator="\n", strip=True)
        logging.info(f"본문 추출 완료 (길이: {len(text)}자)")
        return text

    def get_image(self) -> str:
        """
        대표 이미지 추출: og:image 우선, 없으면 첫 번째 img
        """
        og_image = self.meta_soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            logging.info("대표 이미지 추출 성공: og:image")
            return og_image["content"]

        first_img = self.soup.find("img")
        if first_img and first_img.get("src"):
            logging.info("대표 이미지 추출 성공: 첫 번째 <img>")
            return first_img["src"]

        logging.warning("대표 이미지 없음")
        return ""