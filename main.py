from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import httpx
from typing import List
import cv2
import numpy as np
import uvicorn
import os
from io import BytesIO
from PIL import Image
import base64

app = FastAPI()

# URL base para o ViaCEP (ou outra API de CEP)
VIA_CEP_URL = "https://viacep.com.br/ws/{cep}/json/"

class Address(BaseModel):
    street: str
    neighborhood: str
    city: str
    state: str
    postal_code: str

@app.get("/address/{cep}", response_model=Address)
async def get_address(cep: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(VIA_CEP_URL.format(cep=cep))
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="CEP not found")
        
        data = response.json()
        
        # Verifica se a resposta contém os dados esperados
        if 'erro' in data:
            raise HTTPException(status_code=404, detail="CEP not found")
        
        address = Address(
            street=data.get('logradouro', ''),
            neighborhood=data.get('bairro', ''),
            city=data.get('localidade', ''),
            state=data.get('uf', ''),
            postal_code=data.get('cep', '')
        )
        
        return address

# Defina os caminhos absolutos para os arquivos necessários
base_path = os.path.dirname(__file__)
labels_path = os.path.join(base_path, 'coco.names')
config_path = os.path.join(base_path, 'yolov3.cfg')
weights_path = os.path.join(base_path, 'yolov3.weights')

# Função para carregar nomes das classes
def get_classes(file):
    with open(file, 'r') as f:
        classes = f.read().strip().split("\n")
    return classes

# Função para redimensionar a imagem mantendo a proporção
def resize_with_aspect_ratio(image, width=None, height=None, inter=cv2.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    resized = cv2.resize(image, dim, interpolation=inter)
    return resized

# Função para desenhar as bordas ao redor dos objetos detectados
def draw_boxes(image_np, detections):
    for detection in detections:
        x, y, w, h = detection['box']['x'], detection['box']['y'], detection['box']['w'], detection['box']['h']
        class_name = detection['class']
        confidence = detection['confidence']
        
        color = [int(c) for c in np.random.randint(0, 255, size=(3,))]
        cv2.rectangle(image_np, (x, y), (x + w, y + h), color, 2)
        text = f"{class_name}: {confidence:.2f}"
        cv2.putText(image_np, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return image_np

# Função para processar a imagem
def detect_objects(image_np):
    (H, W) = image_np.shape[:2]
    blob = cv2.dnn.blobFromImage(image_np, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    layer_outputs = net.forward(ln)

    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.5:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    detections = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            detections.append({
                "class": classes[class_ids[i]],
                "confidence": confidences[i],
                "box": {"x": x, "y": y, "w": w, "h": h}
            })

    return detections

# Carregar as classes e a rede YOLO
classes = get_classes(labels_path)
net = cv2.dnn.readNetFromDarknet(config_path, weights_path)

@app.post("/detect/")
async def detect_objects_route(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = Image.open(BytesIO(image_bytes))
    image_np = np.array(image.convert('RGB'))
    image_np = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    image_np = resize_with_aspect_ratio(image_np, width=640)

    detections = detect_objects(image_np)
    image_np = draw_boxes(image_np, detections)

    # Converta a imagem processada para base64
    _, buffer = cv2.imencode('.jpg', image_np)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return {"detections": detections, "image": encoded_image}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
