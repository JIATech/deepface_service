from flask import Flask, request, jsonify
import os
import base64
import tempfile
from PIL import Image
import io
import logging
from deepface import DeepFace
import numpy as np
import cv2

app = Flask(__name__)

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/verify', methods=['POST'])
def verify_face():
    try:
        # Obtener datos de la solicitud
        data = request.json
        
        if not data or 'reference_image' not in data or 'compare_image' not in data:
            return jsonify({
                "error": "Se requieren las imágenes de referencia y comparación"
            }), 400
        
        # Decodificar imágenes base64
        try:
            reference_img_data = base64.b64decode(data['reference_image'])
            compare_img_data = base64.b64decode(data['compare_image'])
        except Exception as e:
            logger.error(f"Error en la decodificación base64: {str(e)}")
            return jsonify({"error": "Formato de imagen inválido"}), 400
        
        # Procesar las imágenes para garantizar compatibilidad con formatos como WebP
        def process_image(img_data):
            # Convertir los bytes de la imagen a un array numpy
            nparr = np.frombuffer(img_data, np.uint8)
            # Decodificar la imagen con OpenCV (soporta múltiples formatos incluyendo WebP)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                # Si OpenCV no puede decodificar, intentar con PIL
                try:
                    pil_img = Image.open(io.BytesIO(img_data))
                    # Convertir a RGB si es necesario
                    if pil_img.mode != 'RGB':
                        pil_img = pil_img.convert('RGB')
                    # Convertir a formato que OpenCV pueda manejar
                    img = np.array(pil_img)
                    # Convertir de RGB a BGR (formato que usa OpenCV)
                    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                except Exception as e:
                    logger.error(f"Error al procesar la imagen con PIL: {str(e)}")
                    raise ValueError("Formato de imagen no compatible")
            
            return img
        
        # Procesar imágenes
        try:
            ref_img = process_image(reference_img_data)
            comp_img = process_image(compare_img_data)
        except Exception as e:
            logger.error(f"Error procesando imágenes: {str(e)}")
            return jsonify({"error": "Error procesando las imágenes"}), 400
            
        # Crear archivos temporales para las imágenes convertidas
        ref_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
        comp_path = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False).name
        
        # Guardar las imágenes procesadas
        cv2.imwrite(ref_path, ref_img)
        cv2.imwrite(comp_path, comp_img)
        
        try:
            # Realizar la verificación con DeepFace
            result = DeepFace.verify(
                img1_path=ref_path,
                img2_path=comp_path,
                model_name='VGG-Face',
                distance_metric='cosine'
            )
            
            # Preparar la respuesta - convertir tipos NumPy a tipos nativos de Python
            response = {
                "verified": bool(result['verified']),  # Convertir bool_ a bool nativo
                "similarity": float(1 - result['distance'])  # Convertir a float nativo
            }
            
            return jsonify(response), 200
            
        except Exception as e:
            logger.error(f"Error en la verificación facial: {str(e)}")
            return jsonify({"error": f"Error en el procesamiento: {str(e)}"}), 500
        
        finally:
            # Limpiar archivos temporales
            try:
                os.remove(ref_path)
                os.remove(comp_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Error general: {str(e)}")
        return jsonify({"error": f"Error en el servicio: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7424))
    app.run(host='0.0.0.0', port=port, debug=False)
