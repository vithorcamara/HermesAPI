# Projeto de Detecção de Objetos e Consulta de Endereços com FastAPI

Este projeto é uma aplicação que combina duas funcionalidades principais:

1. **Detecção de Objetos em Imagens utilizando YOLOv3 e FastAPI**.
2. **Consulta de Endereços via CEP utilizando a API pública ViaCEP**.

## Funcionalidades

### 1. Detecção de Objetos com YOLOv3

- Permite o **upload de uma imagem** e realiza a detecção dos objetos presentes na imagem.
- Retorna as coordenadas das caixas delimitadoras e a confiança de cada detecção.
- Devolve a imagem processada com as caixas desenhadas ao redor dos objetos detectados.

### 2. Consulta de Endereços com ViaCEP

- Permite buscar informações detalhadas de um endereço a partir de um CEP fornecido.
- Integração com a API pública **ViaCEP** para retornar rua, bairro, cidade, estado e CEP.

---

## Requisitos

- **Python 3.x**
- **OpenCV**
- **NumPy**
- **FastAPI**
- **Uvicorn**
- **Pillow**
- **httpx**

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/vithorcamara/DetectorDeObjetos
   ```

2. Instale as dependências necessárias:
   ```bash
   pip install opencv-python numpy fastapi uvicorn pillow httpx
   ```

3. Baixe os arquivos do YOLOv3:
   - [YOLOv3 Config](https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg)
   - [YOLOv3 Weights](https://pjreddie.com/media/files/yolov3.weights)
   - [COCO Names](https://github.com/pjreddie/darknet/blob/master/data/coco.names)

4. Coloque os arquivos `yolov3.cfg`, `yolov3.weights` e `coco.names` no diretório do projeto.

---

## Como Usar

### 1. Detecção de Objetos

1. Execute a API com:
   ```bash
   uvicorn main:app --reload
   ```

2. Faça uma requisição `POST` para o endpoint `/detect/` com uma imagem para realizar a detecção de objetos.

### 2. Consulta de Endereços

1. Execute a API com:
   ```bash
   uvicorn main:app --reload
   ```

2. Faça uma requisição `GET` para o endpoint `/address/{cep}`, onde `{cep}` é o CEP desejado. A API retornará o endereço completo.

---

## Endpoints

### Detecção de Objetos

- **POST /detect/**: Faz o upload de uma imagem e retorna as detecções (objetos e coordenadas), além da imagem com as caixas delimitadoras.

### Consulta de Endereços

- **GET /address/{cep}**: Retorna o endereço completo com base no CEP fornecido. Se o CEP não for encontrado, a API retornará um erro.

---

## Estrutura do Projeto

```plaintext
.
├── yolov3.cfg
├── yolov3.weights
├── coco.names
├── main.py
└── README.md
```