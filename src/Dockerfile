# Base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /YOUR_WORKING_DIRECTORY

# Create and activate a virtual environment no need if you run inside docker image
# RUN python -m venv venv
# ENV PATH="/app/venv/bin:$PATH"

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY . .

# Expose a port (if needed)
EXPOSE 8000

# Specify the command to run the application
CMD [ "python", "app.py" ]
