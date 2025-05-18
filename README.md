# Doxulate - Document Translation Web App

![Doxulate Screenshot ](https://github.com/user-attachments/assets/cdd7d29e-4bdd-42cf-ba66-e9bba2efac0c)



FastAPI-powered web application for translating documents using LibreTranslate's self-hosted engine.

## Features

- DOCX file translation with formatting preservation 
- Customizable translation engine
- Simple drag-and-drop interface
- ( PDF and other formats support soon )

## Prerequisites

- Docker Engine 20.10+ (optional)
- 4GB RAM minimum (8GB recommended for better performance)

## Deployment commands

```bash
git clone https://github.com/Jentcold/Doxulate.git
cd Doxulate

docker run -d -p 5000:5000 libretranslate/libretranslate:latest

pip install -r requirements.txt

python main.py

```

Access the application at: [http://localhost:8000](http://localhost:8000)

## Services

| Service | Port | Description |
|---------|------|-------------|
| Doxulate | 8000 | Main web interface |
| LibreTranslate | 5000 | Docker Translation engine API |

### Note :

Since this is a quickstart guide i have opted for libretranslate since its simple, self hosted, maintaned and free to use, that being said the translation language model you use is up to you just make sure to update the Languages list in "main.py" and the translation function in "Functions.py" or use an enviromental variable.

## File Structure

```
.
├── site/               # Frontend templates and assets
├── tmp_uploaded/       # Temporary operation storage (auto-created)
├── tmp_translated/     # Temporary finished file storage (auto-created)
├── main.py             # FastAPI application
├── Functions.py        # Core translation logic
├── Dockerfile          # App container configuration
└── docker-compose.yml  # Full environment setup
```

## Troubleshooting

**Q**: Translations fail with connection errors  
**A**: Ensure your translation engine is up and running 

**Q**: File uploads failing  
**A**: Ensure the `tmp` directory exists and have write permissions

## License

MIT License - See [LICENSE](LICENSE) for details.
