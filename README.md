# plate-recon-rp
# Aplicación para raspberry con OCR para reconocimiento de patentes
# install:
ln -s /usr/lib/python3/dist-packages/libcamera* venv/lib/python3.11/site-packages/
echo "import site; site.addsitedir('/usr/lib/python3/dist-packages')" >> venv/lib/python3.11/site-packages/sitecustomize.py
**ln -s /usr/lib/python3/dist-packages/kms* venv/lib/python3.11/site-packages/

# run
python -m src.main
