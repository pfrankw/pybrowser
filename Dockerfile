# Use an official Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the application files to the container
COPY pybrowser.py .
COPY templates/index.html templates/index.html

# Install dependencies
RUN pip install flask

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
CMD ["python", "pybrowser.py"]
