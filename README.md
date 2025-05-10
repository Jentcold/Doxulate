# Doxulate - Document Translation Web App

![Doxulate Screenshot](![image]()) 

FastAPI-powered web application for translating documents using LibreTranslate's self-hosted engine.

## Features

- DOCX file translation with formatting preservation 
- Multi-language support (English, Spanish, French, etc.)
- Simple drag-and-drop interface
- Self-contained Docker deployment
- ( PDF and other formats support soon )

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.12+
- 4GB RAM minimum (8GB recommended for better performance)

## One-Command Deployment

```bash
git clone https://github.com/Jentcold/Doxulate.git
cd Doxulate
docker-compose up --build
```

Access the application at: [http://localhost:8000](http://localhost:8000)

## Docker Services

| Service | Port | Description |
|---------|------|-------------|
| Doxulate | 8000 | Main web interface |
| LibreTranslate | 5000 | Translation engine API |

## File Structure

```
.
├── site/               # Frontend templates and assets
├── tmp/                # Temporary operation storage (auto-created)
├── main.py             # FastAPI application
├── Functions.py        # Core translation logic
├── Dockerfile          # App container configuration
└── docker-compose.yml  # Full environment setup
```

## Environment Variables

Configure in `docker-compose.yml`:

- `LIBRETRANSLATE_URL`: Translation service endpoint
- `LOAD_ONLY`: Specify languages to enable to save space
  (Simply remove the command if you wish to download all languages)

## Development Mode

```bash
# Run with live reload for frontend changes
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Troubleshooting

**Q**: Translations fail with connection errors  
**A**: Wait 30-60 seconds after startup for LibreTranslate to initialize 

**Q**: File uploads failing  
**A**: Ensure the `tmp` directory exists and have write permissions

## License

MIT License - See [LICENSE](LICENSE) for details.
