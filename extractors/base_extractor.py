# extractors/base_extractor.py

import logging
from abc import ABC, abstractmethod

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [base_extractor.py] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class BaseExtractor(ABC):
    """
    모든 콘텐츠 추출기의 기본 인터페이스.
    모든 구현체는 get_title, get_text, get_image 메서드를 구현해야 합니다.
    """

    def __init__(self, html: str):
        self.html = html
        logging.info("BaseExtractor 초기화 완료")

    @abstractmethod
    def get_title(self) -> str:
        """
        페이지의 제목을 추출합니다.
        """
        pass

    @abstractmethod
    def get_text(self) -> str:
        """
        페이지의 본문 텍스트를 추출합니다.
        """
        pass

    @abstractmethod
    def get_image(self) -> str:
        """
        페이지의 대표 이미지를 추출합니다.
        """
        pass