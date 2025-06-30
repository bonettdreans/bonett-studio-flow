# 🎬 Bonett Studio Flow API

> API completa para processamento de vídeos e geração de conteúdo audiovisual

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg)](https://ffmpeg.org/)

## 📖 Sobre

A **Bonett Studio Flow API** é uma solução robusta para processamento de vídeos, oferecendo múltiplas funcionalidades em uma única API. Desenvolvida para atender às necessidades de criação de conteúdo audiovisual, desde adição de banners até remoção de chroma key.

## ✨ Funcionalidades

- 🎨 **Banner em Vídeos** - Adicione banners personalizados aos seus vídeos
- ✂️ **Corte de Vídeos** - Edite e corte vídeos com precisão
- 🏷️ **Marca D'água** - Aplique watermarks para proteger seu conteúdo
- 🎥 **Processamento Geral** - Ferramentas diversas para manipulação de vídeo
- 🟢 **Chroma Key** - Remova fundos verdes profissionalmente  
- 🎵 **Áudio** - Mixe, processe e adicione áudios aos vídeos

## 🔧 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **FFmpeg** - Engine de processamento de áudio/vídeo
- **Uvicorn** - Servidor ASGI de alta performance
- **Python 3.8+** - Linguagem de programação

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- [Python 3.8 ou superior](https://www.python.org/)
- [FFmpeg](https://ffmpeg.org/download.html)
- [Git](https://git-scm.com/)

### Verificar instalações:
```bash
python --version
ffmpeg -version
git --version
```

## 🚀 Instalação e Execução

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/bonett-studio-flow.git
cd bonett-studio-flow
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute a API
```bash
python -m app.main
```

A API estará disponível em: **http://localhost:8080**

## 📚 Documentação da API

Após executar a API, acesse:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

## 🛠️ Endpoints Principais

| Serviço | Endpoint Base | Descrição |
|---------|---------------|-----------|
| Banner | `/api/v1/banner/*` | Adição de banners em vídeos |
| Corte | `/api/v1/cut/*` | Ferramentas de edição e corte |
| Marca D'água | `/api/v1/watermark/*` | Aplicação de watermarks |
| Processamento | `/api/v1/video/*` | Ferramentas gerais de vídeo |
| Chroma Key | `/api/v1/green-screen/*` | Remoção de fundo verde |
| Áudio | `/api/v1/audio/*` | Processamento de áudio |

## 📁 Estrutura do Projeto

```
bonett-studio-flow/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicação principal
│   ├── routers/             # Rotas da API
│   │   ├── __init__.py
│   │   ├── banner_router.py
│   │   ├── cut_router.py
│   │   ├── watermark_router.py
│   │   ├── video_processing_router.py
│   │   ├── green_screen_router.py
│   │   └── audio_router.py
│   └── services/            # Lógica de negócio
│       └── audio_service.py
├── requirements.txt
└── README.md
```

## 🎯 Formatos Suportados

### Vídeo
- `.mp4` - Formato principal recomendado
- `.mkv`, `.avi`, `.mov`, `.flv`, `.wmv` - Formatos adicionais

### Áudio
- `.mp3` - Formato principal recomendado
- `.wav`, `.aac`, `.m4a` - Formatos adicionais

### Imagem
- `.png` - Formato principal recomendado
- `.jpg`, `.jpeg`, `.gif` - Formatos adicionais

## 🔧 Configuração

### Variáveis de Ambiente (opcional)
```bash
# .env
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=info
FFMPEG_PATH=/usr/bin/ffmpeg  # Se necessário especificar
```

### Configuração do FFmpeg
Certifique-se de que o FFmpeg está no PATH do sistema ou configure o caminho manualmente nos serviços.

## 🧪 Exemplo de Uso

### Mixar áudio com vídeo (Python)
```python
import requests

url = "http://localhost:8080/api/v1/audio/mix"
files = {
    'video_file': open('video.mp4', 'rb'),
    'audio_file': open('audio.mp3', 'rb')
}
data = {
    'replace_original': True,
    'reduce_original_volume': False
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

### Via cURL
```bash
curl -X POST "http://localhost:8080/api/v1/audio/mix" \
  -F "video_file=@video.mp4" \
  -F "audio_file=@audio.mp3" \
  -F "replace_original=true"
```

## 🚨 Troubleshooting

### Problemas Comuns

**1. Erro: "FFmpeg not found"**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg

# macOS (via Homebrew)  
brew install ffmpeg
```

**2. Erro de importação de módulos**
```bash
# Execute sempre da pasta raiz do projeto
python -m app.main
```

**3. Porta já em uso**
```bash
# Mude a porta no main.py ou mate o processo
lsof -ti:8080 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8080   # Windows
```

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Roadmap

- [ ] Suporte a mais formatos de vídeo
- [ ] Interface web para upload/preview
- [ ] Processamento em batch
- [ ] Sistema de filas para processamentos longos
- [ ] Compressão automática de vídeos
- [ ] Integração com cloud storage
- [ ] Suporte a legendas automáticas

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@bonettdreans](https://github.com/bonettdreans)


---

⭐ **Se este projeto te ajudou, deixe uma estrela!**
