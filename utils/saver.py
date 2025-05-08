# 파일 위치: utils/saver.py

import os
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

# 기본 저장 경로 (필요 시 외부에서 설정 가능하도록 수정 가능)
DEFAULT_SAVE_DIR = "saved_markdowns"

def sanitize_filename(title: str) -> str:
    """파일명으로 사용할 수 있도록 제목을 안전하게 변환"""
    title = re.sub(r'[\\/:"*?<>|]+', "", title)
    return title.strip()[:50]  # 너무 긴 제목은 자름

def save_markdown(title: str, url: str, content_md: str, save_dir: str = DEFAULT_SAVE_DIR) -> str:
    """
    마크다운 형식으로 파일 저장.
    :return: 저장된 파일의 전체 경로
    """
    try:
        # 저장 폴더 없으면 생성
        os.makedirs(save_dir, exist_ok=True)

        # 파일명 구성
        safe_title = sanitize_filename(title)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = f"{date_str}_{safe_title}.md"
        filepath = os.path.join(save_dir, filename)

        # 파일 내용 구성
        markdown_text = f"# {title}\n\n" \
                        f"## URL\n{url}\n\n" \
                        f"## 번역\n\n{content_md.strip()}\n"

        # 저장
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        logger.info(f"[saver.py] ✅ 마크다운 저장 완료: {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"[saver.py] ❌ 마크다운 저장 실패: {e}")
        return ""