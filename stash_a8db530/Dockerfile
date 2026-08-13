FROM python:3.9-slim

WORKDIR /app

# Copy requirements from install folder
COPY qyntara_ai/install/requirements.txt .

# Install dependencies
# Filter out PySide2/6 as we don't need UI in the headless API server usually
# or we use a heavy image with maya base if we need true validation
# For this MCP pattern, let's assume standard python + mocked Maya cmds or headless mayapy if available
# Install dependencies for API and Worker (Geometry + AI)
# We use the CPU version of torch to keep the image smaller for this demo
RUN pip install --no-cache-dir fastapi uvicorn redis requests numpy trimesh open3d
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy source code
COPY . /app

# Expose port
EXPOSE 8000

# Run server
CMD ["uvicorn", "qyntara_ai.server.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
