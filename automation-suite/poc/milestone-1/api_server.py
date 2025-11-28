# Copyright 2025 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
api_server.py

Module responsible for defining the FastAPI application and its endpoints.

This module serves as the main entry point for the Omnia API, providing a RESTful
interface for clients to interact with the application.

Endpoints Ex:
    - /ParseCatalog: Accepts a catalog file and returns the parsed data.

Usage:
    - Run the application using `uvicorn api_server:app --host 0.0.0.0 --port 8000`
    - Use a tool like curl to test the endpoints, for example:
        - `curl -X POST -F 'file=@path/to/catalog/file' http://localhost:8000/ParseCatalog`
"""

import json
import subprocess

from fastapi import FastAPI, File, UploadFile
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
        result = subprocess.run(["python", "catalog_parser/generator.py", "--catalog", "input.json", "--schema", "catalog_parser/resources/CatalogSchema.json"], check=True)
        if result.returncode != 0:
            return {"message": f"Failed to parse catalog. Return code: {result.returncode}"}
        
        # Return a success message
        return {"message": "Catalog parsed successfully"}
    except subprocess.SubprocessError as e:
        # Return an error message if an exception occurs
        return {"message": str(e)}
    except subprocess.CalledProcessError as e:
        # Handle the exception, for example, return an error message
        return {"message": f"Error: {e.cmd} failed with return code {e.returncode}"}
    
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
        result = subprocess.run(["python", "catalog_parser/adapter.py", "--catalog", "input.json", "--schema", "catalog_parser/resources/CatalogSchema.json"], check=True)
        if result.returncode != 0:
            return {"message": f"Failed to generate input files. Return code: {result.returncode}"}
        
        # Return a success message
        return {"message": "Input files generated successfully"}
    except json.JSONDecodeError as e:
        # Return an error message if the JSON data is invalid
        return {"message": f"Invalid JSON data: {str(e)}"}
    except subprocess.SubprocessError as e:
        # Return an error message if an exception occurs
        return {"message": str(e)}
    except subprocess.CalledProcessError as e:
        # Handle the exception, for example, return an error message
        return {"message": f"Error: {e.cmd} failed with return code {e.returncode}"}

@app.post("/BuildImage")
async def build_image():
    """
    Triggers the build image process by executing the build_image_x86_64.yml playbook
    on the omnia_core container using SSH.

    Returns:
        dict: A dictionary containing a success message.
    """

    # Define the SSH command to execute on the omnia_core container
    cmd = "ssh root@omnia_core 'ansible-playbook build_image_x86_64/build_image_x86_64.yml'"

    # Execute the command in the background without waiting for completion
    subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return {"message": "Invoked BuildImage Successfully"}
