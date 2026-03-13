import kagglehub
import shutil
from pathlib import Path

# Download to default location
path = kagglehub.dataset_download("pankajkumar2002/random-image-sample-dataset")

# Move to custom location and flatten structure
custom_path = Path("./data")
custom_path.mkdir(exist_ok=True)

# If files are nested, extract them from the subdirectory
downloaded_path = Path(path)
for item in downloaded_path.glob("*"):
    if item.is_dir():
        # Move contents of subdirectories to data folder
        for subitem in item.glob("*"):
            shutil.move(str(subitem), str(custom_path / subitem.name))
    else:
        # Move files directly
        shutil.move(str(item), str(custom_path / item.name))

# Clean up the downloaded directory if empty
shutil.rmtree(downloaded_path, ignore_errors=True)

print("Path to dataset files:", custom_path)