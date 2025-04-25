# Servicio de Verificación Facial

Este servicio proporciona una API REST para verificar si dos imágenes faciales corresponden a la misma persona, utilizando la biblioteca DeepFace.

## Características

- Endpoint para verificación facial entre una imagen de referencia y una imagen a comparar
- Respuesta en formato JSON con resultado de verificación y porcentaje de similitud
- Manejo de imágenes en formato base64
- Soporte para imágenes WebP

## Requisitos

### Opción 1: Ejecutar con Docker (recomendado)

- Docker
- Docker Compose

### Opción 2: Ejecución local

- Python 3.8+
- Dependencias listadas en `requirements.txt`

## Instalación y ejecución

### Usando Docker (recomendado)

1. Construir y ejecutar el contenedor:

```bash
docker-compose up -d
```

2. El servicio estará disponible en `http://localhost:7424`

### Ejecución local

1. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

2. Ejecutar la aplicación:

```bash
python app.py
```

Por defecto, el servicio se ejecuta en `http://localhost:7424`

## Uso

### Endpoint de Verificación

**URL**: `/verify`
**Método**: `POST`
**Content-Type**: `application/json`

**Cuerpo de la solicitud**:

```json
{
  "reference_image": "base64_encoded_image_string",
  "compare_image": "base64_encoded_image_string"
}
```

**Respuesta exitosa**:

```json
{
  "verified": true,
  "similarity": 0.95,
  "process_time_seconds": 1.234
}
```

- `verified`: booleano que indica si las caras pertenecen a la misma persona
- `similarity`: valor entre 0 y 1 que indica el grado de similitud (más cercano a 1 = más similar)
- `process_time_seconds`: tiempo de procesamiento en segundos que toma verificar las imágenes

**Códigos de respuesta**:

- `200 OK`: Solicitud procesada correctamente
- `400 Bad Request`: Solicitud incorrecta (falta alguna imagen o formato inválido)
- `500 Internal Server Error`: Error en el procesamiento

### Endpoint de Salud

**URL**: `/health`
**Método**: `GET`

**Respuesta**:

```json
{
  "status": "ok"
}
```

## Ejemplo de Uso

### Usando el script de prueba

```bash
# Para el servicio dockerizado
python test_docker.py --reference "imagen_enrolamiento.webp" --compare "imagen_entrada_1.webp" --wait

# Para el servicio local
python test_service.py --server http://localhost:7424 --reference "imagen_enrolamiento.webp" --compare "imagen_entrada_1.webp"
```

### Usando PowerShell en Windows

```powershell
# Para el servicio dockerizado (si tienes problemas con Python)
.\test_with_curl.ps1 -referencePath "D:\ruta\imagen_enrolamiento.webp" -comparePath "D:\ruta\imagen_entrada_1.webp"
```

### Usando Python directamente

```python
import requests
import base64

# Codificar imágenes a base64
with open("imagen_referencia.webp", "rb") as img_file:
    reference_img = base64.b64encode(img_file.read()).decode('utf-8')

with open("imagen_comparar.webp", "rb") as img_file:
    compare_img = base64.b64encode(img_file.read()).decode('utf-8')

# Crear payload
payload = {
    "reference_image": reference_img,
    "compare_image": compare_img
}

# Enviar solicitud
response = requests.post("http://localhost:7424/verify", json=payload)
result = response.json()

print(f"Verificado: {result['verified']}")
print(f"Similitud: {result['similarity']}")
```

## Notas Técnicas

- El servicio utiliza el modelo VGG-Face y métrica de distancia coseno para la verificación facial
- Las imágenes se almacenan temporalmente durante el procesamiento y se eliminan después
- Se recomienda enviar imágenes que contengan caras claramente visibles para obtener mejores resultados
- Soporta formatos de imagen WebP y convencionales (JPG, PNG)

## Archivos incluidos

- `app.py`: Servicio principal con endpoints REST
- `requirements.txt`: Dependencias del proyecto
- `test_service.py`: Cliente para pruebas del servicio
- `verify_local.py`: Script para verificación facial local sin el servicio web
- `check_webp.py`: Utilidad para verificar compatibilidad con imágenes WebP
- `Dockerfile` y `docker-compose.yml`: Archivos para dockerización del servicio
- `test_docker.py`: Cliente para pruebas con el servicio dockerizado

## Dockerización

La versión dockerizada del servicio ofrece las siguientes ventajas:

- Elimina problemas de compatibilidad de dependencias
- Proporciona un entorno aislado y consistente
- Facilita el despliegue en diferentes sistemas
- Incluye un volumen persistente para almacenar los modelos descargados

## Casos de uso comunes

### Caso 1: Verificación de entrada/salida en un establecimiento
El servicio está diseñado para comparar la imagen de una persona que ingresa en un establecimiento con la imagen de la misma persona al salir. El flujo típico sería:

1. Capturar una imagen facial durante el ingreso y almacenarla como referencia
2. Capturar una segunda imagen facial durante la salida
3. Enviar ambas imágenes al servicio para su verificación
4. Confirmar si corresponden a la misma persona basándose en el resultado

### Caso 2: Integración con aplicaciones existentes

Para integrar este servicio en una aplicación existente:

1. Asegurarse de que el contenedor Docker esté en ejecución
2. En el código de la aplicación principal, implementar las llamadas al endpoint `/verify`
3. Procesar las respuestas JSON para tomar decisiones basadas en la verificación

## Solución de problemas

### El servicio no responde
- Verificar que el contenedor esté en ejecución: `docker ps`
- Reiniciar el servicio: `docker-compose restart`
- Verificar logs: `docker-compose logs`

### Imágenes no reconocidas
- Asegurarse de que las imágenes contengan rostros claramente visibles
- Comprobar que el formato de la imagen sea compatible (JPG, PNG, WebP)
- Verificar que la codificación base64 sea correcta

### Resultados inesperados
- Un valor de similitud menor a 0.7 generalmente indica personas diferentes
- La iluminación, ángulo y calidad de la imagen afectan los resultados
- Utilizar imágenes con buena resolución para mejores resultados

## Limitaciones del servicio
- Se recomienda no procesar más de 10 solicitudes por segundo
- El servicio está optimizado para verificación 1:1, no para búsqueda 1:N
- La primera ejecución puede tardar más tiempo mientras se descargan los modelos

## Consideraciones de seguridad
- Las imágenes se procesan localmente y no se almacenan permanentemente
- Para entornos de producción, considere implementar HTTPS
- Los modelos faciales se almacenan en un volumen Docker persistente
