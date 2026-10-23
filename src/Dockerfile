# Use an official, lean Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /code

# Set environment variables
# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /code/requirements.txt

RUN pip install --upgrade pip

# Install dependencies without caching index packages locally to save space
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of the application code into the container
COPY /src /code/src

# Expose port 3100 to the outside world
EXPOSE 3100

# Run the FastAPI application using the built-in CLI command
CMD ["fastapi", "run", "src/main.py", "--port", "3100"]
