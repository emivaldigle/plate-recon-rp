import aiohttp
import asyncio
import base64
import logging

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsynchronousAPIClient:
    def __init__(self, base_url, username="root", password="root"):
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.session = None

    def _get_auth_header(self):
        # Codificar el nombre de usuario y la contraseña en base64
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {
            "Authorization": f"Basic {encoded_credentials}"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        logger.info(f"Session started for {self.base_url}")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()
        logger.info(f"Session closed for {self.base_url}")

    async def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers.update(self._get_auth_header())  # Agregar el header de autenticación
        
        logger.info(f"Sending GET request to {url} with params {params} and headers {headers}")
        
        try:
            async with self.session.get(url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Received response: {data}")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"GET request to {url} failed: {e}")
            raise

    async def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers.update(self._get_auth_header())  # Agregar el header de autenticación
        
        logger.info(f"Sending POST request to {url} with data {data}, json {json}, and headers {headers}")
        
        try:
            async with self.session.post(url, data=data, json=json, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Received response: {data}")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"POST request to {url} failed: {e}")
            raise

    async def patch(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        headers = headers or {}
        headers.update(self._get_auth_header())  # Agregar el header de autenticación
        
        logger.info(f"Sending PATCH request to {url} with data {data}, json {json}, and headers {headers}")
        
        try:
            async with self.session.patch(url, data=data, json=json, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Received response: {data}")
                return data
        except aiohttp.ClientError as e:
            logger.error(f"PATCH request to {url} failed: {e}")
            raise
