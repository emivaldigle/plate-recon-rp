# Dockerfile para Raspberry Pi con libcamera y OpenCV
FROM balenalib/raspberrypi4-64-debian:bookworm-run

# 1. Usar apt-get en lugar de apt para evitar warnings <button class="citation-flag" data-index="1"><button class="citation-flag" data-index="6">
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libcamera-dev \ 
    libdrm-dev \     
    libopencv-dev \
    libatlas-base-dev \
    libboost-dev \
    libgnutls28-dev \
    libx11-dev \
    libegl-mesa0 \  
    libgles2-mesa

# 2. Crear entorno virtual y configurar symlinks
RUN python3.11 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    ln -s /usr/lib/python3/dist-packages/libcamera* /app/venv/lib/python3.11/site-packages/ && \
    echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> /app/venv/lib/python3.11/site-packages/sitecustomize.py

# 3. Copiar codigo fuente
COPY . /app
WORKDIR /app

RUN /app/venv/bin/python -m pip install -r requirements.txt

CMD ["sh", "-c", "source /app/venv/bin/activate && python main.py"]