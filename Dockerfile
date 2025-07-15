FROM python:3.12

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /colle

COPY --chown=user ./src/requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./src/requirements.txt

COPY --chown=user . /app
CMD ["uvicorn", "src.backend.submission_api:app", "--host", "0.0.0.0", "--port", "7860"]