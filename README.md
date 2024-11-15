# Instrucciones para instalar (en windows) 

Nota: se requieren llaves con creditos para las APIs de [fireworks.ai](https://docs.fireworks.ai/getting-started/quickstart#windows) y [openai](https://platform.openai.com/docs/quickstart?desktop-os=windows#create-and-export-an-api-key).

1- Descargar el repositorio
```bash
git clone <>
```

2- Crear un ambiente virtual de python (recomendado)

Entrar a la carpeta del respositorio descargado y crear un ambien virtual
```bash
python -m venv .venv
```
Activar el ambiente virual
```bash
source .venv/Scripts/activate
```
3- Instalar paquetes necesarios

Paquetes que usa el programa principal

```bash
pip install fireworks-ai
pip install openai
pip install nltk
pip install pandas
```
Paquetes que usa campion
```bash
pip install git+https://github.com/batfish/pybatfish.git@new-docs
pip install setuptools
```
Nota: campion parece estar implementado con la version de pybatfish de la rama que aparece el primer comando anterior

4- Crear una carpeta llamada "configs" dentro de la carpeta de "campion_workplace"

5- Descargar imagen de campion de docker
```bash
docker pull modnetv/campion
```

6- Correr imagen de campion
```
docker run --name campion -p 9997:9997
```
Nota: es necesario correr este comando la primera vez para que se asignen correctamente los puertos. En veces sucesivas es suficiente encender el contenedor desde la interfaz de docker.

7- Correr el programa principal
```bash
py run_scenario.py <nombre del modelo> <tecnica de prompt engineering> [numero de caso unico | numeros de primer caso y ultimo caso]
```
Ejemplos:
```bash
py run_scenario.py llama90B zs 5
py run_scenario.py gpt4o fscot 4 7
```