FROM python:3.12.3

# Set the working directory
WORKDIR /code

# Create the directory structure and an empty log file
RUN mkdir -p app/base/logs && touch app/base/logs/application.log

# Ensure the log file is writable
RUN chmod 666 app/base/logs/application.log

COPY ./pyproject.toml /code/

# Install Poetry
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry

# Copy Poetry files to the container
COPY ./pyproject.toml ./poetry.lock* /code/

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the entire project to the container
COPY ./ /code/

EXPOSE 8000

# Command to run the FastAPI app
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]