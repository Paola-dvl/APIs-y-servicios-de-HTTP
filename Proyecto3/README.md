venv se instala en la carpeta 
Instalar pipenv
pip install pipenv

Activar pip venv
python3 -m venv venv
source venv/bin/activate o venv\Scripts\activate

pip install -r requirements.txt

Desactivar pip venv
pip freeze > requirements.txt
deactivate

Ejecutar DJango (Verificar siempre que estes en venv)
python Frontend/manage.py runserver

Ejecutar Flask (Verificar siempre que estes en venv)
python Backend/Servicio2.py