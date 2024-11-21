# Step 1: Use the official Python image as the base image
FROM python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the application files into the container
COPY . /app

# Step 4: Install system dependencies (e.g., for psycopg2 and other libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Install the Python dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Expose the port that Flask will run on
EXPOSE 5000

# Step 7: Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Step 8: Run the Flask application
CMD ["flask", "run"]
