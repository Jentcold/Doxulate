document.addEventListener("DOMContentLoaded", function() {
    const uploadBox = document.getElementById("uploadBox");
    const fileInput = document.getElementById("fileInput");
    const sourceDropdown = document.getElementById("sourceLang");
    const targetDropdown = document.getElementById("targetLang");
    const uploadButton = document.getElementById("uploadButton");
    const translateButton = document.getElementById("translateButton");
    const downloadButton = document.getElementById("downloadButton");
    const loadText = document.getElementById("loadText");
    const messageBox = document.getElementById("messageBox"); 

    // Centralized base URL
    const API_BASE = window.API_BASE || window.location.origin;

    // inline messages
    function showMessage(type, text, timeout = 5000) {
        messageBox.textContent = text;
        messageBox.className = "";          
        messageBox.classList.add(type);     
        messageBox.style.display = "block";
        if (timeout) {
            setTimeout(() => { messageBox.style.display = "none"; }, timeout);
        }
    }

    // Fallback languages
    const FALLBACK_LANGUAGES = {
        en: "English", fr: "French", ar: "Arabic",
        es: "Spanish", de: "German", zh: "Chinese"
    };

    // Load languages from API or fallback
    async function loadLanguages() {
        try {
            let res = await fetch(`https://localhost:5000/languages`);
            if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
            let list = await res.json();
            return list.reduce((m, l) => (m[l.code] = l.name, m), {});
        } catch (err) {
            console.warn("Language load failed:", err);
            showMessage("error", "Could not load languages, using defaults.");
            return FALLBACK_LANGUAGES;
        }
    }

    // Populate dropdowns
    async function initLanguageDropdowns() {
        const langs = await loadLanguages();
        [sourceDropdown, targetDropdown].forEach(dd => dd.innerHTML = "");
        Object.entries(langs).forEach(([code, name]) => {
            sourceDropdown.add(new Option(name, code));
            targetDropdown.add(new Option(name, code));
        });
        if (langs.en) sourceDropdown.value = "en";
        if (langs.es) targetDropdown.value = "es";
    }

    // UI reset 
    function resetUI() {
        loadText.style.display = "none";
        downloadButton.style.display = "none";
        uploadButton.disabled = false;
        translateButton.disabled = false;
        fileInput.value = "";
        document.getElementById("changetxt").textContent = "No file selected";
        document.querySelector(".Upload").style.display = "none";
        document.querySelector(".noUpload").style.display = "block";
    }

    // File select handlers
    document.getElementById("uploadButton").addEventListener("click", () => fileInput.click());
    fileInput.addEventListener("change", e => {
        let file = e.target.files[0];
        if (file) {
            document.getElementById("changetxt").textContent = file.name;
            document.querySelector(".Upload").style.display = "block";
            document.querySelector(".noUpload").style.display = "none";
        }
    });
    uploadBox.addEventListener("dragover", e => {
        e.preventDefault(); uploadBox.classList.add("dragover");
    });
    uploadBox.addEventListener("dragleave", () => uploadBox.classList.remove("dragover"));
    uploadBox.addEventListener("drop", e => {
        e.preventDefault(); uploadBox.classList.remove("dragover");
        let file = e.dataTransfer.files[0];
        if (file) {
            fileInput.files = e.dataTransfer.files;
            document.getElementById("changetxt").textContent = file.name;
            document.querySelector(".Upload").style.display = "block";
            document.querySelector(".noUpload").style.display = "none";
        }
    });

    // Main upload & translate flow
    translateButton.addEventListener("click", uploadAndTranslate);

    async function uploadAndTranslate() {
        let file = fileInput.files[0];
        if (!file) { showMessage("warning", "Please select a file first!"); return; }
        if (!file.name.endsWith(".docx")) { showMessage("error", "Only .docx files allowed."); return; }
        const src = sourceDropdown.value, tgt = targetDropdown.value;
        if (src === tgt) { showMessage("warning", "Source and target must differ."); return; }

        // Prepare UI
        uploadButton.disabled = true;
        translateButton.disabled = true;
        loadText.style.display = "inline-block";
        showMessage("info", "Uploading and translating…", 0); // sticky until clear

        const form = new FormData();
        form.append("file", file);
        form.append("source_lang", src);
        form.append("target_lang", tgt);

        try {
            let res = await fetch(`${API_BASE}/upload/`, { method: "POST", body: form });
            if (!res.ok) {
                let errorMsg = await res.text();
                showMessage("error", `Upload failed: ${errorMsg}`, 8000);
                resetUI();
                return;
            }
            let blob = await res.blob();
            const url = URL.createObjectURL(blob);
            downloadButton.style.display = "inline-block";
            showMessage("success", "Ready to download!");
            downloadButton.onclick = () => {
                const a = document.createElement("a");
                a.href = url;
                a.download = "translated_" + file.name;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                resetUI();
            };
        } catch (err) {
            console.error("Network error:", err);
            showMessage("error", "Network error. Please try again.");
            resetUI();
        } finally {
            loadText.style.display = "none";
        }
    }

    initLanguageDropdowns();
});
