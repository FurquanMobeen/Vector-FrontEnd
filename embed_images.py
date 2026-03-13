import sys
from pathlib import Path
import chromadb
import json
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

def main():
    # Configuration
    image_folder = "./data"
    embedded_data = "./embedded_data"
    model_name = "openai/clip-vit-base-patch32"
    batch_size = 32

    # Check if folder exists
    if not Path(image_folder).exists():
        print(f"ERROR: Folder not found: {image_folder}")
        sys.exit(1)
        
    # Check if folder is empty
    if not any(Path(image_folder).iterdir()):
        print(f"ERROR: Folder is empty, add image data and rerun.")
        sys.exit(1)

    # Create index directory
    embed_path = Path(embedded_data)
    embed_path.mkdir(exist_ok=True)

    # Initialize CLIP model
    print(f"Loading CLIP model: {model_name}...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    model = CLIPModel.from_pretrained(model_name).to(device)
    processor = CLIPProcessor.from_pretrained(model_name)
    model.eval()

    # Initialize ChromaDB
    print("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=str(embed_path))
    collection = client.get_or_create_collection(
        name="images",
        metadata={"hnsw:space": "cosine"}
    )

    # Get all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    image_files = [
        f for f in Path(image_folder).rglob('*')
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_files:
        print(f"ERROR: No image files found in {image_folder}")
        sys.exit(1)

    image_paths = []
    image_metadata = {}

    # Process images in batches
    for i, image_file in enumerate(image_files):
        try:
            # Load and process image
            image = Image.open(image_file).convert('RGB')
            
            # Generate embedding
            inputs = processor(images=image, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = model.get_image_features(**inputs)
                
                if isinstance(outputs, torch.Tensor):
                    image_features = outputs
                else:
                    image_features = outputs.pooler_output if hasattr(outputs, 'pooler_output') else outputs

                # Normalize
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            embedding = image_features.cpu().numpy().astype('float32').reshape(-1).tolist()
            
            # Prepare metadata
            # Use POSIX path (forward slashes) for cross-platform compatibility
            image_id = image_file.as_posix()
            filename = image_file.stem.replace('_', ' ').title()
            
            # Add to ChromaDB
            collection.add(
                ids=[image_id],
                embeddings=[embedding],
                metadatas=[{
                    "title": filename,
                    "description": f"Image: {image_file.name}"
                }],
                documents=[image_file.name]
            )
            
            image_paths.append(image_id)
            image_metadata[image_id] = {
                "title": filename,
                "description": f"Image: {image_file.name}"
            }
            
            # Progress update
            percentage = ((i + 1) / len(image_files)) * 100
            print(f"[{percentage:5.1f}%] Indexed: {image_file.name}")

        except Exception as e:
            print(f"[ERROR] Failed to process {image_file.name}: {str(e)}")
            continue

    # Save metadata
    print("-" * 60)
    metadata = {
        "image_paths": image_paths,
        "image_metadata": image_metadata,
        "num_images": len(image_paths),
        "model": model_name,
        "vector_store": "chromadb"
    }
    
    metadata_path = embed_path / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Metadata saved in {embedded_data}")

if __name__ == "__main__":
    main()
