from flask import Flask, request, jsonify, render_template
from utils.summarize import summarize_url
import logging
import os
import json

app = Flask(__name__)


# 🔹 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 요약 저장 폴더
SUMMARY_FOLDER = os.path.join("data", "summaries")
os.makedirs(SUMMARY_FOLDER, exist_ok=True)

# 🔹 요약 이력 로드 함수
def load_history():
    history = []
    if os.path.exists(SUMMARY_FOLDER):
        for fname in os.listdir(SUMMARY_FOLDER):
            if fname.endswith(".json"):
                fpath = os.path.join(SUMMARY_FOLDER, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        item = json.load(f)
                        item["has_summary"] = item.get("has_summary", os.path.exists(item.get("md_path_summary", "")))
                        item["has_translate"] = item.get("has_translate", os.path.exists(item.get("md_path_translate", "")))
                        item["has_original"] = item.get("has_original", os.path.exists(item.get("md_path_original", "")))
                        item["timestamp"] = item.get("timestamp", os.path.getmtime(fpath))
                        history.append(item)
                except Exception as e:
                    logger.warning(f"[app.py] ⚠️ 이력 파일 로드 실패: {fname} - {e}")
    history.sort(key=lambda x: x["timestamp"], reverse=True)
    logger.info(f"[app.py] ✅ 이력 {len(history)}개 로드 완료 (최신순 정렬)")
    return history

# 🔹 메인 페이지
@app.route('/')
def index():
    logger.info("[app.py] ✅ 메인 페이지 요청 수신")
    history = load_history()
    return render_template("index.html", history=history)

# 🔹 요약 처리
@app.route('/summarize', methods=['POST'])
def summarize():
    try:
        data = request.get_json()
        url = data.get("url", "").strip()
        summary_mode = data.get("summary_mode", "default")
        logger.info(f"[app.py] 📥 요약 요청 수신: {url} (요약 모드: {summary_mode})")

        result = summarize_url(url, summary_mode=summary_mode)
        logger.info(f"[app.py] ✅ 요약 및 저장 완료: {result.get('title')}")

        # 🔸 이미지 반영 여부 로깅
        if result.get("main_image"):
            logger.info(f"[app.py] 🖼️ 대표 이미지 포함됨: {result.get('main_image')}")
        else:
            logger.info(f"[app.py] 🖼️ 대표 이미지 없음")

        return jsonify({
            "title": result.get("title"),
            "translated_title": result.get("translated_title"),
            "date": result.get("date"),
            "url": result.get("url"),
            "summary": result.get("summary"),
            "original": result.get("original"),
            "translated": result.get("translated"),
            "md_path_original": result.get("md_path_original"),
            "md_path_translate": result.get("md_path_translate"),
            "md_path_summary": result.get("md_path_summary"),
            "has_original": result.get("has_original"),
            "has_translate": result.get("has_translate"),
            "has_summary": result.get("has_summary"),
            "main_image": result.get("main_image")  # ✅ 이미지 정보 포함
        })

    except Exception as e:
        logger.error(f"[app.py] ❌ 요약 처리 실패: {e}")
        return jsonify({"error": "요약 처리 중 오류 발생"}), 500

# 🔹 마크다운 읽기
@app.route('/read_md', methods=['POST'])
def read_md():
    try:
        data = request.get_json()
        md_path = data.get("path", "").strip()

        if not md_path.startswith(SUMMARY_FOLDER):
            logger.warning(f"[app.py] ❌ 잘못된 경로 요청 차단: {md_path}")
            return jsonify({"success": False, "error": "허용되지 않은 파일 경로입니다."})

        if not os.path.exists(md_path):
            logger.warning(f"[app.py] ❌ 파일 없음: {md_path}")
            return jsonify({"success": False, "error": "파일이 존재하지 않습니다."})

        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()

        logger.info(f"[app.py] ✅ 마크다운 파일 로드 성공: {md_path}")
        return jsonify({"success": True, "content": content})

    except Exception as e:
        logger.error(f"[app.py] ❌ 마크다운 파일 읽기 실패: {e}")
        return jsonify({"success": False, "error": "파일 읽기 중 오류 발생"})

# 🔹 파일 삭제 API
@app.route('/delete_summary', methods=['POST'])
def delete_summary():
    try:
        data = request.get_json()
        md_path_summary = data.get("md_path_summary", "").strip()
        md_path_translate = data.get("md_path_translate", "").strip()
        md_path_original = data.get("md_path_original", "").strip()
        meta_json = data.get("meta_json", "").strip()

        if not meta_json and md_path_summary:
            base = os.path.basename(md_path_summary).replace(".summary.md", "")
            meta_json = os.path.join(SUMMARY_FOLDER, f"{base}.json")

        target_files = [md_path_summary, md_path_translate, md_path_original, meta_json]
        deleted = []

        for path in target_files:
            if path and os.path.exists(path):
                os.remove(path)
                deleted.append(path)

        logger.info(f"[app.py] 🗑️ 삭제 완료: {deleted}")
        return jsonify({"success": True, "deleted": deleted})

    except Exception as e:
        logger.error(f"[app.py] ❌ 삭제 실패: {e}")
        return jsonify({"success": False, "error": "삭제 중 오류 발생"})

# 🔹 재요약 요청 API
@app.route('/retry_summary', methods=['POST'])
def retry_summary():
    try:
        data = request.get_json()
        md_path_original = data.get("md_path_original", "").strip()

        if not md_path_original.startswith(SUMMARY_FOLDER) or not os.path.exists(md_path_original):
            logger.warning(f"[app.py] ❌ 재요약 실패: 잘못된 경로 또는 파일 없음: {md_path_original}")
            return jsonify({"success": False, "error": "잘못된 경로이거나 파일이 존재하지 않습니다."})

        with open(md_path_original, "r", encoding="utf-8") as f:
            original_content = f.read()

        from utils.llm import call_llm  # 동적 import로 내부 순환 방지
        summary_md = call_llm(original_content, task="summarize")

        # 기존 json 메타 정보 불러오기
        base = os.path.basename(md_path_original).replace(".original.md", "")
        meta_path = os.path.join(SUMMARY_FOLDER, f"{base}.json")
        if not os.path.exists(meta_path):
            raise ValueError("메타 정보 파일이 존재하지 않습니다.")

        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)

        translated_title = meta.get("translated_title", meta.get("title", ""))
        summary_md_path = os.path.join(SUMMARY_FOLDER, f"{base}.summary.md")

        with open(summary_md_path, "w", encoding="utf-8") as f:
            f.write(f"# {translated_title}\n\n{summary_md}")

        meta["has_summary"] = True
        meta["md_path_summary"] = summary_md_path

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        logger.info(f"[app.py] 🔁 재요약 완료: {summary_md_path}")
        return jsonify({"success": True, **meta})

    except Exception as e:
        logger.error(f"[app.py] ❌ 재요약 처리 실패: {e}")
        return jsonify({"success": False, "error": "재요약 처리 중 오류 발생"})

# 🔹 실행
if __name__ == '__main__':
    app.run(debug=True)