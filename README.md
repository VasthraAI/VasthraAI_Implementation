# Implementation Instructions
Here's a step-by-step guide to set up VasthraAI with the web app.

## Initial

1. Clone the repository.

```bash
git clone https://github.com/VasthraAI/VasthraAI_Implementation.git
```

### For machines without a GPU

Sometimes, the pytorch versions in the requirements do not work with machines without CUDA support. To fix this, checkout the no-gpu branch
```bash
git checkout no-gpu
```


## Set up the virtual environment

1. Run the virtal environment.
* On Windows:
```bash
venv\Scripts\activate
```
* On Linux
```bash
source venv/bin/activate
```

## Set up the FastAPI backend

1. Navigate to the /API directory
```bash
cd API
```
2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server
```bash
python api.py
```
## Run the React application:

1. Navigate out of the ```/API``` directory and go to the WebApp directory
```bash
cd ..
cd WebApp
```
2. Install dependencies
```bash
npm install
```
3. Run the react application
```bash
npm run dev
```
4. Open the app in the browser, from the port given in the cmd. Usually ```localhost:5173``` or something similar

## Usage

After opening the web app, upload a sketch and click proceed. After a few seconds, the image would be ready to view and download.