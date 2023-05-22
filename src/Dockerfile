# Base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /YOUR_WORKING_DIRECTORY

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose port 5003
EXPOSE 5003

# Specify the command to run the application
CMD [ "python", "main.py" ]
