# Use an official Python runtime as a parent image
FROM python:3.12.5

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /fast-api-image-processing
COPY . .

# Make the start.sh script executable
RUN chmod +x ./start.sh

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV REDIS_URL=redis://redis:6379/0
ENV DATABASE_URL=sqlite:///./image-processing.db

# Set the entry point to the shell script
CMD ["./start.sh"]
