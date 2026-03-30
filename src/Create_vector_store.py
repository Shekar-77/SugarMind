import uuid
import numpy as np
import os
import io
import base64
from pathlib import Path
from PIL import Image
import easyocr

# Docling Imports
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.document import TableItem, PictureItem, TextItem, SectionHeaderItem

# Vector Store & Embedding Imports
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

# --- 1. Initialize Models ---
# Text & Table Model (384 dimensions)
text_model = SentenceTransformer('all-MiniLM-L6-v2')

# Multi-modal Model for Images (512 dimensions)
clip_model = SentenceTransformer('clip-ViT-B-32')

# OCR Reader
reader = easyocr.Reader(['en'])

# Qdrant Client
client = QdrantClient(":memory:") # Use "localhost" if running via Docker
COLLECTION_NAME = "multimodal_docs"

# --- 2. Helper Functions ---
def img_to_base64(pil_img):
    """Converts a PIL image to a base64 string for storage/display."""
    buffered = io.BytesIO()
    pil_img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# --- 3. Configure Docling ---
pipeline_options = PdfPipelineOptions(do_ocr=True, generate_picture_images=True)
pipeline_options.table_structure_options.do_table_structure = True

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        InputFormat.DOCX: WordFormatOption(pipeline_options=pipeline_options),
    }
)

# --- 4. Initialize Qdrant Collection ---
if not client.collection_exists(COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config={
            "text_vec": VectorParams(size=384, distance=Distance.COSINE),
            "image_vec": VectorParams(size=512, distance=Distance.COSINE),
            "table_content": VectorParams(size=384, distance=Distance.COSINE),
        }
    )

# --- 5. Main Processing Loop ---
def index_documents(folder_path):
    docs_path = Path(folder_path)
    
    for file in docs_path.iterdir():
        if file.suffix.lower() not in [".pdf", ".docx"]: continue
        print(f"🚀 Indexing: {file.name}")

        try:
            result = converter.convert(file)
            points = []
            current_section = "General"

            for element, _level in result.document.iterate_items():
                
                # A. Handle Sections
                if isinstance(element, SectionHeaderItem):
                    current_section = element.text.strip()

                # B. Handle Tables
                elif isinstance(element, TableItem):
                    table_md = element.export_to_markdown()
                    if table_md.strip():
                        t_vec = text_model.encode(f"[{current_section}] {table_md}").tolist()
                        points.append(PointStruct(
                            id=str(uuid.uuid4()),
                            vector={"table_content": t_vec},
                            payload={"content": table_md, "type": "table", "source": file.name, "section": current_section}
                        ))

                # C. Handle Images (OCR + CLIP)
                elif isinstance(element, PictureItem):
                    pil_image = element.get_image(result.document)
                    if pil_image:
                        # CLIP Embedding (Visual)
                        i_vec = clip_model.encode(pil_image).tolist()
                        
                        # OCR Processing (EasyOCR)
                        img_array = np.array(pil_image.convert('RGB'))
                        ocr_text = " ".join(reader.readtext(img_array, detail=0)).strip()
                        
                        # Text Embedding (Semantic OCR)
                        t_vec = text_model.encode(ocr_text or "image/diagram").tolist()

                        points.append(PointStruct(
                            id=str(uuid.uuid4()),
                            vector={"image_vec": i_vec, "text_vec": t_vec},
                            payload={
                                "content": ocr_text, 
                                "type": "image", 
                                "source": file.name, 
                                "base64": img_to_base64(pil_image)
                            }
                        ))

                # D. Handle Standard Text
                elif isinstance(element, TextItem):
                    txt = element.text.strip()
                    if len(txt) > 10:
                        t_vec = text_model.encode(f"[{current_section}] {txt}").tolist()
                        points.append(PointStruct(
                            id=str(uuid.uuid4()),
                            vector={"text_vec": t_vec},
                            payload={"content": txt, "type": "text", "source": file.name, "section": current_section}
                        ))

            if points:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                print(f"✅ Indexed {len(points)} elements from {file.name}")

        except Exception as e:
            print(f"❌ Failed {file.name}: {e}")

# Run it
# index_documents("/content/documents")