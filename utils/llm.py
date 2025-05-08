import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# LM Studio 로컬 서버 주소 (prompt 기반 모델은 completions 엔드포인트 사용)
LM_STUDIO_URL = "http://localhost:1234/v1/completions"
def call_llm(text: str, task: str = "translate", model: str = "gemma-3-4b-it-qat") -> str:
    """
    LM Studio에 요청을 보내 번역 또는 요약 결과를 반환받음

    :param text: 입력 텍스트
    :param task: 'translate' 또는 'summarize'
    :param model: 사용할 로컬 모델 이름 (prompt-only 기반)
    :return: 결과 텍스트
    """
    if task == "translate":
        prompt = f"Translate into Korean (no explanation, no repetition, only translated result):\n\n{text}"
    elif task == "summarize":
        prompt = f"Summarize in Korean (no explanation, no repetition):\n\n{text}"
    else:
        raise ValueError("지원되지 않는 작업 유형입니다: 'translate' 또는 'summarize' 중 선택해주세요.")

    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": 2048,
        "temperature": 0.7
    }

    try:
        logger.info(f"[llm.py] 🚀 LLM 요청 시작 (task: {task}, model: {model})")
        response = requests.post(LM_STUDIO_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        content = data.get("choices", [{}])[0].get("text", "").strip()
        logger.info(f"[llm.py] ✅ LLM 응답 수신 완료 (길이: {len(content)}자)")
        return content
    except Exception as e:
        logger.error(f"[llm.py] ❌ LLM 호출 실패: {e}")
        return "❌ LLM 호출 실패"