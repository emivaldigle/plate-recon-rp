from rpi_rf import RFDevice
import time

GPIO_TRANSMISOR = 27

# Configurar el transmisor
transmisor = RFDevice(GPIO_TRANSMISOR)
transmisor.enable_tx()

# Código binario y su equivalente decimal
GATE_CODE = "0101010100"
DECIMAL_CODE = int(GATE_CODE, 2)

# Configuración del pulso y protocolo
PULSE = 180
PROTOCOL = 2  # Cambia esto si usas otro protocolo

try:
    print("Enviando datos...")
    transmisor.tx_code(DECIMAL_CODE, tx_proto=PROTOCOL, tx_pulselength=PULSE, tx_length=len(GATE_CODE))
    time.sleep(1)
    print("Datos enviados")
except Exception as ex:
    print(f"Error: {ex}")
finally:
    # Apagar el transmisor
    transmisor.cleanup()