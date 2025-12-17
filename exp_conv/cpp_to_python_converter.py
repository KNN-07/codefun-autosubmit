"""
C++ to Python converter using OpenAI-compatible API
"""

import os
import json
import requests
import argparse
from pathlib import Path
from typing import Optional, Dict, List
import time
import hashlib
import concurrent.futures
import threading
from datetime import datetime, timedelta

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = None

class CppToPythonConverter:
    def __init__(self, api_url: str, api_key: str, model: str = "gpt-3.5-turbo", max_workers: int = 4, rpm_limit: int = 20):
        self.api_url = api_url
        # Support multiple API keys (comma-separated)
        self.api_keys = [key.strip() for key in api_key.split(',')] if ',' in api_key else [api_key]
        self.current_key_index = 0
        self.model = model
        self.converted_files_cache = set()
        self.conversion_count = 0
        self.max_workers = max_workers
        self.rpm_limit = rpm_limit
        # Track requests per API key
        self.request_times = {i: [] for i in range(len(self.api_keys))}
        self.rate_limit_lock = threading.Lock()
        self.conversion_lock = threading.Lock()
        self.key_lock = threading.Lock()
        
    def get_file_hash(self, file_path: Path) -> str:
        """Get MD5 hash of file content for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""
    
    def load_conversion_cache(self, cache_file: Path):
        """Load previously converted files cache"""
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.converted_files_cache = set(cache_data.get('converted_files', []))
                    print(f"Loaded cache with {len(self.converted_files_cache)} previously converted files")
            except Exception as e:
                print(f"Error loading cache: {e}")
                self.converted_files_cache = set()
    
    def save_conversion_cache(self, cache_file: Path):
        """Save conversion cache"""
        try:
            cache_data = {
                'converted_files': list(self.converted_files_cache),
                'timestamp': time.time()
            }
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def find_cpp_files(self, source_dir: Path) -> List[Path]:
        """Find all C++ files in source directory"""
        cpp_extensions = {'.cpp', '.cc', '.cxx', '.c++', '.h', '.hpp', '.hxx', '.h++'}
        cpp_files = []
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in cpp_extensions:
                    cpp_files.append(file_path)
        
        return sorted(cpp_files)
    
    def get_next_api_key(self):
        """Get the next API key in rotation"""
        with self.key_lock:
            key = self.api_keys[self.current_key_index]
            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
            return key
    
    def wait_for_rate_limit(self):
        """Wait if we're approaching the rate limit for any API key"""
        with self.rate_limit_lock:
            now = datetime.now()
            minute_ago = now - timedelta(minutes=1)
            
            # Find the key with the fewest recent requests
            best_key_index = 0
            min_requests = float('inf')
            
            for key_index, times in self.request_times.items():
                # Remove requests older than 1 minute
                recent_times = [t for t in times if t > minute_ago]
                self.request_times[key_index] = recent_times
                
                if len(recent_times) < min_requests:
                    min_requests = len(recent_times)
                    best_key_index = key_index
            
            # If all keys are at limit, wait for the oldest one to expire
            if min_requests >= self.rpm_limit:
                oldest_time = min([min(times) for times in self.request_times.values() if times])
                wait_time = 60 - (now - oldest_time).total_seconds() + 1
                if wait_time > 0:
                    print(f"All API keys at rate limit. Waiting {wait_time:.1f} seconds...")
                    time.sleep(wait_time)
                    # Clean up again after waiting
                    for key_index in self.request_times:
                        self.request_times[key_index] = [t for t in self.request_times[key_index] if t > datetime.now() - timedelta(minutes=1)]
            
            # Record this request for the best key
            self.request_times[best_key_index].append(datetime.now())
            return best_key_index
    
    def convert_cpp_to_python(self, cpp_content: str, filename: str) -> Optional[str]:
        """Convert C++ code to Python using OpenAI API with rate limiting and key rotation"""
        # Wait for rate limit and get the best API key
        key_index = self.wait_for_rate_limit()
        api_key = self.api_keys[key_index]
        
        prompt = f"""Convert the following C++ code to equivalent Python code. 
Maintain the same functionality and logic. Use appropriate Python libraries when needed.
IMPORTANT: Convert all file I/O operations to stdio (stdin/stdout) operations.
Replace file reading with sys.stdin, file writing with sys.stdout.
Use sys.stdin.read() for reading all input, sys.stdout.write() for writing strings.
Import sys at the beginning. Replace cin/cout with sys.stdin/sys.stdout operations.
For multiple inputs, use sys.stdin.read().split() and parse as needed.
Add comments explaining the conversion where necessary.

C++ filename: {filename}

C++ Code:
```cpp
{cpp_content}
```

Please provide only the Python code without any additional explanation or markdown formatting."""

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert programmer who converts C++ code to Python. Always provide clean, functional Python code that maintains the original logic.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.1,
            'max_tokens': 4000
        }
        
        try:
            response = requests.post(
                f"{self.api_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                python_code = result['choices'][0]['message']['content'].strip()
                
                # Clean up the response - remove markdown code blocks if present
                if python_code.startswith('```python'):
                    python_code = python_code[9:]
                if python_code.startswith('```'):
                    python_code = python_code[3:]
                if python_code.endswith('```'):
                    python_code = python_code[:-3]
                
                return python_code.strip()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error converting {filename}: {e}")
            return None
    
    def get_python_filename(self, cpp_path: Path, source_dir: Path, target_dir: Path) -> Path:
        """Generate corresponding Python filename"""
        relative_path = cpp_path.relative_to(source_dir)
        
        # Change extension to .py
        if relative_path.suffix.lower() in {'.h', '.hpp', '.hxx', '.h++'}:
            # For header files, create a Python module
            python_name = relative_path.stem + '.py'
        else:
            python_name = relative_path.stem + '.py'
        
        # Create target path maintaining directory structure
        target_path = target_dir / relative_path.parent / python_name
        return target_path
    
    def convert_single_file(self, cpp_file: Path, python_file: Path, cache_key: str, source_path: Path) -> bool:
        """Convert a single C++ file to Python (thread-safe)"""
        try:
            # Read C++ file
            with open(cpp_file, 'r', encoding='utf-8') as f:
                cpp_content = f.read()
            
            if not cpp_content.strip():
                print(f"  Skipping empty file: {cpp_file}")
                return False
            
            # Convert to Python
            python_content = self.convert_cpp_to_python(cpp_content, cpp_file.name)
            
            if python_content is None:
                print(f"  Failed to convert: {cpp_file}")
                return False
            
            # Create target directory
            python_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write Python file
            with open(python_file, 'w', encoding='utf-8') as f:
                f.write(f"# Converted from {cpp_file.name}\n")
                f.write(f"# Original path: {cpp_file}\n")
                f.write(f"# Conversion date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(python_content)
            
            # Update cache and count (thread-safe)
            with self.conversion_lock:
                self.converted_files_cache.add(cache_key)
                self.conversion_count += 1
            
            print(f"  ✓ Converted: {cpp_file.name} -> {python_file.name}")
            return True
            
        except Exception as e:
            print(f"  Error processing {cpp_file}: {e}")
            return False

    def convert_folder(self, source_dir: str, target_dir: str, cache_file: str = ".conversion_cache.json"):
        """Convert all C++ files in source folder to Python in target folder with parallel processing"""
        source_path = Path(source_dir)
        target_path = Path(target_dir)
        cache_path = Path(cache_file)
        
        if not source_path.exists():
            print(f"Source directory {source_dir} does not exist")
            return
        
        # Load conversion cache
        self.load_conversion_cache(cache_path)
        
        # Find all C++ files
        cpp_files = self.find_cpp_files(source_path)
        print(f"Found {len(cpp_files)} C++ files to process")
        
        # Filter out already converted files (by checking if target exists)
        files_to_convert = []
        for cpp_file in cpp_files:
            python_file = self.get_python_filename(cpp_file, source_path, target_path)
            file_hash = self.get_file_hash(cpp_file)
            cache_key = f"{str(cpp_file)}:{file_hash}"
            
            if cache_key not in self.converted_files_cache or not python_file.exists():
                files_to_convert.append((cpp_file, python_file, cache_key))
        
        print(f"Files to convert: {len(files_to_convert)}")
        print(f"Files already converted (cached): {len(cpp_files) - len(files_to_convert)}")
        print(f"Using {self.max_workers} parallel workers with {self.rpm_limit} RPM limit")
        
        if not files_to_convert:
            print("No new files to convert!")
            return
        
        # Create target directories
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Convert files in parallel
        successful_conversions = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all conversion tasks
            future_to_file = {
                executor.submit(self.convert_single_file, cpp_file, python_file, cache_key, source_path): (cpp_file, cache_key)
                for cpp_file, python_file, cache_key in files_to_convert
            }
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_file):
                cpp_file, cache_key = future_to_file[future]
                try:
                    success = future.result()
                    if success:
                        successful_conversions += 1
                        
                        # Save cache periodically
                        if successful_conversions % 5 == 0:
                            self.save_conversion_cache(cache_path)
                            
                except Exception as e:
                    print(f"  Error in parallel conversion of {cpp_file}: {e}")
        
        # Save final cache
        self.save_conversion_cache(cache_path)
        
        print(f"\n✓ Conversion complete!")
        print(f"  Total files converted: {self.conversion_count}")
        print(f"  Successful conversions: {successful_conversions}")
        print(f"  Python files created in: {target_path}")

def load_env_config():
    """Load configuration from .env file if it exists"""
    if not DOTENV_AVAILABLE:
        return None
    
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded configuration from {env_path}")
        
        # Support multiple API keys (comma-separated)
        api_key = os.getenv('LLM_API_KEY', 'ollama')
        if ',' in api_key:
            print(f"Multiple API keys detected: {len([k.strip() for k in api_key.split(',')])} keys")
        
        return {
            'api_url': os.getenv('LLM_API_URL'),
            'api_key': api_key,
            'model': os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
        }
    return None

def main():
    # Try to load .env configuration first
    env_config = load_env_config()
    
    parser = argparse.ArgumentParser(description='Convert C++ files to Python using OpenAI-compatible API')
    parser.add_argument('source', help='Source C++ directory')
    parser.add_argument('target', help='Target Python directory')
    parser.add_argument('--workers', type=int, default=4, help='Number of parallel workers (default: 4)')
    parser.add_argument('--rpm', type=int, default=20, help='Rate limit in requests per minute (default: 20)')
    
    # Make API arguments optional if .env config exists
    if env_config:
        parser.add_argument('--api-url', help=f'OpenAI-compatible API URL (default from .env: {env_config["api_url"]})')
        parser.add_argument('--api-key', default=env_config['api_key'], help=f'API key (default from .env). Use commas for multiple keys: key1,key2,key3')
        parser.add_argument('--model', default=env_config['model'], help=f'Model name (default from .env: {env_config["model"]})')
    else:
        parser.add_argument('--api-url', required=True, help='OpenAI-compatible API URL (e.g., http://localhost:11434/v1)')
        parser.add_argument('--api-key', default='ollama', help='API key (default: ollama). For multiple keys, use: key1,key2,key3')
        parser.add_argument('--model', default='gpt-3.5-turbo', help='Model name (default: gpt-3.5-turbo)')
    
    args = parser.parse_args()
    
    # Use .env config as fallback for missing arguments
    if env_config:
        api_url = args.api_url or env_config['api_url']
        api_key = args.api_key or env_config['api_key']
        model = args.model or env_config['model']
    else:
        api_url = args.api_url
        api_key = args.api_key
        model = args.model
    
    if not api_url:
        parser.error("API URL is required. Provide it via --api-url argument or LLM_API_URL in .env file")
    
    converter = CppToPythonConverter(
        api_url=api_url,
        api_key=api_key,
        model=model,
        max_workers=args.workers,
        rpm_limit=args.rpm
    )
    
    converter.convert_folder(args.source, args.target)

if __name__ == '__main__':
    main()