# Use an official Python runtime as a parent image
FROM python:3.7.3-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
RUN mkdir -p data/collector
RUN mkdir -p data/matcher

# Make required directories
RUN mkdir logs
RUN mkdir data

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install textblob
#RUN python -m textblob.download_corpora

# Make port 5000 10005 available to the world outside this container
EXPOSE 5000 10005

# Run start.sh when the container launches
#ENTRYPOINT ["./start.sh"]
#CMD ["api"]
CMD gunicorn --workers=4 -b 0.0.0.0:5000 trade-advisor-api:app