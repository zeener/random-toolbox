"""Hash Generator for various hashing algorithms.

This module provides functionality to generate hash values using different
algorithms like MD5, SHA1, SHA256, SHA512, etc.
"""

import hashlib
from typing import Dict, Any, List


class HashGenerator:
    """Generator for creating hash values using various algorithms."""
    
    SUPPORTED_ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'sha3_224': hashlib.sha3_224,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512,
        'blake2b': hashlib.blake2b,
        'blake2s': hashlib.blake2s,
    }
    
    def __init__(self):
        """Initialize the Hash Generator."""
        pass
    
    def generate_hash(self, text: str, algorithm: str = 'sha256') -> Dict[str, Any]:
        """
        Generate hash for the given text using specified algorithm.
        
        Args:
            text (str): Text to hash
            algorithm (str): Hashing algorithm to use
            
        Returns:
            Dict containing hash result and metadata
            
        Raises:
            ValueError: If algorithm is not supported or text is invalid
        """
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        
        algorithm = algorithm.lower().strip()
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}. "
                           f"Supported algorithms: {', '.join(self.SUPPORTED_ALGORITHMS.keys())}")
        
        # Generate hash
        hash_function = self.SUPPORTED_ALGORITHMS[algorithm]
        
        try:
            # Handle blake2 algorithms with default parameters
            if algorithm in ['blake2b', 'blake2s']:
                hasher = hash_function()
            else:
                hasher = hash_function()
            
            hasher.update(text.encode('utf-8'))
            hash_value = hasher.hexdigest()
            
        except Exception as e:
            raise ValueError(f"Error generating hash: {str(e)}")
        
        return {
            "hash": hash_value,
            "algorithm": algorithm,
            "input_text": text,
            "input_length": len(text),
            "hash_length": len(hash_value),
            "encoding": "utf-8"
        }
    
    def generate_multiple_hashes(self, text: str, algorithms: List[str] = None) -> Dict[str, Any]:
        """
        Generate multiple hashes for the same text.
        
        Args:
            text (str): Text to hash
            algorithms (List[str]): List of algorithms to use
            
        Returns:
            Dict containing all hash results and metadata
        """
        if algorithms is None:
            algorithms = ['md5', 'sha1', 'sha256', 'sha512']
        
        results = {}
        
        for algorithm in algorithms:
            try:
                result = self.generate_hash(text, algorithm)
                results[algorithm] = {
                    "hash": result["hash"],
                    "hash_length": result["hash_length"]
                }
            except ValueError as e:
                results[algorithm] = {
                    "error": str(e)
                }
        
        return {
            "hashes": results,
            "input_text": text,
            "input_length": len(text),
            "algorithms_used": algorithms,
            "encoding": "utf-8"
        }
    
    def get_supported_algorithms(self) -> List[str]:
        """
        Get list of supported hashing algorithms.
        
        Returns:
            List of supported algorithm names
        """
        return list(self.SUPPORTED_ALGORITHMS.keys())
    
    def get_algorithm_info(self, algorithm: str) -> Dict[str, Any]:
        """
        Get information about a specific algorithm.
        
        Args:
            algorithm (str): Algorithm name
            
        Returns:
            Dict containing algorithm information
        """
        algorithm = algorithm.lower().strip()
        
        if algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        # Algorithm properties
        algorithm_info = {
            'md5': {'output_size': 32, 'security': 'weak', 'description': 'Fast but cryptographically broken'},
            'sha1': {'output_size': 40, 'security': 'weak', 'description': 'Deprecated for cryptographic use'},
            'sha224': {'output_size': 56, 'security': 'good', 'description': 'SHA-2 family, 224-bit'},
            'sha256': {'output_size': 64, 'security': 'good', 'description': 'SHA-2 family, 256-bit (recommended)'},
            'sha384': {'output_size': 96, 'security': 'good', 'description': 'SHA-2 family, 384-bit'},
            'sha512': {'output_size': 128, 'security': 'good', 'description': 'SHA-2 family, 512-bit'},
            'sha3_224': {'output_size': 56, 'security': 'excellent', 'description': 'SHA-3 family, 224-bit'},
            'sha3_256': {'output_size': 64, 'security': 'excellent', 'description': 'SHA-3 family, 256-bit'},
            'sha3_384': {'output_size': 96, 'security': 'excellent', 'description': 'SHA-3 family, 384-bit'},
            'sha3_512': {'output_size': 128, 'security': 'excellent', 'description': 'SHA-3 family, 512-bit'},
            'blake2b': {'output_size': 128, 'security': 'excellent', 'description': 'BLAKE2b, fast and secure'},
            'blake2s': {'output_size': 64, 'security': 'excellent', 'description': 'BLAKE2s, optimized for 8-32 bit platforms'},
        }
        
        info = algorithm_info.get(algorithm, {})
        
        return {
            "algorithm": algorithm,
            "output_size_hex": info.get('output_size', 0),
            "security_level": info.get('security', 'unknown'),
            "description": info.get('description', 'No description available'),
            "family": self._get_algorithm_family(algorithm)
        }
    
    def _get_algorithm_family(self, algorithm: str) -> str:
        """Get the family/category of the algorithm."""
        if algorithm == 'md5':
            return 'MD5'
        elif algorithm == 'sha1':
            return 'SHA-1'
        elif algorithm.startswith('sha2') or algorithm in ['sha224', 'sha256', 'sha384', 'sha512']:
            return 'SHA-2'
        elif algorithm.startswith('sha3'):
            return 'SHA-3'
        elif algorithm.startswith('blake2'):
            return 'BLAKE2'
        else:
            return 'Other'