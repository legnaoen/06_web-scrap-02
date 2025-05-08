# 파일 위치: utils/test_llm.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm import call_llm

# ✅ 테스트할 입력 텍스트 (프롬프트는 내부에서 자동 생성됨)
content_to_translate = "Design-minded home goods brand Simplehuman recently released a product that’s a little out of its wheelhouse—a limited-edition tequila with distillery Nosotros. It may be the company’s first foray into spirits, but the brand already knows how to work with the Weber blue agave that made the tequila. The agave fibers on Simplehuman’s Soapwell sponge begin their life cycle by being pressed into Nosotros tequila at the company’s distillery in Tequila, Mexico. Nosotros then supplies its leftover agave fibers to Simplehuman. The $100 Nosotros x Simplehuman Blanco tequila is made out of that same agave, and was released to mark a year that Simplehuman has been spinning the fibers into sponges."

if __name__ == "__main__":
    print("=== 원본 입력 ===")
    print(content_to_translate)

    translated = call_llm(content_to_translate, task="translate", model="gemma-3-4b-it-qat")
    print("\n=== 번역 결과 ===")
    print(translated)

    summarized = call_llm(content_to_translate, task="summarize", model="gemma-3-4b-it-qat")
    print("\n=== 요약 결과 ===")
    print(summarized)