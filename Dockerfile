FROM openjdk:17-slim as jre-build
WORKDIR /app
# Binutils for objcopy, needed by jlink.
RUN apt-get update && \
    apt-get install -y --no-install-recommends binutils wget tini
COPY ./morphology-2.2.5-SNAPSHOT.jar /app/morphology-2.2.5-SNAPSHOT.jar
RUN jdeps --print-module-deps --ignore-missing-deps /app/morphology-2.2.5-SNAPSHOT.jar > java.modules
RUN jlink --strip-debug  --add-modules "$(cat java.modules)" --output /java
    
FROM python:3.9-slim as venv-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.9-slim
COPY --from=jre-build /usr/bin/tini /usr/bin/tini
RUN addgroup --gid 1001 "elg" && \
    adduser --disabled-password --gecos "ELG User,,," --home /elg --ingroup elg --uid 1001 elg && \
    chmod +x /usr/bin/tini
COPY --chown=elg:elg --from=jre-build /java /java
COPY --chown=elg:elg --from=venv-build /opt/venv /opt/venv

USER elg:elg
WORKDIR /elg
COPY --chown=elg:elg --from=jre-build /app/morphology-2.2.5-SNAPSHOT.jar /elg/
COPY --chown=elg:elg app.py docker-entrypoint.sh /elg/
ENV PATH="/opt/venv/bin:$PATH"

ENV WORKERS=1
ENV TIMEOUT=60
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO
ENV PYTHON_PATH="/opt/venv/bin"

RUN chmod +x ./docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
