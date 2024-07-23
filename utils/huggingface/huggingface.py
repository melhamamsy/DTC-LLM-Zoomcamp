import os

def setup_hf_cache_dir(path):
    os.environ['HF_HOME'] = path
    print(f"HuggingFace cache directory has been set to: {path}")