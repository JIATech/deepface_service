import sys
import os
import argparse

try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False
    print("OpenCV no está instalado o no es accesible")

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("PIL no está instalado o no es accesible")

def check_image(image_path):
    """
    Verifica si una imagen puede ser abierta y muestra información sobre ella
    """
    print(f"\nVerificando imagen: {image_path}")
    
    # Verificar que el archivo exista
    if not os.path.exists(image_path):
        print(f"Error: El archivo {image_path} no existe")
        return False
        
    success = False
    
    # Intentar abrir con OpenCV si está disponible
    if HAS_OPENCV:
        try:
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            if img is not None:
                height, width, channels = img.shape
                print(f"[OpenCV] Imagen cargada correctamente")
                print(f"[OpenCV] Dimensiones: {width}x{height}, Canales: {channels}")
                success = True
            else:
                print(f"[OpenCV] No se pudo cargar la imagen (posible falta de soporte para WebP)")
        except Exception as e:
            print(f"[OpenCV] Error: {str(e)}")
    
    # Intentar abrir con PIL si está disponible
    if HAS_PIL:
        try:
            img = Image.open(image_path)
            print(f"[PIL] Imagen cargada correctamente")
            print(f"[PIL] Formato: {img.format}, Modo: {img.mode}, Dimensiones: {img.size}")
            success = True
        except Exception as e:
            print(f"[PIL] Error: {str(e)}")
    
    return success

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Verificación de imágenes WebP')
    parser.add_argument('--images', nargs='+', help='Rutas a las imágenes a verificar')
    
    args = parser.parse_args()
    
    if not args.images:
        # Valores predeterminados si no se proporcionan imágenes
        default_images = [
            "D:\\deepface_service\\imagen_enrolamiento.webp",
            "D:\\deepface_service\\imagen_entrada_1.webp",
            "D:\\deepface_service\\imagen_salida_1.webp"
        ]
        print(f"No se proporcionaron imágenes, verificando las imágenes predeterminadas:")
        for img_path in default_images:
            check_image(img_path)
    else:
        for img_path in args.images:
            check_image(img_path)
