# Start from Python 3.12 image
FROM python:3.12

# Set working directory
WORKDIR /app

# Copy model artifacts
COPY . /app/nyis_model

# Install dependencies
RUN pip install --no-cache-dir -r nyis_model/requirements.txt

# Expose port for REST API
EXPOSE 5000

# Command to serve predictions (MLflow pyfunc) on all network interfaces
CMD ["mlflow", "models", "serve", "-m", "nyis_model", "-p", "5000", "--host", "0.0.0.0", "--no-conda"]
