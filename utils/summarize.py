# 파일 위치: summarize.py

import os
import json
import logging
import re
from datetime import datetime
from extractors.soup_extractor import SoupExtractor
from utils.translator import translate_to_korean
from utils.fetcher import fetch_html
from utils.llm import call_llm  # ✅ LLM 요약 호출용
import markdown2

logger = logging.getLogger(__name__)
SAVE_FOLDER = "data/summaries"

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def extract_and_replace_images(md_text: str):
    pattern = r'!\[.*?\]\(.*?\)'
    images = []
    def replace(match):
        images.append(match.group(0))
        return f"[[IMG{len(images)-1}]]"
    cleaned = re.sub(pattern, replace, md_text)
    return cleaned, images

def restore_images(translated_text: str, image_blocks: list):
    for i, img in enumerate(image_blocks):
        translated_text = translated_text.replace(f"[[IMG{i}]]", img)
    return translated_text

def save_to_markdown(title: str, translated_title: str, date: str, url: str,
                     original: str, translated: str, summary: str, images: list) -> dict:
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    slug = slugify(title)
    base = f"{date}-{slug}"

    original_md = os.path.join(SAVE_FOLDER, f"{base}.original.md")
    translate_md = os.path.join(SAVE_FOLDER, f"{base}.translate.md")
    summary_md = os.path.join(SAVE_FOLDER, f"{base}.summary.md")
    meta_json = os.path.join(SAVE_FOLDER, f"{base}.json")

    with open(original_md, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{original}")
    with open(translate_md, "w", encoding="utf-8") as f:
        f.write(f"# {translated_title}\n\n{translated}")
    with open(summary_md, "w", encoding="utf-8") as f:
        f.write(f"# {translated_title}\n\n{summary}")

    timestamp = datetime.now().timestamp()

    meta = {
        "title": title,
        "translated_title": translated_title,
        "date": date,
        "url": url,
        "md_path_original": original_md,
        "md_path_translate": translate_md,
        "md_path_summary": summary_md,
        "has_original": os.path.exists(original_md),
        "has_translate": os.path.exists(translate_md),
        "has_summary": os.path.exists(summary_md),
        "timestamp": timestamp,
        "images": images,
        "main_image": images[0] if images else ""
    }

    with open(meta_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    logger.info(f"[summarize.py] ✅ 파일 저장 완료: {base}")
    return meta

def markdown_to_html(md_text: str) -> str:
    try:
        html = markdown2.markdown(md_text)
        logger.info("[summarize.py] ✅ 마크다운 → HTML 변환 완료")
        return html
    except Exception as e:
        logger.warning(f"[summarize.py] ⚠️ 마크다운 변환 실패: {e}")
        return md_text

def summarize_url(url: str, summary_mode: str = "default") -> dict:
    try:
        logger.info(f"[summarize.py] ✅ 요약 시작: {url} (mode: {summary_mode})")

        html = fetch_html(url)
        if not html:
            raise ValueError("HTML을 가져오지 못했습니다.")

        extractor = SoupExtractor(html, url)
        title = extractor.get_title()
        content = extractor.get_text_with_images()

        if not content or len(content) < 100:
            raise ValueError("본문 내용이 너무 짧습니다.")
        logger.info(f"[summarize.py] ✅ 본문 추출 완료 (길이: {len(content)}자)")

        images = extractor.get_images()
        main_image = extractor.get_image()

        translated_title = translate_to_korean(title)
        logger.info(f"[summarize.py] ✅ 제목 번역: {translated_title}")

        # ✅ 이미지 치환 후 번역
        content_wo_img, image_blocks = extract_and_replace_images(content)
        translated_raw = translate_to_korean(content_wo_img)
        translated = restore_images(translated_raw, image_blocks)
        logger.info(f"[summarize.py] ✅ 본문 번역 완료")

        # ✅ 요약 방식 분기
        if summary_mode == "llm":
            summary_raw = call_llm(content, task="summarize", model="gemma-3-4b-it-qat")
            summary = restore_images(summary_raw, image_blocks)
            logger.info(f"[summarize.py] ✅ LLM 요약 완료")
        else:
            summary = translated
            logger.info(f"[summarize.py] ✅ 기본 요약 사용")

        summary_html = markdown_to_html(summary)

        today = datetime.now().strftime("%Y-%m-%d")
        meta = save_to_markdown(title, translated_title, today, url, content, translated, summary, images)

        return {
            "title": title,
            "translated_title": translated_title,
            "date": today,
            "url": url,
            "summary": summary_html,
            "original": content,
            "translated": translated,
            "md_path_original": meta["md_path_original"],
            "md_path_translate": meta["md_path_translate"],
            "md_path_summary": meta["md_path_summary"],
            "has_original": meta["has_original"],
            "has_translate": meta["has_translate"],
            "has_summary": meta["has_summary"],
            "images": images,
            "main_image": images[0] if images else ""
        }

    except Exception as e:
        logger.error(f"[summarize.py] ❌ 요약 실패: {e}")
        return {
            "title": "요약 실패",
            "translated_title": "요약 실패",
            "summary": f"❌ 요약 중 오류 발생: {e}",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "url": url,
            "original": "",
            "translated": "",
            "has_summary": False,
            "has_translate": False,
            "has_original": False
        }