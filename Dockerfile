# Dockerfile para Raspberry Pi con libcamera y OpenCV
FROM balenalib/raspberrypi4-64-debian:bookworm-run

# 1. Usar apt-get en lugar de apt para evitar warnings <button class="citation-flag" data-index="1"><button class="citation-flag" data-index="6">
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    libcamera-dev \  # Reemplaza python3-libcamera <button class="citation-flag" data-index="7">
    libdrm-dev \     # Reemplaza libkms-dev <button class="citation-flag" data-index="7">
    libopencv-dev \
    libatlas-base-dev \
    libboost-dev \
    libgnutls28-dev \
    libx11-dev \
    libegl-mesa0 \    # Corrección para EGL <button class="citation-flag" data-index="7">
    libgles2-mesa

# 2. Crear entorno virtual y configurar symlinks
RUN python3.11 -m venv /app/venv && \
    /app/venv/bin/pip install --upgrade pip && \
    ln -s /usr/lib/python3/dist-packages/libcamera* /app/venv/lib/python3.11/site-packages/ && \
    echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> /app/venv/lib/python3.11/site-packages/sitecustomize.py

# 3. Copiar código fuente
COPY . /app
WORKDIR /app

# 4. Instalar dependencias Python
RUN /app/venv/bin/pip install -r requirements.txt

# 5. Ejecutar el script (con JSONArgsRecommended fix <button class="citation-flag" data-index="4">)
CMD ["sh", "-c", "source /app/venv/bin/activate && python main.py"]