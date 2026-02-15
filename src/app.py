#!/usr/bin/python

import json
import os
from typing import Dict, Any
from venv import logger
import base64
import subprocess

def extract_content(name, model_source_base64, working_dir):
    """
    Extracts the OpenSCAD code and associated resources from the input event and saves them to a temporary directory.
    Parameters:
        name: Name of the resource
        model_source_base64: Base64-encoded file contents
        working_dir: Path to the directory where files will be saved
    """
    try:
        if '/' in name:
            # Create subdirectories if needed
            subdir = os.path.dirname(name)
            os.makedirs(os.path.join(working_dir, subdir), exist_ok=True)

        resource_path = os.path.join(working_dir, name)
        decoded_content = base64.b64decode(model_source_base64)
        with open(resource_path, "wb") as f:
            f.write(decoded_content)
        logger.info(f"Successfully extracted resource {name} to {resource_path}")
    except Exception as e:
        logger.error(f"Error extracting resource {name}: {str(e)}")
        raise


# Hanlder unwrapping the OpenSCAD code to render and associated resources
# and invoking OpenSCAD in headless mode to obtani the render model
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function
    Parameters:
        event: Dict containing the Lambda function event data. This JSON follows the schema of this example:
        {
            "model_source_base64": "base64-encoded OpenSCAD code",
            "resources": [
                {
                    "path": "resource1",
                    "content_base64": "base64-encoded content of resource1"
                },
                {
                    "path": "resource2",
                    "content_base64": "base64-encoded content of resource2"
                }
            ]
        }
        context: Lambda runtime context
    Returns:
        Dict containing status message
    """
    try:
        # Create working direcoty
        job_id = context.aws_request_id
        wdir = f"/tmp/{job_id}"
        os.mkdir(wdir)

        # extract files from event and save to working directory
        model_source_base64 = event.get("model_source_base64")

        extract_content("model.scad", model_source_base64, wdir)

        resources = event.get("resources", [])  

        for resource in resources:
            resource_path = resource.get("path")
            resource_content_base64 = resource.get("content_base64")
            if resource_path and resource_content_base64:
                extract_content(resource_path, resource_content_base64, wdir)
            else:
                raise ValueError(f"Unable to extract resource from request: {resource}")
        
        # invoke OpenSCAD
        output_path = os.path.join(wdir, "output.stl")
        render_command = f"/usr/local/bin/openscad -o {output_path} {os.path.join(wdir, 'model.scad')}"
        
        try:
            render_output = subprocess.check_output(render_command, shell=True, check=True)
            logger.info(f"OpenSCAD render output: {render_output.decode('utf-8')}")
        except subprocess.CalledProcessError as e:
            logger.error(f"OpenSCAD render error: {e.output.decode('utf-8')}")
            raise RuntimeError(f"OpenSCAD rendering failed: {e.output.decode('utf-8')}")

        rendered_model_base64 = None
        with open(output_path, "rb") as f:
            rendered_model_base64 = base64.b64encode(f.read()).decode('utf-8')
        
        if not rendered_model_base64:
            raise ValueError("Failed to render model content")
        
        logger.info(f"Successfully rendered model for job {job_id}")

        # Create the response content
        response_content = {
            "job_id": job_id,
            "rendered_model_base64": rendered_model_base64,
            "name": "output.stl"
        }
        
        return {
            "statusCode": 200,
            "body": json.dumps(response_content)
        }

    except Exception as e:
        logger.error(f"Error processing render request: {str(e)}")
        raise