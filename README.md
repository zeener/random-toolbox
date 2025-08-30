# Random Toolbox

**A versatile command-line toolkit and API for developers.**

Generate random text, secure passwords, and API keys through both CLI and REST API interfaces. Perfect for testing, development, and secure credential generation.

---

## ✨ Features

- **🖥️ CLI Tools**: Command-line interface for quick data generation
- **🌐 REST API**: HTTP endpoints for application integration  
- **📝 Text Generator**: Lorem ipsum text (words, sentences, paragraphs)
- **🔐 Password Generator**: Cryptographically secure passwords with entropy tracking
- **🔑 API Key Generator**: Multiple formats (hex, base64, base58) with prefix support

---

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/random-toolbox.git
cd random-toolbox
```

2. **Set up virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### CLI Usage

> **Note**: Run CLI commands from the project root directory with the virtual environment activated.

**Method 1 - Python module (recommended):**
```bash
# Generate 5 random words
python -m src.cli.main text --type word --count 5

# Generate 3 sentences  
python -m src.cli.main text --type sentence --count 3

# Generate 2 paragraphs
python -m src.cli.main text --type paragraph --count 2
```

**Method 2 - Direct file execution:**
```bash
# Alternative way to run commands
python src/cli/main.py text --type word --count 5
```

**Generate secure passwords:**
```bash
# Basic 16-character password
python -m src.cli.main password

# Custom password with symbols and entropy info
python -m src.cli.main password --length 20 --symbols --show-entropy

# Exclude ambiguous characters
python -m src.cli.main password --exclude-ambiguous
```

**Generate API keys:**
```bash
# Hex format (default)
python -m src.cli.main apikey

# Base64 with prefix
python -m src.cli.main apikey --format base64 --prefix "sk_"

# Base58 Bitcoin-style
python -m src.cli.main apikey --format base58 --show-entropy
```

### API Usage

**Start the server:**
```bash
source .venv/bin/activate
python src/api/app.py
# Server runs on http://localhost:5600
```

**API Examples:**

**Text Generation:**
```bash
# Generate 3 random words
curl "http://localhost:5600/api/v1/text/random?type=word&count=3"

# Generate a paragraph
curl "http://localhost:5600/api/v1/text/random?type=paragraph"
```

**Password Generation:**
```bash
# Basic password
curl "http://localhost:5600/api/v1/password/generate"

# Custom password with symbols
curl "http://localhost:5600/api/v1/password/generate?length=16&symbols=true&exclude_ambiguous=true"
```

**API Key Generation:**
```bash
# Hex format
curl "http://localhost:5600/api/v1/apikey/generate"

# Base64 with prefix
curl "http://localhost:5600/api/v1/apikey/generate?format=base64&prefix=sk_&length=32"
```

---

## 📡 API Reference

### Base URL
```
http://localhost:5600/api/v1
```

### Response Format
All endpoints return standardized JSON:
```json
{
  "success": true,
  "data": {
    "result": "generated_content",
    "metadata": { "additional_info": "here" }
  },
  "timestamp": "2025-08-30T20:58:30.046507Z"
}
```

### Error Format
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  },
  "timestamp": "2025-08-30T20:58:30.046507Z"
}
```

### Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/health` | GET | Health check | None |
| `/text/random` | GET | Generate text | `type`, `count` |
| `/password/generate` | GET | Generate password | `length`, `uppercase`, `lowercase`, `numbers`, `symbols`, `exclude_ambiguous` |
| `/apikey/generate` | GET | Generate API key | `format`, `length`, `prefix`, `charset` |

---

## 🔧 Development

### Project Structure
```
random-toolbox/
├── src/
│   ├── cli/main.py              # CLI interface
│   ├── api/app.py               # REST API server
│   └── core/generators/         # Core generation logic
├── tests/                       # Comprehensive test suite (102 tests)
├── requirements.txt             # Python dependencies
└── Todo.md                      # Task tracking (synced with Linear)
```

### Security Features
- **Cryptographic Security**: Uses Python `secrets` module
- **Entropy Tracking**: Mathematical strength assessment
- **Input Validation**: Comprehensive parameter checking
- **Multiple Formats**: Support for various encoding schemes

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Development Setup
1. Fork the repository
2. Create a virtual environment: `python3 -m venv .venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Make your changes
5. Test thoroughly
6. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
