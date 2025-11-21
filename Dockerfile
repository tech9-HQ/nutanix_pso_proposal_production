# --- 1. Base image ---
FROM python:3.11-slim

# --- 2. Workdir ---
WORKDIR /app

# --- 3. System deps (if you need postgres, etc, add dev libs here) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# --- 4. Copy project files ---
COPY . /app

# --- 5. Install Python dependencies ---
# assumes you have requirements.txt in project root
RUN pip install --no-cache-dir -r requirements.txt

# --- 6. Expose port used by uvicorn ---
EXPOSE 8000

# --- 7. Start FastAPI (serving frontend via StaticFiles) ---
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
