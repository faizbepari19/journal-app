from abc import ABC, abstractmethod
import os
import ssl
import certifi
import google.generativeai as genai
from typing import List, Dict, Any

# Disable SSL certificate verification for development
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables to disable SSL verification for gRPC and Google AI
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON'] = ''
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Disable gRPC SSL verification
try:
    import grpc
    # Create insecure channel options for gRPC
    os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = ''
    print("🔓 SSL certificate verification disabled for development")
except ImportError:
    print("ℹ️ gRPC not available, basic SSL bypass enabled")

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass
    
    @abstractmethod
    def extract_date_filter(self, query: str) -> Dict[str, Any]:
        """
        Extract date filter information from natural language query
        Returns: {
            'has_date_filter': bool,
            'start_date': str (YYYY-MM-DD) or None,
            'end_date': str (YYYY-MM-DD) or None,
            'filter_type': str ('specific_date', 'date_range', 'relative', None)
        }
        """
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider"""
    
    def __init__(self):
        api_key = os.getenv('GOOGLE_AI_API_KEY')
        if not api_key or api_key == 'your-google-ai-api-key-here':
            raise ValueError("Google AI API key not configured")
        
        genai.configure(api_key=api_key)
        self.text_model = genai.GenerativeModel('gemini-pro')
        self.embedding_model = 'models/embedding-001'
    
    def generate_text(self, prompt: str) -> str:
        try:
            response = self.text_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 1000,
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error generating text with Gemini: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        try:
            # Add timeout and retry logic
            import time
            max_retries = 3
            base_delay = 1
            
            for attempt in range(max_retries):
                try:
                    result = genai.embed_content(
                        model=self.embedding_model,
                        content=text,
                        task_type="retrieval_document"
                    )
                    return result['embedding']
                except Exception as e:
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # Exponential backoff
                        print(f"Attempt {attempt + 1} failed, retrying in {delay}s: {str(e)}")
                        time.sleep(delay)
                        continue
                    else:
                        raise e
                        
        except Exception as e:
            # Return a dummy embedding for development when AI fails
            print(f"Warning: AI embedding failed: {str(e)}")
            # Return a random embedding of the right size for development
            import random
            return [random.random() for _ in range(768)]
    
    def extract_date_filter(self, query: str) -> Dict[str, Any]:
        """Extract date filter from query using Gemini AI"""
        try:
            from datetime import datetime, date
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            prompt = f"""Analyze this user query and extract any date/time filtering information. Today's date is {current_date}.

User Query: "{query}"

If the query contains any date or time references, extract them and return ONLY a JSON object with these fields:
{{
    "has_date_filter": true/false,
    "start_date": "YYYY-MM-DD" (or null),
    "end_date": "YYYY-MM-DD" (or null),
    "filter_type": "specific_date|date_range|relative" (or null),
    "explanation": "brief explanation of the date filter found"
}}

Examples:
- "current month" → {{"has_date_filter": true, "start_date": "{current_year}-{current_month:02d}-01", "end_date": "{current_year}-{current_month:02d}-30", "filter_type": "relative", "explanation": "Current month filter"}}
- "last week" → {{"has_date_filter": true, "start_date": "calculated-start", "end_date": "calculated-end", "filter_type": "relative", "explanation": "Previous week filter"}}
- "August 2025" → {{"has_date_filter": true, "start_date": "2025-08-01", "end_date": "2025-08-31", "filter_type": "date_range", "explanation": "Specific month filter"}}
- "no date reference" → {{"has_date_filter": false, "start_date": null, "end_date": null, "filter_type": null, "explanation": "No date filtering needed"}}

Return ONLY the JSON object, no other text:"""

            response = self.text_model.generate_content(
                prompt,
                generation_config={
                    'temperature': 0.1,  # Low temperature for consistent parsing
                    'max_output_tokens': 300,
                }
            )
            
            # Parse the JSON response
            import json
            response_text = response.text.strip()
            
            # Clean up the response to extract just the JSON
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            try:
                date_filter = json.loads(response_text)
                print(f"📅 LLM extracted date filter: {date_filter}")
                return date_filter
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse LLM date filter response: {response_text}")
                return {
                    'has_date_filter': False,
                    'start_date': None,
                    'end_date': None,
                    'filter_type': None,
                    'explanation': 'Failed to parse date filter'
                }
                
        except Exception as e:
            print(f"Error extracting date filter with Gemini: {str(e)}")
            return {
                'has_date_filter': False,
                'start_date': None,
                'end_date': None,
                'filter_type': None,
                'explanation': f'Error: {str(e)}'
            }

class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider (placeholder implementation)"""
    
    def __init__(self):
        # Initialize OpenAI client when implemented
        self.api_key = os.getenv('OPENAI_API_KEY')
    
    def generate_text(self, prompt: str) -> str:
        # TODO: Implement OpenAI text generation
        raise NotImplementedError("OpenAI provider not implemented yet")
    
    def generate_embedding(self, text: str) -> List[float]:
        # TODO: Implement OpenAI embedding
        raise NotImplementedError("OpenAI provider not implemented yet")
    
    def extract_date_filter(self, query: str) -> Dict[str, Any]:
        # TODO: Implement OpenAI date extraction
        return {
            'has_date_filter': False,
            'start_date': None,
            'end_date': None,
            'filter_type': None,
            'explanation': 'OpenAI provider not implemented'
        }

