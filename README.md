# eventos
Aplicación web para venta de entradas a eventos

## Aplicar entorno virtual
python -m venv env

## Activar entorno virtual
- Linux/Mac: source env/bin/activate
- Windows: source env/Scripts/activate   o   .\venv\Scripts\Activate
- Windows (alternativa): ./env/Scripts.activate

## Instalar dependencias
pip install -r requirements

## Instalar el interface de Django
pip install django-admin-interface

## Instalar el tema de admin desde fixture
python manage.py loaddata theme_fixture.json

## Hacer migraciones
python manage.py migrate

## Poblar base de datos 
python manage.py puebla_datos

## Correr app
python manage.py runserver

## Agregar cambios
git add .
git commit -m " ejem : hice un cambio"

## Subir cambios al repositorio remoto
git push origin main

## crear una rama
git branch nombre-de-la-rama

## cambiarse de rama
git checkout nombre-de-la-rama

## crear y cambiarse de rama
git checkout -b nombre-de-la-rama

## subir a una rama del repositorio
git push -u origin nombre-de-la-rama

## agregar los cambios
git add .

## ver cambios que hiciste y no te acordas
git status

# Permisos:
# CLIENTES
Solo pueden ver eventos existentes.
Pueden crear, editar y eliminar comentarios propios.
Pueden crear solicitudes de reembolso.
Pueden ver notificaciones.
Pueden crear, editar y eliminar calificaciones.
Pueden comprar tickets.
Pueden agregar/eliminar favoritos.

# VENDEDORES
Pueden acceder al admin.
Pueden ver eventos existentes y ya ocurridos.
No pueden crear ni eliminar eventos, solo editarlos.
Pueden editar y eliminar comentarios propios y ajenos.
Pueden aceptar o rechazar reembolsos.
Pueden editar/eliminar tickets únicamente si hay reembolso aceptado.
Pueden crear, editar y eliminar notificaciones.
Pueden crear y editar calificaciones.
No pueden manipular categorías o venues.