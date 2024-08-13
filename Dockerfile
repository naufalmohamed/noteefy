# Use Python 3.8.10 as the base image
FROM python:3.8.10-slim

# Set environment variables
ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    SECRET_KEY=your-secret-key \
    DATABASE_URL=your-database-url

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_ENV=production

# Run Flask app
CMD ["flask", "run"]
