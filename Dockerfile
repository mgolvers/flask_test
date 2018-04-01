# Image
FROM python:alpine3.6

# Comments
LABEL maintainer="Martins Golvers"
LABEL version="1.0"

# Create application directory.
WORKDIR /flask

# Copy requirements file
COPY requirements.txt ./

# Install mysql-devel
RUN apk add --update --no-cache build-base postgresql-dev

# Install python dependencies.
RUN pip install -r requirements.txt

# Copy application to app dir. 
COPY src /flask

# Expose port.
EXPOSE 8000

# Run application.
ENTRYPOINT ["gunicorn", "-b 0.0.0.0:8000" , "run:app"]
