# CLIP Image Search

A full-stack CLIP-based image search application with user authentication and vector search capabilities.

## Project Structure

```
Vector-Search/
├── backend/           # FastAPI backend with authentication
│   ├── app/
│   ├── scripts/
│   └── requirements.txt
└── frontend/          # Streamlit frontend
    ├── pages/
    ├── src/
    ├── app.py
    └── requirements.txt
```

## Start-up steps

### 1. Clone the repository:
```bash
git clone https://github.com/FurquanMobeen/Vector-Search.git
cd Vector-Search
```

### 2. Create and activate virtual environment:
```bash
# For Windows:
python -m venv .venv
.venv\Scripts\activate

# For MacOS/Linux:
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install backend packages:
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 4. Install frontend packages:
```bash
cd frontend
pip install -r requirements.txt
cd ..
```
**OPTIONAL**: If you have a CUDA GPU and you want to use it, do this after installing the packages from the requirements.txt file:
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Check if torch is supporting your CUDA GPU
```bash
# For Windows:
python -c "import torch; print('CUDA available:',torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"
# or
py -c "import torch; print('CUDA available:',torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"

# For MacOS/Linux:
python3 -c "import torch; print('CUDA available:',torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"
```
This will then be used for embed the images.

### 5. Create test users (First time only):
```bash
cd backend
python scripts/create_test_data.py
cd ..
```

This creates test users:
- **Admin**: username: `admin`, password: `admin123`
- **User1**: username: `user1`, password: `user123`
- **User2**: username: `user2`, password: `user123`

### 6. Data:
#### Option 1: Add your own images
```bash
cd frontend
mkdir data
```

#### Option 2: Generate predefined testing data
```bash
cd frontend
python download_data.py
```

### 7. Embed the images into ChromaDB:
```bash
cd frontend
python embed_images.py
cd ..
```

### 8. Run the application:

**Terminal 1 - Start Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
streamlit run app.py
```

Then open http://localhost:8501 and login with the test credentials.
**--server.port**: Define your own port

**--server.embedded_data**: If you have your own embedded data somewhere else

**--server.model**: Load another CLIP model of your liking

**Common CLIP models**:
 - openai/clip-vit-base-patch32 - Default, balanced (fastest)
 - openai/clip-vit-base-patch16 - Better accuracy, slower
 - openai/clip-vit-large-patch14 - Best accuracy, slowest

## UI functionality

### Image Search
#### Search by Image:
1. Upload an image of your file explorer.
2. This will show you the uploaded image.
3. Underneath the image you'll see some functionality to rotate the image or reset it back to its original position.
4. When you are satisfied with your image and image direction, click on "Search by Image" to see the similar image results.
5. On the left, it will show you the similar image results in a 3x3 grid.
6. Underneath the results, there will be pagination so that you can see more similar results.



### Text Search
#### Search by Text
1. In the "Insert Text" section, you can insert the text that you want to query.
2. After clicking on the "Search by Text" button, it will show you the similar images based on the text.
3. On the left you'll see the images in a 3x3 grid and there is a pagination under the similar images, and this will generate the next 9 results.

### Manage Images
#### Upload Image to Database:
1. Upload an image of your file explorer.
2. This will show you the uploaded image.
3. Underneath the image you'll see some functionality to rotate the image or reset it back to its original position.
4. Enter a title and description for the image, it will give you an error if you don't
5. Click on "Add Image", this will add the image with the metadata to the embedding in the vector space.

#### Select Image to Manage:
1. In the "Select Image" drop-down, you can select the image that you want to manage. Difficult finding it? Then you can use the text box to search the title for the image.
2. After selecting the image, the image will appear right of the page with the title and the description.
3. In the "Edit Metadata" section you'll see that you can update the title or description of the image. When done you can click on "Update Metadata" to save the changes.
4. In the "Delete Image" section you can delete the image from the embedded vector space. By clicking on the "Delete from Database" you'll delete the image.
5. On the right side, under the selected image, you can see a section called "Export Metadata". Here you can export the .json data of all the images or for the selected image.