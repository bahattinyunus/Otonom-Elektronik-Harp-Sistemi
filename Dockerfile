FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required for OpenCV, PyTorch, and numpy
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install eventlet

# Copy the rest of the application
COPY . .

# Expose the Flask/SocketIO port
EXPOSE 5000

# Run the system
CMD ["python", "main.py"]
