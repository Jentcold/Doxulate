document.addEventListener("DOMContentLoaded", function() {
    const uploadBox = document.getElementById("uploadBox");
    const fileInput = document.getElementById("fileInput");
    const sourceDropdown = document.getElementById("sourceLang");
    const targetDropdown = document.getElementById("targetLang");

    // Hardcoded fallback languages
    const FALLBACK_LANGUAGES = {
        en: "English",
        fr: "French",
        ar: "Arabic",
        es: "Spanish",
        de: "German",
        zh: "Chinese"
    };

    // Load languages from LibreTranslate API
    async function loadLanguages() {
        try {
            const response = await fetch('http://localhost:5000/languages');
            if (!response.ok) throw new Error('API response not OK');
            
            const apiLanguages = await response.json();
            return apiLanguages.reduce((acc, lang) => {
                acc[lang.code] = lang.name;
                return acc;
            }, {});
        } catch (error) {
            console.warn('Using fallback languages:', error);
            return FALLBACK_LANGUAGES;
        }
    }

    // Populate dropdowns with languages
    async function initLanguageDropdowns() {
        const languages = await loadLanguages();
        
        // Clear existing options
        sourceDropdown.innerHTML = '';
        targetDropdown.innerHTML = '';
        
        // Add new options
        for (const [code, name] of Object.entries(languages)) {
            const option1 = new Option(name, code);
            const option2 = new Option(name, code);
            sourceDropdown.add(option1);
            targetDropdown.add(option2);
        }
        
        // Set sensible defaults if available
        if (languages['en']) sourceDropdown.value = 'en';
        if (languages['es']) targetDropdown.value = 'es';
    }

    // Initialize the page
    async function init() {
        await initLanguageDropdowns();
        
        // File picker
        document.getElementById("uploadButton").addEventListener("click", function() {
            fileInput.click();
        });

        //  Start Translate
        document.getElementById("translateButton").addEventListener("click", function() {
            let file = fileInput.files[0]; // Get selected file

            if (!file) {
                alert("Please select a file first!");
                return;
            }

            uploadFile(file); // Call the upload function
        });

        // Handle file selection
        fileInput.addEventListener("change", function(event) {
            let file = event.target.files[0];
            if (file) {
                console.log("File Name:", file.name); 
                
                document.getElementById("changetxt").textContent = file.name;
                document.querySelector(".Upload").style.display = "block";
                document.querySelector(".noUpload").style.display = "none";
            }
        });

        // Drag & Drop 
        uploadBox.addEventListener("dragover", function(event) {
            event.preventDefault();
            uploadBox.classList.add("dragover");
        });
        uploadBox.addEventListener("dragleave", function() {
            uploadBox.classList.remove("dragover");
        });
        uploadBox.addEventListener("drop", function(event) {
            event.preventDefault();
            uploadBox.classList.remove("dragover");

            let file = event.dataTransfer.files[0];
            if (file) {
                console.log("File Name:", file.name); 
                
                document.getElementById("changetxt").textContent = file.name;
                document.querySelector(".Upload").style.display = "block";
                document.querySelector(".noUpload").style.display = "none";
            }
        });
    }
    init();
    
    // Function to upload file to FastAPI 
    async function uploadFile(file) {
        // Check file type 
        if (!file.name.endsWith(".docx")) {
            alert("File type Not allowed!");
            return;
        }

        // check duplicate languages
        const sourceLang = document.getElementById("sourceLang").value;
        const targetLang = document.getElementById("targetLang").value;
        if (sourceLang === targetLang) {
            alert("Source and target languages cannot be the same.");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        formData.append("source_lang", sourceLang);
        formData.append("target_lang", targetLang);

        // Show load bar and hide buttons
        document.getElementById('loadText').style.display = "inline-block";
        document.getElementById("translateButton").style.display = "none";
        document.getElementById("uploadButton").style.display = "none";

        // Fetch upload function
        try {
            const response = await fetch("/upload/", {
                method: "POST",
                body: formData
            });

            // Check Response
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Upload failed:", errorText);
                resetUI();
                alert("Upload failed. Please try again.");
                return;
            }

            const blob = await response.blob();
            console.log("Blob Type:", blob.type);  // log file type

            // Hide loading and show download button
            document.getElementById('loadText').style.display = "none";
            document.getElementById("downloadButton").style.display = "inline-block";

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "translated_" + file.name;
            document.body.appendChild(a);

            // Click to download 
            document.getElementById("downloadButton").addEventListener("click", function() {
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                // Reset buttons after download
                document.getElementById('loadText').style.display = "none";
                document.getElementById("downloadButton").style.display = "none"; 
                document.getElementById("uploadButton").style.display = "inline-block"; 
                document.getElementById("translateButton").style.display = "inline-block"; 
                resetUI();
            });
        } catch (error) {
            console.error("Network error:", error);
        }
    }

    // Reset UI
    function resetUI() {
        document.getElementById('loadText').style.display = "none";
        document.getElementById("downloadButton").style.display = "none";  
        document.getElementById("uploadButton").style.display = "inline-block";  
        document.getElementById("translateButton").style.display = "inline-block";  

        // Reset file input and text
        document.getElementById("fileInput").value = "";  
        document.getElementById("changetxt").textContent = "No file selected"; 
        document.querySelector(".Upload").style.display = "none";
        document.querySelector(".noUpload").style.display = "block"; 
    }

});
