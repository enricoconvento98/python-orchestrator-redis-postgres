# app/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the dependencies file to the working directory
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size
# --trusted-host: Required if you are behind a firewall/proxy
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run orchestrator.py when the container launches
CMD ["python", "orchestrator.py"]