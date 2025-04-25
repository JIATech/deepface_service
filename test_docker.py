import requests
import base64
import argparse
import json
import sys
import os
import time

def encode_image(image_path):
    """Codifica una imagen en base64"""
    if not os.path.exists(image_path):
        print(f"Error: El archivo {image_path} no existe")
        sys.exit(1)
    
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

def verify_faces(server_url, reference_img_path, compare_img_path):
    """Realiza una solicitud al servicio de verificación facial"""
    try:
        # Codificar imágenes
        reference_img = encode_image(reference_img_path)
        compare_img = encode_image(compare_img_path)
        
        # Crear payload
        payload = {
            "reference_image": reference_img,
            "compare_image": compare_img
        }
        
        # Enviar solicitud
        print(f"Enviando solicitud a {server_url}/verify...")
        response = requests.post(f"{server_url}/verify", json=payload)
        
        # Verificar respuesta
        if response.status_code == 200:
            result = response.json()
            print("\nResultado de verificación:")
            print(f"Verificado: {result['verified']}")
            print(f"Similitud: {result['similarity']:.4f}")
            return result
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_service_health(server_url, max_retries=10, retry_interval=3):
    """Verificar que el servicio esté funcionando antes de continuar"""
    print(f"Verificando disponibilidad del servicio en {server_url}/health...")
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{server_url}/health", timeout=5)
            if response.status_code == 200:
                print("Servicio disponible y funcionando correctamente.")
                return True
            else:
                print(f"Intento {i+1}/{max_retries}: Servicio no disponible (código {response.status_code})")
        except requests.exceptions.RequestException:
            print(f"Intento {i+1}/{max_retries}: Servicio no accesible")
        
        time.sleep(retry_interval)
    
    print(f"El servicio no está disponible después de {max_retries} intentos.")
    return False

if __name__ == "__main__":
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='Cliente para servicio dockerizado de verificación facial')
    parser.add_argument('--server', default='http://localhost:7424', 
                        help='URL del servidor (default: http://localhost:7424)')
    parser.add_argument('--reference', required=True, 
                        help='Ruta a la imagen de referencia')
    parser.add_argument('--compare', required=True, 
                        help='Ruta a la imagen de comparación')
    parser.add_argument('--output', help='Guardar resultado en archivo JSON')
    parser.add_argument('--wait', action='store_true', help='Esperar a que el servicio esté disponible')
    
    args = parser.parse_args()
    
    # Verificar disponibilidad del servicio si se especifica la opción --wait
    if args.wait and not check_service_health(args.server):
        print("No se pudo conectar con el servicio.")
        sys.exit(1)
    
    # Ejecutar verificación
    result = verify_faces(args.server, args.reference, args.compare)
    
    # Guardar resultado si se especificó
    if result and args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Resultado guardado en: {args.output}")
