# Dockerfile para Raspberry Pi con libcamera y OpenCV
FROM balenalib/raspberrypi4-64-debian:bookworm-run  # Imagen ARM64 válida <button class="citation-flag" data-index="7">

# 1. Instalar dependencias del sistema
RUN apt update && apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libcamera-dev \
    python3-libcamera \
    libkms-dev \
    libopencv-dev \
    libatlas-base-dev \
    libboost-dev \
    libgnutls28-dev \
    libx11-dev \  # Para Qt/XCB <button class="citation-flag" data-index="1">
    libegl1-mesa \  # Para DRM/KMS <button class="citation-flag" data-index="3">
    libgles2-mesa

# 2. Crear entorno virtual y configurar symlinks
RUN python3.11 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    ln -s /usr/lib/python3/dist-packages/libcamera* /app/venv/lib/python3.11/site-packages/ && \
    ln -s /usr/lib/python3/dist-packages/kms* /app/venv/lib/python3.11/site-packages/ && \
    echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> /app/venv/lib/python3.11/site-packages/sitecustomize.py

# 3. Copiar código fuente
COPY . /app
WORKDIR /app

# 4. Instalar dependencias Python
RUN /app/venv/bin/pip install -r requirements.txt

# 5. Ejecutar el script con acceso a la cámara
CMD ["bash", "-c", "source /app/venv/bin/activate && \
                    python main.py --no-install-tag  # Ignorar errores de install_tag <button class="citation-flag" data-index="4">"]