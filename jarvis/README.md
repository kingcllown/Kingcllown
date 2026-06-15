# Jarvis - Advanced Asynchronous Desktop Assistant

**A professional, production-ready Turkish desktop assistant framework written in Python.**

## Overview

Jarvis is a modular, asynchronous desktop assistant designed to control OS-level operations with explicit permission management. Built with a robust plugin architecture, it integrates Turkish Speech-to-Text/Text-to-Speech, intent matching, and secure OS control.

## Key Features

- **Asynchronous Architecture**: Non-blocking asyncio event loop for continuous background processing
- **Turkish NLP Integration**: Voice interaction with Turkish language support
- **Secure OS Control**: Permission-based system for app launching, volume control, diagnostics
- **Plugin System**: Extensible architecture for registering custom skills
- **Production-Ready**: Clean code, error handling, logging, configuration management
- **Local LLM Integration**: Optional local LLM API wrapper for advanced intent matching

## Architecture

```
jarvis/
├── core/                    # Core framework
│   ├── __init__.py
│   ├── assistant.py         # Main async event loop & orchestration
│   ├── config.py            # Configuration management
│   └── logger.py            # Centralized logging
├── nlu/                     # Natural Language Understanding
│   ├── __init__.py
│   ├── intent_matcher.py    # Intent detection & routing
│   ├── turkish_nlp.py       # Turkish language utilities
│   └── local_llm_wrapper.py # Optional local LLM integration
├── speech/                  # Speech I/O
│   ├── __init__.py
│   ├── stt.py               # Speech-to-Text (Turkish)
│   └── tts.py               # Text-to-Speech (Turkish)
├── os_control/              # OS-level operations
│   ├── __init__.py
│   ├── permission_manager.py# Permission & security layer
│   ├── app_manager.py       # App launching/killing
│   ├── system_info.py       # System diagnostics (CPU/RAM)
│   └── audio_manager.py     # Volume & audio control
├── plugins/                 # Plugin/Skill system
│   ├── __init__.py
│   ├── base_skill.py        # Base class for all skills
│   ├── skill_registry.py    # Skill discovery & registration
│   └── builtin/             # Built-in skills
│       ├── __init__.py
│       ├── system_skill.py   # System control skills
│       └── info_skill.py     # Information retrieval skills
├── config/
│   ├── default.yaml         # Default configuration
│   ├── permissions.yaml     # Permission policies
│   └── intents.yaml         # Intent definitions
├── tests/
│   ├── __init__.py
│   ├── test_core.py
│   ├── test_nlu.py
│   ├── test_os_control.py
│   └── test_plugins.py
├── requirements.txt         # Dependencies
├── main.py                  # Entry point
└── README.md
```

## Installation

### Prerequisites
- Python 3.9+
- VS Code (recommended)
- Windows/Linux/macOS

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Kingcllown.git
cd jarvis

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
import asyncio
from jarvis.core.assistant import JarvisAssistant

async def main():
    assistant = JarvisAssistant(config_path="config/default.yaml")
    await assistant.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuration

### Permissions System

Control what Jarvis can do via `config/permissions.yaml`:

```yaml
permissions:
  app_launch: true
  app_kill: true
  volume_control: true
  system_diagnostics: true
  file_operations: false  # Disabled by default for security
```

### Intent Definitions

Define intents in `config/intents.yaml`:

```yaml
intents:
  app_launch:
    patterns:
      - "[aç|başlat] {app_name}"
      - "{app_name} aç"
    skill: "system_skill"
    action: "launch_app"
```

## Usage Examples

### Register a Custom Skill

```python
from jarvis.plugins.base_skill import BaseSkill

class WeatherSkill(BaseSkill):
    def __init__(self):
        super().__init__(name="weather", description="Weather information")
    
    async def execute(self, intent, parameters):
        # Your implementation
        return await self.fetch_weather(parameters.get("location"))

# Register in main.py
assistant.skill_registry.register(WeatherSkill())
```

### Voice Interaction

```python
# User speaks: "Spotify aç" (Open Spotify)
# Jarvis processes through pipeline:
# 1. STT: "Spotify aç" → text
# 2. NLU: intent=app_launch, app_name=Spotify
# 3. Permission check: Allowed
# 4. Execute: Launch Spotify
# 5. TTS: "Spotify açılıyor" (Opening Spotify)
```

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
black jarvis/
flake8 jarvis/
```

## Advanced Configuration

### Local LLM Integration

For advanced intent matching using a local LLM (Ollama, LLaMA, etc.):

```yaml
nlu:
  use_local_llm: true
  llm_api_url: "http://localhost:11434/api/generate"
  llm_model: "mistral"
```

### Custom Speech Engine

Swap STT/TTS providers:

```yaml
speech:
  stt_provider: "google"  # or "azure", "offline"
  tts_provider: "google"  # or "azure", "pyttsx3"
  language: "tr-TR"
```

## Security Considerations

1. **Permission-Based Model**: Every OS action requires explicit permission
2. **Sandboxing**: Restricted subprocess execution with validated commands
3. **Secure Logging**: Sensitive data (passwords, tokens) never logged
4. **Config Validation**: YAML configs validated against schema on load
5. **Error Handling**: Graceful failures without exposing system internals

## Troubleshooting

### Audio Issues
- Check microphone permissions in OS settings
- Verify audio drivers are installed
- Test with `python -m sounddevice` to list devices

### Intent Not Recognized
- Check `config/intents.yaml` for pattern definitions
- Review logs in `logs/jarvis.log`
- Verify Turkish NLP models are downloaded

## Contributing

Contributions welcome! Please:
1. Create a feature branch
2. Add tests for new functionality
3. Follow PEP 8 style guide
4. Submit a pull request

## License

MIT License - See LICENSE file

## Roadmap

- [ ] Web UI dashboard
- [ ] Mobile app integration
- [ ] Advanced ML-based intent matching
- [ ] Multi-language support expansion
- [ ] Cloud sync for configurations
- [ ] AI model fine-tuning support

## Support

For issues, questions, or suggestions: [Create an issue](https://github.com/kingcllown/Kingcllown/issues)
