import os
import sys
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from dotenv import load_dotenv

load_dotenv("../.env")

def extract_text_from_pdf(endpoint, key, file_path):
    """
    Extract text from a PDF file using Azure Document Intelligence
    
    Args:
        endpoint (str): Azure Document Intelligence endpoint URL
        key (str): Azure Document Intelligence API key
        file_path (str): Path to the PDF file
    
    Returns:
        str: Extracted text from the PDF
    """
    # Initialize the Document Intelligence client
    document_intelligence_client = DocumentIntelligenceClient(
        endpoint=endpoint, 
        credential=AzureKeyCredential(key)
    )
    
    # Check if file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist")
    
    # Open the PDF file
    with open(file_path, "rb") as f:
        pdf_content = f.read()
    
    # Call the Document Intelligence service
    poller = document_intelligence_client.begin_analyze_document(
        "prebuilt-layout",  # Using the prebuilt Layout model for better structural analysis
        body = pdf_content
    )
    
    # Get the result of the operation
    result = poller.result()
    
    # Extract and concatenate text from all pages with better structure
    extracted_text = ""
    
    # Process paragraphs for better text flow
    for page_idx, page in enumerate(result.pages):
        extracted_text += f"\n--- Page {page_idx + 1} ---\n\n"
        
        # Extract text from paragraphs (maintains better formatting)
        if hasattr(page, 'paragraphs') and page.paragraphs:
            for para in page.paragraphs:
                extracted_text += para.content + "\n\n"
        # Fallback to lines if paragraphs aren't available
        else:
            for line in page.lines:
                extracted_text += line.content + "\n"
        
        # Extract tables if available
        if hasattr(result, 'tables') and result.tables:
            tables_on_page = [table for table in result.tables if table.bounding_regions[0].page_number == page_idx + 1]
            
            if tables_on_page:
                extracted_text += "\n--- Tables ---\n"
                
                for table_idx, table in enumerate(tables_on_page):
                    extracted_text += f"\nTable {table_idx + 1}:\n"
                    
                    # Create a matrix to hold the table data
                    rows = max([cell.row_index for cell in table.cells]) + 1
                    cols = max([cell.column_index for cell in table.cells]) + 1
                    table_matrix = [['' for _ in range(cols)] for _ in range(rows)]
                    
                    # Fill the matrix with cell contents
                    for cell in table.cells:
                        table_matrix[cell.row_index][cell.column_index] = cell.content
                    
                    # Generate text representation of the table
                    for row in table_matrix:
                        extracted_text += ' | '.join(row) + '\n'
                    
                    extracted_text += '\n'
    
    return extracted_text

def main():
    # Azure Document Intelligence configuration
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    # Check if environment variables are set
    if not endpoint or not key:
        print("Error: Azure Document Intelligence endpoint and key must be set as environment variables")
        print("Set AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT and AZURE_DOCUMENT_INTELLIGENCE_KEY")
        sys.exit(1)
    
    # Get PDF file path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python extract_pdf.py <pdf_file_path>")
        sys.exit(1)
    
    pdf_file_path = sys.argv[1]
    
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(endpoint, key, pdf_file_path)        
        # Print extracted text
        # print("Extracted Text:")
        # print("-" * 50)
        # print(extracted_text)
        return extracted_text
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()