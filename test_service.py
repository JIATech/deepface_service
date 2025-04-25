import requests
import base64
import argparse
import json
import sys
import os

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

if __name__ == "__main__":
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='Cliente para servicio de verificación facial')
    parser.add_argument('--server', default='http://localhost:5000', 
                        help='URL del servidor (default: http://localhost:5000)')
    parser.add_argument('--reference', required=True, 
                        help='Ruta a la imagen de referencia')
    parser.add_argument('--compare', required=True, 
                        help='Ruta a la imagen de comparación')
    parser.add_argument('--output', help='Guardar resultado en archivo JSON')
    
    args = parser.parse_args()
    
    # Ejecutar verificación
    result = verify_faces(args.server, args.reference, args.compare)
    
    # Guardar resultado si se especificó
    if result and args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Resultado guardado en: {args.output}")
