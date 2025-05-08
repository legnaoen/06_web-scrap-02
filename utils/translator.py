# 파일 위치: utils/translator.py

import logging
import re
from googletrans import Translator

# 로그 설정
logger = logging.getLogger(__name__)

def restore_markdown(text: str) -> str:
    """
    번역 후 깨진 마크다운 문법을 복원합니다.
    예: '* 문제 *' -> '*문제*', '** 사용자 **' -> '**사용자**'
    """
    text = re.sub(r'\*\s*(.*?)\s*\*', r'*\1*', text)
    text = re.sub(r'\*\*\s*(.*?)\s*\*\*', r'**\1**', text)
    text = re.sub(r'__\s*(.*?)\s*__', r'__\1__', text)
    text = re.sub(r'`{1,3}\s*(.*?)\s*`{1,3}', r'`\1`', text)
    text = re.sub(r'#{1,6}\s+', lambda m: m.group(0).strip() + ' ', text)
    return text

def split_into_chunks(text: str, max_length: int = 4000) -> list:
    """
    텍스트를 max_length를 기준으로 자르되 줄 단위로 나눔
    """
    lines = text.splitlines(keepends=True)
    chunks = []
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) > max_length:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += line

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

def translate_to_korean(text: str) -> str:
    """
    텍스트를 4000자 단위로 나눠 Google 번역, 마크다운 복원 포함
    """
    try:
        translator = Translator()
        chunks = split_into_chunks(text)
        results = []

        for i, chunk in enumerate(chunks):
            try:
                result = translator.translate(chunk, dest='ko')
                results.append(result.text)
            except Exception as e:
                logger.warning(f"[translator.py] ⚠️ 번역 실패 (블록 {i+1}): {e}")
                results.append(chunk)

        joined = "\n".join(results)
        logger.info(f"[translator.py] ✅ 전체 번역 완료 (총 {len(chunks)}블록)")
        return restore_markdown(joined)

    except Exception as e:
        logger.error(f"[translator.py] ❌ 전체 번역 실패: {e}")
        return text