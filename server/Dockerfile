# Use the official Python image from the Docker Hub
FROM python:3.12

RUN #mkdir -p /server
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /server
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local directory to the working directory
COPY . .
#EXPOSE 8000

# Define the command to run the application when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
