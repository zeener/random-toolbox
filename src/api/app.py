from flask import Flask, jsonify, request
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from src.core.generators.text_generator import TextGenerator
from src.core.generators.password_generator import PasswordGenerator
from src.core.generators.apikey_generator import APIKeyGenerator

app = Flask(__name__)

# Global generator instances
text_generator = TextGenerator()
password_generator = PasswordGenerator()
apikey_generator = APIKeyGenerator()

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5600)