class GroqProvider(LLMProvider):
    """Groq LLM provider"""
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key or api_key == 'your-groq-api-key-here':
            print("Warning: No valid Groq API key found. Using fallback mode.")
            self.client = None
        else:
            try:
                from groq import Groq
                import httpx
                
                # Create a custom HTTP client that bypasses SSL verification
                transport = httpx.HTTPTransport(verify=False)
                http_client = httpx.Client(
                    transport=transport,
                    verify=False,
                    timeout=30.0,
                    limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
                )
                
                self.client = Groq(
                    api_key=api_key,
                    http_client=http_client
                )
                print("✅ Groq client initialized with SSL bypass")
            except Exception as e:
                print(f"Warning: Could not initialize Groq client: {e}")
                self.client = None
    
    def generate_text(self, prompt: str) -> str:
        if not self.client:
            # Fallback response for development
            return f"[FALLBACK] This is a simulated AI response to: '{prompt[:100]}...'. Groq API is currently unavailable."
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Updated to current supported model
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                timeout=30
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq API error: {e}")
            # Return fallback response instead of failing
            return f"[FALLBACK] AI service temporarily unavailable. Your question was: '{prompt[:100]}...'"
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Groq doesn't provide embedding models, so we'll use a simple
        hash-based approach for development or fall back to local embeddings
        """
        try:
            # Simple hash-based embedding for development
            import hashlib
            import struct
            
            # Create a consistent hash of the text
            hash_object = hashlib.md5(text.encode())
            hash_bytes = hash_object.digest()
            
            # Convert to a 768-dimensional vector (standard embedding size)
            embedding = []
            for i in range(768):
                # Use the hash bytes cyclically to create 768 dimensions
                byte_index = i % len(hash_bytes)
                value = struct.unpack('B', hash_bytes[byte_index:byte_index+1])[0]
                # Normalize to [-1, 1] range
                normalized_value = (value / 255.0) * 2 - 1
                embedding.append(normalized_value)
            
            print(f"Generated hash-based embedding with {len(embedding)} dimensions")
            return embedding
        except Exception as e:
            print(f"Warning: Could not generate hash-based embedding: {str(e)}")
            # Return random embedding as last resort
            import random
            return [random.random() * 2 - 1 for _ in range(768)]
    
    def extract_date_filter(self, query: str) -> Dict[str, Any]:
        """Extract date filter from query using Groq AI"""
        if not self.client:
            return {
                'has_date_filter': False,
                'start_date': None,
                'end_date': None,
                'filter_type': None,
                'explanation': 'Groq API unavailable'
            }
        
        try:
            from datetime import datetime
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            prompt = f"""Analyze this user query and extract date/time filtering information. Today's date is {current_date}.

Query: "{query}"

Return ONLY a JSON object with these fields:
{{
    "has_date_filter": true/false,
    "start_date": "YYYY-MM-DD" or null,
    "end_date": "YYYY-MM-DD" or null,
    "filter_type": "specific_date|date_range|relative" or null,
    "explanation": "brief explanation"
}}

Examples:
- "current month" → {{"has_date_filter": true, "start_date": "{current_year}-{current_month:02d}-01", "end_date": "{current_year}-{current_month:02d}-30", "filter_type": "relative", "explanation": "Current month filter"}}
- "last week" → calculate previous week dates
- "August 2025" → {{"has_date_filter": true, "start_date": "2025-08-01", "end_date": "2025-08-31", "filter_type": "date_range", "explanation": "Specific month"}}
- No date → {{"has_date_filter": false, "start_date": null, "end_date": null, "filter_type": null, "explanation": "No date filter"}}

Return ONLY the JSON, no other text:"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=200,
                timeout=15
            )
            
            # Parse the JSON response
            import json
            response_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            try:
                date_filter = json.loads(response_text)
                print(f"📅 Groq extracted date filter: {date_filter}")
                return date_filter
            except json.JSONDecodeError as e:
                print(f"⚠️ Failed to parse Groq date filter: {response_text}")
                return {
                    'has_date_filter': False,
                    'start_date': None,
                    'end_date': None,
                    'filter_type': None,
                    'explanation': 'Failed to parse'
                }
                
        except Exception as e:
            print(f"Error extracting date filter with Groq: {str(e)}")
            return {
                'has_date_filter': False,
                'start_date': None,
                'end_date': None,
                'filter_type': None,
                'explanation': f'Error: {str(e)}'
            }

class LLMFactory:
    """Factory class for creating LLM providers"""
    
    _providers = {
        'gemini': GeminiProvider,
        'openai': OpenAIProvider,
        'groq': GroqProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str = None) -> LLMProvider:
        """Create an LLM provider instance"""
        if provider_name is None:
            provider_name = os.getenv('LLM_PROVIDER', 'groq')  # Default to groq
        
        provider_name = provider_name.lower()
        
        if provider_name not in cls._providers:
            raise ValueError(f"Unknown LLM provider: {provider_name}. Available providers: {list(cls._providers.keys())}")
        
        return cls._providers[provider_name]()

# Convenience instance for easy import
llm_service = LLMFactory.create_provider()