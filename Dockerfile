# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run batch_pipeline.py when the container launches to create and populate the SQLite database
RUN python pipeline.py

# Make port 80 available to the world outside this container
EXPOSE 80

# Run fast_api_app.py when the container launches
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "80"]