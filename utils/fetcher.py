# utils/fetcher.py

import requests
from requests.exceptions import RequestException, Timeout
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [fetcher.py] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": "https://www.google.com/"
}


def fetch_html(url: str, timeout: int = 10) -> str:
    """
    주어진 URL로부터 HTML 콘텐츠를 가져옵니다.

    Args:
        url (str): 가져올 웹페이지의 URL
        timeout (int): 요청 타임아웃 (초)

    Returns:
        str: HTML 문자열

    Raises:
        Exception: 요청 실패 시 예외 발생
    """
    logging.info(f"HTML 요청 시작: {url}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        # 인코딩 우선순위: HTTP 헤더 > meta charset > apparent_encoding
        encoding = response.encoding
        content_type = response.headers.get("Content-Type", "")
        if "charset=" in content_type:
            encoding = content_type.split("charset=")[-1].split(";")[0].strip()
        else:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, "html.parser")
            meta = soup.find("meta", charset=True)
            if meta:
                encoding = meta.get("charset")
            else:
                meta = soup.find("meta", attrs={"http-equiv": "Content-Type"})
                if meta and "charset=" in meta.get("content", ""):
                    encoding = meta.get("content").split("charset=")[-1].strip()

        response.encoding = encoding or response.apparent_encoding
        try:
            html = response.text
        except UnicodeDecodeError:
            html = response.content.decode("utf-8", errors="replace")
        logging.info(f"HTML 요청 성공: {url} [상태코드: {response.status_code}]")
        return html

    except Timeout:
        logging.error(f"[Timeout] 요청 시간 초과: {url}")
        raise

    except RequestException as e:
        logging.error(f"[Error] 요청 실패: {url} - {e}")
        raise


# 테스트 실행
if __name__ == "__main__":
    test_url = "https://example.com"
    try:
        html = fetch_html(test_url)
        print(html[:500])  # 출력 생략 방지를 위한 요약 출력
    except Exception as e:
        logging.error(f"테스트 실행 중 오류 발생: {e}")