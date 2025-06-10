# eventos
Aplicación web para venta de entradas a eventos

## Aplicar entorno virtual
python -m venv env

## Activar entorno virtual
- Linux/Mac: source env/bin/activate
- Windows: source env/Scripts/activate
- Windows (alternativa): ./env/Scripts.activate

## Instalar dependencias
pip install -r requirements

## Hacer migraciones
python manage.py migrate

## Llenar base de datos con fixture
python manage.py loaddata events.json

## Correr app
python manage.py runserver

## Agregar cambios
git add .
git commit -m " ejem : hice un cambio"

## Subir cambios al repositorio remoto
git push origin main


