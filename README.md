# Stechs-challenge
Repo para el challenge de Stechs  
A continuación se explican los paso a paso para testear el servidor construido una vez descargado el contenido de este repositorio.

# Instalar las dependencias necesarias:
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential pkg-config mysql-server snmp  

pip3 install -r stechsproject/requirements.txt  

# Configurar la DB:
sudo mysql -u root  

CREATE DATABASE stechs_challenge;  
 
CREATE USER 'django'@'localhost' IDENTIFIED BY 'stechs';  

exit;  

sudo mysql -u root stechs_challenge < /archivos_externos/challenge_db.sql  

# Aplicar las migraciones de django
cd stechsproject  

python3 manage.py migrate cablemodems.py 0001_initial --fake (Como cargamos la DB desde el dump tenemos que fakear esta migración)  

python3 manage.py migrate  

# Correr el agente SNMP 
snmpsimd.py --data-dir=./archivos_externos --agent-udpv4-endpoint=127.0.0.1:1024  

# Pegar contra el endpoint
HTPP POST Request a "http://127.0.0.1:8000/api/device/inventory/cm/48f7c0900592"  


Ejemplo de respuesta:   
{  

  "errorCode": 409,  
  
  "errorStr": "Cable Modem info already stored",  
  
  "result": "failure",  
  
  "items": {}  
  
}  


