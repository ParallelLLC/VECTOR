# Minimal runtime image
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
ENV VECTOR_STATE_FILE=/app/out/state.json
ENV VECTOR_EDGES_FILE=/app/examples/edges.csv
EXPOSE 8000
CMD ["uvicorn", "vector.service:app", "--host", "0.0.0.0", "--port", "8000"]
