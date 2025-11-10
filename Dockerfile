FROM python:3.12-slim
WORKDIR app/
COPY dist/*.whl /tmp/ 
COPY config.yaml . 
RUN pip install --no-cache-dir /tmp/*.whl 
CMD ["/bin/bash"] 