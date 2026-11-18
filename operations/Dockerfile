FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df AS packages
COPY requirements.txt /build/requirements.txt
COPY wheels /build/wheels
RUN python -m pip install --no-index --no-cache-dir --require-hashes --find-links=/build/wheels --prefix=/install -r /build/requirements.txt
COPY app /build/app
RUN python -m pip install --no-index --no-cache-dir --no-deps --prefix=/install /build/app/*.whl

FROM python:3.12-slim-bookworm@sha256:935c3c5b12357a7e10caa9c1e6ca5692344d97cf229832ef584be2cec9fc03df
COPY --from=packages /install /usr/local
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
USER 1000:0
ENTRYPOINT ["python", "-m", "lai.operations.runtime"]
