import os
import sys
from dotenv import load_dotenv

load_dotenv("../.env")

def main():
    # Azure Document Intelligence configuration
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    print(endpoint)
    print(key)

if __name__ == "__main__":
    main()
