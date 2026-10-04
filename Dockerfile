FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the package itself
COPY . .
RUN pip install --no-cache-dir .

# Create non-root user
RUN useradd -m -s /bin/bash user
USER user

ENTRYPOINT ["iptv-validators"]
