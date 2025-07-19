# 📄 Doxulate – Translate Full Documents Without Losing Formatting

> Tired of copy-pasting text into translators and ruining your document’s formatting? Doxulate is a document translation app that preserves layout, fonts, and styles — built with FastAPI and fully local.

---

## ✨ Features

- 🔤 Translate entire documents: DOCX (More Soon)
- 🎨 Preserve original formatting (fonts, colors, layout)
- 🚀 Fast and lightweight — runs locally with no cloud dependencies
- 🔐 Private by default — nothing is uploaded unless you choose to
- 🌍 Supports multiple languages using LibreTranslate

---

## 📸 Screenshots

![Doxulate Demo](https://github.com/user-attachments/assets/cdd7d29e-4bdd-42cf-ba66-e9bba2efac0c)

---

## 🧰 Tech Stack

| Layer      | Technology     |
|------------|----------------|
| Backend    | [FastAPI](https://fastapi.tiangolo.com/), Python |
| Frontend   | HTML, CSS, JavaScript |
| Translation Engine | [LibreTranslate](https://libretranslate.com/) |

---

## 📍 Use Cases

- Students translating papers without altering structure
- Professionals handling bilingual contracts or reports
- Agencies processing document batches efficiently

---

## 🚀 How to Run Locally

> Clone the repo and run the FastAPI server:

```bash
git clone https://github.com/Jentcold/Doxulate.git
cd Doxulate
pip install -r requirements.txt
python main.py
