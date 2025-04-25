import sys
import os
import argparse
import json
from deepface import DeepFace
import cv2
import numpy as np

def verify_faces_local(reference_img_path, compare_img_path):
    """
    Verifica localmente dos imágenes faciales sin necesidad de usar el servicio web
    Soporta formatos como JPG, PNG y WebP
    """
    try:
        print(f"Verificando imágenes...")
        print(f"Imagen de referencia: {reference_img_path}")
        print(f"Imagen a comparar: {compare_img_path}")
        
        # Verificar que los archivos existan
        if not os.path.exists(reference_img_path):
            print(f"Error: El archivo {reference_img_path} no existe")
            return None
            
        if not os.path.exists(compare_img_path):
            print(f"Error: El archivo {compare_img_path} no existe")
            return None
        
        # Si las imágenes son WebP, convertirlas primero
        def process_image_if_needed(img_path):
            # Si es WebP, convertir a jpg temporal
            if img_path.lower().endswith('.webp'):
                print(f"Detectada imagen WebP: {img_path}")
                try:
                    # Leer con OpenCV
                    img = cv2.imread(img_path, cv2.IMREAD_COLOR)
                    
                    # Si OpenCV no pudo leer (versiones antiguas no soportan WebP)
                    if img is None:
                        # Intentar usar PIL si está disponible
                        try:
                            from PIL import Image
                            import io
                            
                            # Abrir con PIL y convertir
                            pil_img = Image.open(img_path)
                            if pil_img.mode != 'RGB':
                                pil_img = pil_img.convert('RGB')
                                
                            # Convertir a array numpy y luego a formato BGR de OpenCV
                            img = np.array(pil_img)
                            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        except ImportError:
                            print("No se pudo encontrar PIL para procesar WebP. Instale con: pip install Pillow")
                            return img_path
                        except Exception as e:
                            print(f"Error procesando WebP con PIL: {str(e)}")
                            return img_path
                    
                    # Guardar como JPG temporal
                    temp_path = img_path.rsplit('.', 1)[0] + '_temp.jpg'
                    cv2.imwrite(temp_path, img)
                    print(f"Imagen convertida guardada como: {temp_path}")
                    return temp_path
                except Exception as e:
                    print(f"Error procesando WebP: {str(e)}")
                    return img_path
            return img_path
        
        # Procesar imágenes si son WebP
        ref_path = process_image_if_needed(reference_img_path)
        comp_path = process_image_if_needed(compare_img_path)
        
        # Realizar verificación con DeepFace
        result = DeepFace.verify(
            img1_path=ref_path,
            img2_path=comp_path,
            model_name='VGG-Face',
            distance_metric='cosine'
        )
        
        # Convertir distancia a similitud
        similarity = 1 - result['distance']
        
        # Formatear resultado como en el servicio
        formatted_result = {
            "verified": result['verified'],
            "similarity": similarity
        }
        
        # Mostrar resultado
        print("\nResultado de verificación:")
        print(f"Verificado: {formatted_result['verified']}")
        print(f"Similitud: {formatted_result['similarity']:.4f}")
        
        # Eliminar archivos temporales si se crearon
        try:
            if ref_path != reference_img_path and os.path.exists(ref_path):
                os.remove(ref_path)
            if comp_path != compare_img_path and os.path.exists(comp_path):
                os.remove(comp_path)
        except:
            pass
            
        return formatted_result
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    # Configurar argumentos
    parser = argparse.ArgumentParser(description='Verificación facial local')
    parser.add_argument('--reference', required=True, 
                        help='Ruta a la imagen de referencia')
    parser.add_argument('--compare', required=True, 
                        help='Ruta a la imagen de comparación')
    parser.add_argument('--output', help='Guardar resultado en archivo JSON')
    
    args = parser.parse_args()
    
    # Ejecutar verificación
    result = verify_faces_local(args.reference, args.compare)
    
    # Guardar resultado si se especificó
    if result and args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Resultado guardado en: {args.output}")
