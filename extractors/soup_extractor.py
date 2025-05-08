# 파일 위치: extractors/soup_extractor.py

import logging
from bs4 import BeautifulSoup, NavigableString
from extractors.base_extractor import BaseExtractor
import trafilatura
from readability import Document
from urllib.parse import urljoin

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [soup_extractor.py] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class SoupExtractor(BaseExtractor):
    """
    trafilatura → readability fallback 방식의 본문 추출기
    """

    def __init__(self, html: str, base_url: str = ""):
        super().__init__(html)
        self.html = html
        self.soup = BeautifulSoup(html, "lxml")
        self.base_url = base_url
        self.trafilatura_result = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False,
            include_formatting=True
        )
        logging.info("SoupExtractor 초기화 완료")

    def get_title(self) -> str:
        if self.soup.title:
            title = self.soup.title.get_text(strip=True)
            logging.info(f"제목 추출 완료: {title}")
            return title

        try:
            doc = Document(self.html)
            title = doc.title()
            logging.info(f"[Fallback] 제목 추출 완료 (readability): {title}")
            return title
        except Exception as e:
            logging.warning(f"제목 추출 실패: {e}")
            return ""

    def get_text(self) -> str:
        if self.trafilatura_result and len(self.trafilatura_result) > 100:
            logging.info(f"본문 추출 성공 (trafilatura, 길이: {len(self.trafilatura_result)}자)")
            return self.trafilatura_result

        try:
            doc = Document(self.html)
            content_html = doc.summary()
            content_soup = BeautifulSoup(content_html, "lxml")
            text = content_soup.get_text(separator="\n", strip=True)
            logging.warning("본문 추출 fallback 사용 (readability)")
            return text
        except Exception as e:
            logging.error(f"본문 추출 실패: {e}")
            return ""

    def get_text_with_images(self) -> str:
        try:
            doc = Document(self.html)
            content_html = doc.summary()
            content_soup = BeautifulSoup(content_html, "lxml")

            output_parts = []

            for tag in content_soup.find_all(["p", "img", "h1", "h2", "h3", "ul", "ol", "li", "blockquote"]):
                if tag.name == "p":
                    para = tag.get_text(" ", strip=True)
                    imgs = tag.find_all("img")
                    for img in imgs:
                        src = img.get("src")
                        if src:
                            full_url = urljoin(self.base_url, src)
                            para += f"\n\n![image]({full_url})"
                    if para:
                        output_parts.append(para)

                elif tag.name == "img":
                    src = tag.get("src")
                    if src:
                        full_url = urljoin(self.base_url, src)
                        output_parts.append(f"![image]({full_url})")

                elif tag.name in ["h1", "h2", "h3"]:
                    level = int(tag.name[1])
                    text = tag.get_text(" ", strip=True)
                    output_parts.append(f"{'#' * level} {text}")

                elif tag.name == "li":
                    output_parts.append(f"- {tag.get_text(' ', strip=True)}")

                elif tag.name == "blockquote":
                    block = tag.get_text(" ", strip=True)
                    output_parts.append(f"> {block}")

            result = "\n\n".join(output_parts)
            logging.info("본문+이미지 추출 성공 (readability 기반)")
            return result

        except Exception as e:
            logging.error(f"본문+이미지 추출 실패: {e}")
            return self.get_text()

    def get_image(self) -> str:
        og_image = self.soup.find("meta", property="og:image")
        if og_image and og_image.get("content"):
            url = urljoin(self.base_url, og_image["content"])
            logging.info(f"대표 이미지 추출 성공: og:image → {url}")
            return url

        first_img = self.soup.find("img")
        if first_img and first_img.get("src"):
            url = urljoin(self.base_url, first_img["src"])
            logging.info(f"대표 이미지 추출 성공: <img> 태그 → {url}")
            return url

        all_images = self.get_images()
        if all_images:
            logging.info(f"대표 이미지 fallback 사용 → {all_images[0]}")
            return all_images[0]

        logging.warning("대표 이미지 없음")
        return ""

    def get_images(self) -> list:
        image_urls = []
        img_tags = self.soup.find_all("img")
        logging.info(f"총 <img> 태그 수: {len(img_tags)}")

        for img in img_tags:
            src = img.get("src")
            if src:
                full_url = urljoin(self.base_url, src)
                image_urls.append(full_url)
                logging.info(f"📸 본문 이미지 포착: {full_url}")

        if image_urls:
            logging.info(f"본문 이미지 총 {len(image_urls)}개 추출 완료")
        else:
            logging.warning("⚠️ 본문에서 이미지가 포착되지 않았습니다.")

        return image_urls