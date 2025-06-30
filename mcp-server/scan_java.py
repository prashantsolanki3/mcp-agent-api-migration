import os

def scan_java_files(input_dir: str) -> str:
    java_sources = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    java_sources.append(f.read())
    return '\n\n'.join(java_sources)
