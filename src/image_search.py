import numpy as np
import torch
import chromadb
import json
from pathlib import Path
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from typing import List, Tuple, Optional

class ImageSearchApp:

    def __init__(self, embedded_data: str = "embedded_data", model_name: str = "openai/clip-vit-base-patch32"):
        self.embedded_data = Path(embedded_data)
        self.model_name = model_name
        self.collection = None
        self.metadata = None
        self.image_paths = None
        self.image_metadata = None
        self.model = None
        self.processor = None
        self.device = None

        # Load everything on initialization
        self._load_index()
        self._load_model()

    def _load_index(self):
        metadata_path = self.embedded_data / "metadata.json"

        if not metadata_path.exists():
            raise FileNotFoundError(
                f"ChromaDB metadata not found at {metadata_path}\n"
                "Please run 'python embed_images.py' first to generate the index."
            )

        print(f"Loading ChromaDB collection from {self.embedded_data}...")

        # Initialize Chroma client with persistent storage
        client = chromadb.PersistentClient(path=str(self.embedded_data))
        self.collection = client.get_or_create_collection(
            name="images",
            metadata={"hnsw:space": "cosine"}
        )

        with open(metadata_path, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        self.image_paths = self.metadata["image_paths"]
        self.image_metadata = self.metadata.get("image_metadata", {})

        # Convert paths to absolute using POSIX format for cross-platform compatibility
        self.image_paths = [Path(p).resolve().as_posix() for p in self.image_paths]
        self.image_metadata = {Path(k).resolve().as_posix(): v for k, v in self.image_metadata.items()}

        # If image_metadata is empty, create default metadata for all images
        if not self.image_metadata:
            self.image_metadata = {}
            for path in self.image_paths:
                filename = Path(path).stem.replace('_', ' ').title()
                self.image_metadata[path] = {
                    "title": filename,
                    "description": f"Image: {Path(path).name}"
                }

        print(f"Loaded collection with {self.collection.count()} images")

    def _load_model(self):
        print(f"Loading CLIP model: {self.model_name}")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")

        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        self.model.eval()

        print("Model loaded successfully!")

    def embed_image(self, image: Image.Image) -> np.ndarray:
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Process image
        inputs = self.processor(images=image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate embedding
        with torch.no_grad():
            outputs = self.model.get_image_features(**inputs)

            # Handle different transformers versions
            if isinstance(outputs, torch.Tensor):
                image_features = outputs
            elif hasattr(outputs, 'pooler_output'):
                image_features = outputs.pooler_output
            elif hasattr(outputs, 'image_embeds'):
                image_features = outputs.image_embeds
            elif hasattr(outputs, 'last_hidden_state'):
                image_features = outputs.last_hidden_state[:, 0]
            else:
                raise ValueError(f"Unexpected output type: {type(outputs)}")

        # Normalize
        image_features = image_features / image_features.norm(dim=-1, keepdim=True)

        arr = image_features.cpu().numpy().astype('float32')
        return arr.reshape(-1)

    def search(self, query_image: Image.Image, k: int = 5) -> List[Tuple[str, float]]:
        if query_image is None:
            return []

        # Generate query embedding
        query_embedding = self.embed_image(query_image).tolist()

        # Search in ChromaDB collection
        results = self.collection.query(query_embeddings=[query_embedding], n_results=k)

        # Build results with distances
        result_list = []
        if results['ids'] and len(results['ids']) > 0:
            for i, img_id in enumerate(results['ids'][0]):
                # Resolve to absolute path using POSIX format
                img_path = Path(img_id).resolve().as_posix()
                # ChromaDB stores distances as cosine distances
                distance = results['distances'][0][i] if results['distances'] else 0
                result_list.append((img_path, float(distance)))

        return result_list

    def search_and_format(self, query_image: Optional[Image.Image], num_results: int) -> List:
        if query_image is None:
            return []

        # Perform search
        results = self.search(query_image, k=num_results)

        if not results:
            return []

        # Format for Streamlit gallery
        gallery_images = []
        for i, (img_path, similarity) in enumerate(results):
            # Get metadata for this image
            metadata = self.image_metadata.get(img_path, {})
            title = metadata.get("title", Path(img_path).stem.replace('_', ' ').title())
            description = metadata.get("description", "")

            caption = f"#{i+1}: {title}\n{description}\nSimilarity: {similarity:.4f}"
            gallery_images.append((img_path, caption))

        return gallery_images

    def text_search_and_format(self, query_text: str, num_results: int) -> List:
        if not query_text:
            return []

        try:
            # Generate text embedding using CLIP
            inputs = self.processor(text=[query_text], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.get_text_features(**inputs)

                # Handle different output types
                if isinstance(outputs, torch.Tensor):
                    text_features = outputs
                elif hasattr(outputs, 'pooler_output'):
                    text_features = outputs.pooler_output
                elif hasattr(outputs, 'last_hidden_state'):
                    text_features = outputs.last_hidden_state[:, 0]
                else:
                    text_features = outputs

                # Normalize
                text_features = text_features / text_features.norm(dim=-1, keepdim=True)

            # Convert to numpy and flatten to 1D
            embedding_array = text_features.cpu().numpy().astype('float32')
            query_embedding = embedding_array.reshape(-1).tolist()

            # Search in ChromaDB
            results = self.collection.query(query_embeddings=[query_embedding], n_results=num_results)

            # Build results with distances
            gallery_images = []
            if results['ids'] and len(results['ids']) > 0:
                for i, img_id in enumerate(results['ids'][0]):
                    img_path = Path(img_id).resolve().as_posix()
                    distance = results['distances'][0][i] if results['distances'] else 0
                    metadata = self.image_metadata.get(img_path, {})
                    title = metadata.get("title", Path(img_path).stem.replace('_', ' ').title())
                    description = metadata.get("description", "")

                    caption = f"#{i+1}: {title}\n{description}\nSimilarity: {distance:.4f}"
                    gallery_images.append((img_path, caption))

            return gallery_images

        except Exception as e:
            print(f"Error in text search: {str(e)}")
            return []
    
    def get_all_images(self) -> List[Tuple[str, str, str]]:
        results = []
        for img_path in self.image_paths:
            metadata = self.image_metadata.get(img_path, {})
            title = metadata.get("title", Path(img_path).stem.replace('_', ' ').title())
            description = metadata.get("description", "")
            results.append((img_path, title, description))
        return results

    def add_to_database(self, query_image: Optional[Image.Image], title: str = "", description: str = "", save_dir: str = "uploaded_images") -> str:
        if query_image is None:
            return "Please upload an image first!"

        try:
            # Create save directory if it doesn't exist
            save_path = Path(save_dir)
            save_path.mkdir(exist_ok=True)

            # Generate a unique filename
            import time
            timestamp = int(time.time() * 1000)
            filename = f"uploaded_{timestamp}.jpg"
            full_path = save_path / filename

            # Save the image
            query_image.save(full_path, format='JPEG')

            # Generate embedding
            embedding = self.embed_image(query_image)
            # ensure 1D list
            embedding = embedding.reshape(-1)

            # Generate unique ID for this image
            # Use POSIX path (forward slashes) for cross-platform compatibility
            image_id = full_path.as_posix()
            
            # Add to ChromaDB collection
            self.collection.add(
                ids=[image_id],
                embeddings=[embedding.tolist()],
                metadatas=[{
                    "title": title if title else f"Uploaded Image {timestamp}",
                    "description": description if description else "User uploaded image"
                }],
                documents=[filename]
            )

            # Update paths list
            self.image_paths.append(image_id)

            # Add metadata for this image
            self.image_metadata[image_id] = {
                "title": title if title else f"Uploaded Image {timestamp}",
                "description": description if description else "User uploaded image"
            }

            # Update metadata
            self.metadata["image_paths"] = self.image_paths
            self.metadata["image_metadata"] = self.image_metadata
            self.metadata["num_images"] = len(self.image_paths)

            # Save metadata
            metadata_path = self.embedded_data / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)

            return (f"Successfully added image to database!\n\n"
                    f"Saved as: {filename}\n"
                    f"Title: {self.image_metadata[image_id]['title']}\n"
                    f"Description: {self.image_metadata[image_id]['description']}\n"
                    f"Total images in database: {len(self.image_paths)}\n"
                    f"Index updated and saved")

        except Exception as e:
            return f"Error adding image to database: {str(e)}"

    def update_metadata(self, image_path: str, new_title: str, new_description: str) -> str:
        if image_path not in self.image_metadata:
            return "Image not found!"

        try:
            # Update metadata
            self.image_metadata[image_path] = {
                "title": new_title,
                "description": new_description
            }

            # Update in ChromaDB
            self.collection.update(
                ids=[image_path],
                metadatas=[{
                    "title": new_title,
                    "description": new_description
                }]
            )

            # Save to file
            self.metadata["image_metadata"] = self.image_metadata
            metadata_path = self.embedded_data / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)

            return f"Successfully updated metadata for {Path(image_path).name}"

        except Exception as e:
            return f"Error updating metadata: {str(e)}"

    def delete_from_database(self, image_path: str) -> str:
        if image_path not in self.image_metadata:
            return "Image not found!"

        try:
            # Delete from ChromaDB
            self.collection.delete(ids=[image_path])

            # Delete the image file
            img_file = Path(image_path)
            if img_file.exists():
                img_file.unlink()

            # Update paths list and metadata
            self.image_paths.remove(image_path)
            del self.image_metadata[image_path]

            # Update metadata
            self.metadata["image_paths"] = self.image_paths
            self.metadata["image_metadata"] = self.image_metadata
            self.metadata["num_images"] = len(self.image_paths)

            # Save to file
            metadata_path = self.embedded_data / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)

            return f"Successfully deleted {Path(image_path).name} from database"

        except Exception as e:
            return f"Error deleting image: {str(e)}"

    def export_metadata_json(self) -> str:
        try:
            return json.dumps(self.metadata, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error exporting metadata: {str(e)}"

