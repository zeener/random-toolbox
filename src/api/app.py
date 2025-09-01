from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.generators.text_generator import TextGenerator
from src.core.generators.password_generator import PasswordGenerator
from src.core.generators.apikey_generator import APIKeyGenerator
from src.core.generators.hash_generator import HashGenerator
from src.core.generators.uuid_generator import UUIDGenerator
from src.core.utilities.base64_utility import Base64Utility
from src.core.utilities.url_utility import URLUtility

app = Flask(__name__)

# Global generator instances
text_generator = TextGenerator()
password_generator = PasswordGenerator()
apikey_generator = APIKeyGenerator()
hash_generator = HashGenerator()
uuid_generator = UUIDGenerator()
base64_utility = Base64Utility()
url_utility = URLUtility()

def create_response(data, success=True, error=None):
    """Create standardized JSON response."""
    response = {
        "success": success,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if success:
        response["data"] = data
    else:
        response["error"] = error
        
    return jsonify(response)

@app.errorhandler(400)
def bad_request(error):
    return create_response(None, False, {
        "code": "BAD_REQUEST", 
        "message": "Invalid request parameters"
    }), 400

@app.errorhandler(500)
def internal_error(error):
    return create_response(None, False, {
        "code": "INTERNAL_ERROR",
        "message": "Internal server error"
    }), 500

@app.route('/api/v1/health')
def health_check():
    """Health check endpoint."""
    return create_response({"status": "healthy", "version": "1.0.0"})

@app.route('/api/v1/text/random')
def generate_text():
    """Generate random text endpoint."""
    try:
        content_type = request.args.get('type', 'paragraph')
        count = int(request.args.get('count', 1))
        
        if content_type not in ['word', 'sentence', 'paragraph']:
            return create_response(None, False, {
                "code": "INVALID_TYPE",
                "message": "Type must be one of: word, sentence, paragraph",
                "details": {"provided": content_type, "valid_options": ["word", "sentence", "paragraph"]}
            }), 400
            
        result = text_generator.generate(content_type, count)
        
        return create_response({
            "result": result,
            "metadata": {
                "type": content_type,
                "count": count,
                "is_array": isinstance(result, list)
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "INVALID_PARAMETER",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "GENERATION_ERROR",
            "message": "Failed to generate text"
        }), 500

@app.route('/api/v1/password/generate')
def generate_password():
    """Generate password endpoint."""
    try:
        length = int(request.args.get('length', 16))
        uppercase = request.args.get('uppercase', 'true').lower() == 'true'
        lowercase = request.args.get('lowercase', 'true').lower() == 'true'
        numbers = request.args.get('numbers', 'true').lower() == 'true'
        symbols = request.args.get('symbols', 'false').lower() == 'true'
        exclude_ambiguous = request.args.get('exclude_ambiguous', 'false').lower() == 'true'
        
        result = password_generator.generate_password(
            length=length,
            uppercase=uppercase,
            lowercase=lowercase,
            numbers=numbers,
            symbols=symbols,
            exclude_ambiguous=exclude_ambiguous
        )
        
        return create_response({
            "password": result["password"],
            "metadata": {
                "length": result["length"],
                "entropy_bits": result["entropy_bits"],
                "strength": result["strength"],
                "config": result["config"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "INVALID_PARAMETER",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "GENERATION_ERROR",
            "message": "Failed to generate password"
        }), 500

@app.route('/api/v1/apikey/generate')
def generate_apikey():
    """Generate API key endpoint."""
    try:
        key_format = request.args.get('format', 'hex')
        length = int(request.args.get('length', 32))
        prefix = request.args.get('prefix', '')
        charset = request.args.get('charset', None)
        
        if key_format not in ['hex', 'base64', 'base58', 'custom']:
            return create_response(None, False, {
                "code": "INVALID_FORMAT",
                "message": "Format must be one of: hex, base64, base58, custom",
                "details": {"provided": key_format, "valid_options": ["hex", "base64", "base58", "custom"]}
            }), 400
        
        result = apikey_generator.generate(
            key_format=key_format,
            length=length,
            prefix=prefix,
            charset=charset
        )
        
        return create_response({
            "api_key": result["api_key"],
            "metadata": {
                "format": result["format"],
                "length": result["length"],
                "total_length": result["total_length"],
                "prefix": result["prefix"],
                "entropy_bits": result["entropy_bits"],
                "security_level": result["security_level"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "INVALID_PARAMETER",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "GENERATION_ERROR",
            "message": "Failed to generate API key"
        }), 500

# Hash Generation Endpoints
@app.route('/api/v1/hash/generate')
def generate_hash():
    """Generate hash endpoint."""
    try:
        text = request.args.get('text', '')
        algorithm = request.args.get('algorithm', 'sha256')
        
        if not text:
            return create_response(None, False, {
                "code": "MISSING_TEXT",
                "message": "Text parameter is required"
            }), 400
            
        result = hash_generator.generate_hash(text, algorithm)
        
        return create_response({
            "hash": result["hash"],
            "metadata": {
                "algorithm": result["algorithm"],
                "input_length": result["input_length"],
                "hash_length": result["hash_length"],
                "encoding": result["encoding"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "INVALID_PARAMETER",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "GENERATION_ERROR",
            "message": "Failed to generate hash"
        }), 500

@app.route('/api/v1/hash/algorithms')
def get_hash_algorithms():
    """Get supported hash algorithms."""
    try:
        algorithms = hash_generator.get_supported_algorithms()
        return create_response({
            "algorithms": algorithms,
            "count": len(algorithms)
        })
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to get algorithms"
        }), 500

# UUID Generation Endpoints
@app.route('/api/v1/uuid/generate')
def generate_uuid():
    """Generate UUID endpoint."""
    try:
        version = request.args.get('version', 'v4')
        
        result = uuid_generator.generate_uuid(version)
        
        return create_response({
            "uuid": result["uuid"],
            "metadata": {
                "version": result["version"],
                "type": result["type"],
                "description": result["description"],
                "length": result["length"],
                "format": result["format"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "INVALID_PARAMETER",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "GENERATION_ERROR",
            "message": "Failed to generate UUID"
        }), 500

@app.route('/api/v1/uuid/validate')
def validate_uuid():
    """Validate UUID endpoint."""
    try:
        uuid_string = request.args.get('uuid', '')
        
        if not uuid_string:
            return create_response(None, False, {
                "code": "MISSING_UUID",
                "message": "UUID parameter is required"
            }), 400
            
        result = uuid_generator.validate_uuid(uuid_string)
        
        return create_response(result)
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "VALIDATION_ERROR",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to validate UUID"
        }), 500

# Base64 Utility Endpoints
@app.route('/api/v1/base64/encode', methods=['POST'])
def encode_base64():
    """Encode text to Base64."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return create_response(None, False, {
                "code": "MISSING_TEXT",
                "message": "JSON body with 'text' field is required"
            }), 400
        
        text = data['text']
        result = base64_utility.encode(text)
        
        return create_response({
            "encoded": result["encoded"],
            "metadata": {
                "original_length": result["original_length"],
                "encoded_length": result["encoded_length"],
                "size_increase_percent": result["size_increase_percent"],
                "padding_chars": result["padding_chars"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "ENCODING_ERROR",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to encode Base64"
        }), 500

@app.route('/api/v1/base64/decode', methods=['POST'])
def decode_base64():
    """Decode Base64 text."""
    try:
        data = request.get_json()
        if not data or 'encoded' not in data:
            return create_response(None, False, {
                "code": "MISSING_ENCODED",
                "message": "JSON body with 'encoded' field is required"
            }), 400
        
        encoded = data['encoded']
        result = base64_utility.decode(encoded)
        
        return create_response({
            "decoded": result["decoded"],
            "metadata": {
                "encoded_length": result["encoded_length"],
                "decoded_length": result["decoded_length"],
                "size_decrease_percent": result["size_decrease_percent"],
                "padding_chars": result["padding_chars"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "DECODING_ERROR",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to decode Base64"
        }), 500

# URL Utility Endpoints
@app.route('/api/v1/url/encode', methods=['POST'])
def encode_url():
    """Encode text for URL usage."""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return create_response(None, False, {
                "code": "MISSING_TEXT",
                "message": "JSON body with 'text' field is required"
            }), 400
        
        text = data['text']
        encoding_type = data.get('type', 'standard')
        
        result = url_utility.encode(text, encoding_type)
        
        return create_response({
            "encoded": result["encoded"],
            "metadata": {
                "encoding_type": result["encoding_type"],
                "original_length": result["original_length"],
                "encoded_length": result["encoded_length"],
                "size_increase_percent": result["size_increase_percent"],
                "characters_encoded": result["characters_encoded"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "ENCODING_ERROR",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to encode URL"
        }), 500

@app.route('/api/v1/url/decode', methods=['POST'])
def decode_url():
    """Decode URL-encoded text."""
    try:
        data = request.get_json()
        if not data or 'encoded' not in data:
            return create_response(None, False, {
                "code": "MISSING_ENCODED",
                "message": "JSON body with 'encoded' field is required"
            }), 400
        
        encoded = data['encoded']
        encoding_type = data.get('type', 'auto')
        
        result = url_utility.decode(encoded, encoding_type)
        
        return create_response({
            "decoded": result["decoded"],
            "metadata": {
                "decoding_type": result["decoding_type"],
                "encoded_length": result["encoded_length"],
                "decoded_length": result["decoded_length"],
                "size_decrease_percent": result["size_decrease_percent"],
                "characters_decoded": result["characters_decoded"]
            }
        })
        
    except ValueError as e:
        return create_response(None, False, {
            "code": "DECODING_ERROR",
            "message": str(e)
        }), 400
    except Exception as e:
        return create_response(None, False, {
            "code": "INTERNAL_ERROR",
            "message": "Failed to decode URL"
        }), 500

# API Documentation endpoints

@app.route('/api/swagger.yaml')
def swagger_spec():
    """Serve the Swagger specification file."""
    try:
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to reach the project root, then into docs
        docs_dir = os.path.join(current_dir, '..', '..', 'docs')
        return send_from_directory(docs_dir, 'api-swagger.yaml')
    except Exception as e:
        return jsonify({"error": "Swagger specification not found"}), 404

@app.route('/api')
def api_info():
    """API information endpoint."""
    return create_response({
        "name": "Random Toolbox API",
        "version": "1.0.0",
        "description": "A comprehensive suite of developer tools API",
        "documentation": "/api/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "text_generation": "/api/v1/text/random",
            "password_generation": "/api/v1/password/generate",
            "apikey_generation": "/api/v1/apikey/generate",
            "hash_generation": "/api/v1/hash/generate",
            "uuid_generation": "/api/v1/uuid/generate",
            "base64_encode": "/api/v1/base64/encode",
            "base64_decode": "/api/v1/base64/decode",
            "url_encode": "/api/v1/url/encode",
            "url_decode": "/api/v1/url/decode"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5600)