document.addEventListener("DOMContentLoaded", function () {
    const summarizeBtn = document.getElementById("summarize-btn");
    const urlInput = document.getElementById("url-input");
    const summaryModeSelect = document.getElementById("summary-mode");  // ✅ 추가된 셀렉트박스

    const titleEl = document.getElementById("summary-title");
    const dateEl = document.getElementById("summary-date");
    const linkEl = document.getElementById("summary-link");

    const summaryEl = document.getElementById("summary-body");
    const translatedEl = document.getElementById("translated-body");
    const originalEl = document.getElementById("original-body");

    const tabSummary = document.getElementById("tab-btn-summary");
    const tabTranslated = document.getElementById("tab-btn-translated");
    const tabOriginal = document.getElementById("tab-btn-original");

    const imageEl = document.getElementById("main-image");
    const imageGalleryEl = document.getElementById("image-gallery") || null;

    summarizeBtn.addEventListener("click", async () => {
        const url = urlInput.value.trim();
        const summaryMode = summaryModeSelect ? summaryModeSelect.value : "default";  // ✅ 드롭다운 값 읽기

        if (!url) {
            summaryEl.innerHTML = "❗ URL을 입력해주세요.";
            return;
        }

        clearOutput();
        summaryEl.innerHTML = "⏳ 요약 중...";

        try {
            const response = await fetch("/summarize", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url, summary_mode: summaryMode })  // ✅ 요청에 포함
            });

            const data = await response.json();

            if (data.title && data.date) {
                renderTabs(data);
                addToHistory(data);
                window.historyData.unshift(data);
                urlInput.value = "";
            } else {
                summaryEl.innerHTML = `❌ 오류: ${data.error || "알 수 없는 오류"}`;
            }
        } catch (error) {
            summaryEl.innerHTML = `❌ 네트워크 오류: ${error}`;
        }
    });

    // 이하 기존 코드 변경 없음 ----------------------------

    document.querySelectorAll(".list-group-item").forEach((item) => {
        item.addEventListener("click", async (e) => {
            if (e.target.classList.contains("delete-btn")) return;
            renderTabs({
                title: item.getAttribute("data-title"),
                date: item.getAttribute("data-date"),
                url: item.getAttribute("data-url"),
                md_path_summary: item.getAttribute("data-md-summary"),
                md_path_translate: item.getAttribute("data-md-translate"),
                md_path_original: item.getAttribute("data-md-original"),
                main_image: item.getAttribute("data-main-image") || "",
                images: window.historyData.find(d => d.url === item.getAttribute("data-url"))?.images || []
            });
        });
    });

    document.querySelectorAll(".delete-btn").forEach((btn) => {
        btn.addEventListener("click", async (e) => {
            e.stopPropagation();
            const li = e.target.closest("li");

            const payload = {
                md_path_summary: li.getAttribute("data-md-summary"),
                md_path_translate: li.getAttribute("data-md-translate"),
                md_path_original: li.getAttribute("data-md-original"),
                meta_json: li.getAttribute("data-md-summary")?.replace(/\.summary\.md$/, ".json")
            };

            if (confirm(`'${li.getAttribute("data-title")}' 항목을 삭제하시겠습니까?`)) {
                try {
                    const res = await fetch("/delete_summary", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify(payload)
                    });
                    const result = await res.json();
                    if (result.success) {
                        li.remove();
                        clearOutput("🗑️ 항목이 삭제되었습니다.");
                    } else {
                        alert("❌ 삭제 실패: " + result.error);
                    }
                } catch (err) {
                    alert("❌ 삭제 요청 중 오류 발생: " + err);
                }
            }
        });
    });

    async function renderTabs({ title, date, url, md_path_summary, md_path_translate, md_path_original, main_image, images = [] }) {
        titleEl.innerText = title;
        dateEl.innerText = date;
        linkEl.href = url;
        linkEl.innerText = "원문 링크";

        if (imageEl) {
            imageEl.src = main_image || "";
            imageEl.style.display = main_image ? "block" : "none";
        }

        if (imageGalleryEl) {
            imageGalleryEl.innerHTML = "";
            if (Array.isArray(images) && images.length > 0) {
                for (const src of images) {
                    const img = document.createElement("img");
                    img.src = src;
                    img.alt = "본문 이미지";
                    imageGalleryEl.appendChild(img);
                }
            }
        }

        const tabs = [
            { name: "summary", path: md_path_summary, button: tabSummary, el: summaryEl },
            { name: "translated", path: md_path_translate, button: tabTranslated, el: translatedEl },
            { name: "original", path: md_path_original, button: tabOriginal, el: originalEl }
        ];

        let firstValidTab = null;

        for (const tab of tabs) {
            if (tab.path) {
                const content = await loadMarkdown(tab.path);
                if (content !== null) {
                    tab.el.innerHTML = window.marked ? marked.parse(content) : content;
                    tab.button.disabled = false;
                    if (!firstValidTab) firstValidTab = tab;
                } else {
                    tab.el.innerHTML = "❗ 내용을 불러올 수 없습니다.";
                    tab.button.disabled = true;
                }
            } else {
                tab.el.innerHTML = "❗ 파일 없음";
                tab.button.disabled = true;
            }
        }

        document.querySelectorAll(".nav-link").forEach(btn => btn.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active", "show"));

        if (firstValidTab) {
            firstValidTab.button.classList.add("active");
            document.getElementById("tab-" + firstValidTab.name).classList.add("active", "show");
        } else {
            summaryEl.innerHTML = "❗ 표시할 내용이 없습니다.";
        }

        // ✅ Retry 버튼 생성 및 이벤트 등록
        const retryBtnId = "retry-summary-btn";
        let retryBtn = document.getElementById(retryBtnId);
        if (!retryBtn) {
            retryBtn = document.createElement("button");
            retryBtn.id = retryBtnId;
            retryBtn.textContent = "Retry";
            retryBtn.className = "btn btn-sm btn-outline-secondary mt-2"; // margin top for spacing

            const summaryTabContent = document.getElementById("tab-summary");
            if (summaryTabContent) {
                summaryTabContent.insertAdjacentElement("beforeend", retryBtn);
            } else {
                summaryEl.insertAdjacentElement("afterend", retryBtn);
            }
        }

        retryBtn.onclick = async () => {
            summaryEl.innerHTML = "⏳ 요약 다시 시도 중...";
            try {
                const response = await fetch("/retry_summary", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ md_path_original: md_path_original })
                });

                const data = await response.json();
                if (data.success) {
                    const updatedContent = await loadMarkdown(md_path_summary);
                    if (updatedContent) {
                        summaryEl.innerHTML = window.marked ? marked.parse(updatedContent) : updatedContent;
                        const currentLi = document.querySelector(`.list-group-item[data-url="${url}"]`);
                        if (currentLi && data.new_md_path_summary) {
                            currentLi.setAttribute("data-md-summary", data.new_md_path_summary);
                        }
                    } else {
                        summaryEl.innerHTML = "❌ 요약 실패: 새로운 요약 파일을 불러올 수 없습니다.";
                    }
                } else {
                    summaryEl.innerHTML = `❌ 요약 실패: ${data.error || "요약 결과 없음"}`;
                }
            } catch (err) {
                summaryEl.innerHTML = `❌ 네트워크 오류: ${err}`;
            }
        };
    }

    async function loadMarkdown(path) {
        try {
            const res = await fetch("/read_md", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ path })
            });
            const result = await res.json();
            return result.success ? result.content : null;
        } catch {
            return null;
        }
    }

    function addToHistory({ title, date, url, md_path_summary, md_path_translate, md_path_original, main_image }) {
        const ul = document.querySelector(".list-group");

        const li = document.createElement("li");
        li.className = "list-group-item list-group-item-action";
        li.setAttribute("data-title", title);
        li.setAttribute("data-date", date);
        li.setAttribute("data-url", url);
        li.setAttribute("data-md-summary", md_path_summary || "");
        li.setAttribute("data-md-translate", md_path_translate || "");
        li.setAttribute("data-md-original", md_path_original || "");
        li.setAttribute("data-main-image", main_image || "");

        li.innerHTML = `
            <span class="history-title">🔗 ${title}</span>
            <span class="text-danger delete-btn">❌</span>
        `;

        li.addEventListener("click", () => {
            renderTabs({
                title,
                date,
                url,
                md_path_summary,
                md_path_translate,
                md_path_original,
                main_image,
                images: window.historyData.find(d => d.url === url)?.images || []
            });
        });

        li.querySelector(".delete-btn").addEventListener("click", async (e) => {
            e.stopPropagation();
            const payload = {
                md_path_summary,
                md_path_translate,
                md_path_original,
                meta_json: md_path_summary?.replace(/\.summary\.md$/, ".json")
            };

            const confirmed = confirm(`'${title}' 항목을 삭제하시겠습니까?`);
            if (confirmed) {
                const res = await fetch("/delete_summary", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();
                if (result.success) {
                    li.remove();
                    clearOutput("🗑️ 항목이 삭제되었습니다.");
                } else {
                    alert("❌ 삭제 실패: " + result.error);
                }
            }
        });

        ul.prepend(li);
    }

    function clearOutput(msg = "") {
        titleEl.innerText = "";
        dateEl.innerText = "";
        linkEl.innerText = "";
        summaryEl.innerHTML = msg;
        translatedEl.innerHTML = "";
        originalEl.innerHTML = "";

        if (imageEl) {
            imageEl.src = "";
            imageEl.style.display = "none";
        }

        if (imageGalleryEl) {
            imageGalleryEl.innerHTML = "";
        }

        tabSummary.disabled = true;
        tabTranslated.disabled = true;
        tabOriginal.disabled = true;

        document.querySelectorAll(".nav-link").forEach(btn => btn.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active", "show"));
    }
});