import chromadb
from pathlib import Path
import json
import time

def check_and_fix_paths():
    embedded_data = Path("./embedded_data")

    if not embedded_data.exists():
        print("No embedded_data folder found, skipping path fix.")
        return

    metadata_path = embedded_data / "metadata.json"
    if not metadata_path.exists():
        print("No metadata.json found, skipping path fix.")
        return

    # Load metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)

    # Check if any paths have backslashes
    needs_fix = any('\\' in p for p in metadata.get("image_paths", []))
    needs_fix = needs_fix or any('\\' in k for k in metadata.get("image_metadata", {}).keys())

    if not needs_fix:
        print("All paths already use forward slashes, no fix needed.")
        return

    print("Found backslashes in paths, fixing...")

    # Fix metadata
    metadata["image_paths"] = [p.replace('\\', '/') for p in metadata.get("image_paths", [])]
    old_metadata = metadata.get("image_metadata", {})
    metadata["image_metadata"] = {k.replace('\\', '/'): v for k, v in old_metadata.items()}

    # Save fixed metadata
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Fix ChromaDB
    client = None
    try:
        client = chromadb.PersistentClient(path=str(embedded_data))
        collection = client.get_or_create_collection(
            name="images",
            metadata={"hnsw:space": "cosine"}
        )

        all_items = collection.get(include=["embeddings", "metadatas", "documents"])

        # Find items with backslashes
        items_to_fix = []
        for i, old_id in enumerate(all_items['ids']):
            if '\\' in old_id:
                new_id = old_id.replace('\\', '/')
                items_to_fix.append({
                    'old_id': old_id,
                    'new_id': new_id,
                    'embedding': all_items['embeddings'][i],
                    'metadata': all_items['metadatas'][i] if all_items['metadatas'] else {},
                    'document': all_items['documents'][i] if all_items['documents'] else None
                })

        if items_to_fix:
            print(f"Fixing {len(items_to_fix)} items in ChromaDB...")

            # Process in batches
            batch_size = 100
            for batch_start in range(0, len(items_to_fix), batch_size):
                batch = items_to_fix[batch_start:batch_start + batch_size]

                # Delete old IDs
                collection.delete(ids=[item['old_id'] for item in batch])

                # Add with new IDs
                collection.add(
                    ids=[item['new_id'] for item in batch],
                    embeddings=[item['embedding'] for item in batch],
                    metadatas=[item['metadata'] for item in batch],
                    documents=[item['document'] for item in batch]
                )

            print(f"Fixed {len(items_to_fix)} paths in ChromaDB!")
        else:
            print("ChromaDB paths already correct.")

    except Exception as e:
        print(f"Error fixing ChromaDB: {e}")
        # Don't fail deployment if this fails
    finally:
        # CRITICAL: Properly close the ChromaDB client to release resources
        if client is not None:
            try:
                # Clear references and force cleanup
                collection = None
                del client
                print("ChromaDB client closed successfully.")
                # Small delay to ensure resources are fully released
                time.sleep(0.5)
            except Exception as e:
                print(f"Warning: Error closing ChromaDB client: {e}")

    print("Path fix complete!")

if __name__ == "__main__":
    check_and_fix_paths()
