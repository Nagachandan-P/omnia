from fastapi import FastAPI, File, Response, UploadFile
import json
import subprocess

app = FastAPI()

@app.post("/ParseCatalog")
async def parse_catalog(file: UploadFile = File(...)) -> dict:
    """
    Parse a catalog from an uploaded JSON file.

    Args:
        file (UploadFile): The uploaded JSON file.

    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    try:
        # Check if the file is a valid JSON file
        if not file.filename.endswith('.json'):
            return {"message": "Invalid file format. Only JSON files are accepted."}
        
        # Read the contents of the uploaded file
        contents = await file.read()
        
        # Parse the JSON data from the file contents
        json_data = json.loads(contents)

        # Validate the JSON data
        if not isinstance(json_data, dict):
            return {"message": "Invalid JSON data. The data must be a dictionary."}
        
        # Write the JSON data to a local file
        with open('input.json', 'w') as f:
            json.dump(json_data, f)
        
        # Run the generator_main.py script with the local file as input
        result = subprocess.run(["python", "catalog_parser/generator.py", "--catalog", "input.json", "--schema", "catalog_parser/resources/CatalogSchema.json"])
        if result.returncode != 0:
            return {"message": f"Failed to parse catalog. Return code: {result.returncode}"}
        
        # Return a success message
        return {"message": "Catalog parsed successfully"}
    except Exception as e:
        # Return an error message if an exception occurs
        return {"message": str(e)}
    
@app.post("/GenerateInputFiles")
async def generate_input_files(file: UploadFile = File(...)) -> dict:
    """
    Generate input files from an uploaded JSON file.

    Args:
        file (UploadFile): The uploaded JSON file.

    Returns:
        dict: A dictionary containing a success message or an error message.
    """
    try:
        # Check if the file is a valid JSON file
        if not file.filename.endswith('.json'):
            return {"message": "Invalid file format. Only JSON files are accepted."}
        
        # Read the contents of the uploaded file
        contents = await file.read()
        
        # Parse the JSON data from the file contents
        json_data = json.loads(contents)
        
        # Validate the JSON data
        if not isinstance(json_data, dict):
            return {"message": "Invalid JSON data. The data must be a dictionary."}
        
        # Write the JSON data to a local file
        with open('input.json', 'w') as f:
            json.dump(json_data, f)
        
        # Run the generator_main.py script with the local file as input
        result = subprocess.run(["python", "catalog_parser/adapter.py", "--catalog", "input.json", "--schema", "catalog_parser/resources/CatalogSchema.json"])
        if result.returncode != 0:
            return {"message": f"Failed to generate input files. Return code: {result.returncode}"}
        
        # Return a success message
        return {"message": "Input files generated successfully"}
    except json.JSONDecodeError as e:
        # Return an error message if the JSON data is invalid
        return {"message": f"Invalid JSON data: {str(e)}"}
    except Exception as e:
        # Return an error message if an exception occurs
        return {"message": str(e)}
@app.post("/BuildImage")
async def build_image():
    # Define the SSH command to execute on the omnia_core container
    cmd = f"ssh root@omnia_core 'ansible-playbook build_image_x86_64/build_image_x86_64.yml'"

    # Execute the command in the background without waiting for completion
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"message": "Invoked BuildImage Successfully"}
