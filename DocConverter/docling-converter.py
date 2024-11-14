# it use models to parse heavy processing
from docling.document_converter import DocumentConverter

source = "https://arxiv.org/pdf/2408.09869" 
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_markdown())  
