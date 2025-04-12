#!/usr/bin/env python3

from getpass import getpass
from base64 import b64encode
from SecureString import clearmem
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512
from Cryptodome.Random import get_random_bytes
from Cryptodome.Cipher import AES
import MySQLdb
import config
import sys
import ast

# Se obtiene la contraseña para cifrar los datos
password = getpass()

# Leer archivo de datos
with open('diagnosticos_tratamientos.txt', 'r', encoding='utf-8') as f:
    file_content = f.read()
    data = ast.literal_eval(file_content)

# Conexión a la base de datos
try:
    mydb = MySQLdb.connect(
        user=config.user,
        passwd=config.password,
        db=config.dbname
    )
    cursor = mydb.cursor()

    # Procesar cada registro
    for record_id, record in data.items():
        name = record['name']
        diagnosis = bytes(record['diagnosis'], 'utf-8')
        treatment = bytes(record['treatment'], 'utf-8')

        # Generar salt y clave
        passwordSalt = get_random_bytes(16)
        key = PBKDF2(password, passwordSalt, 32, count=1000000, hmac_hash_module=SHA512)

        # Generar nonces y cifrar
        diagnosis_nonce = get_random_bytes(8)
        treatment_nonce = get_random_bytes(8)
        diag_aes = AES.new(key, AES.MODE_CTR, nonce=diagnosis_nonce)
        treat_aes = AES.new(key, AES.MODE_CTR, nonce=treatment_nonce)

        diagnosis_ciphertext = diag_aes.encrypt(diagnosis)
        treatment_ciphertext = treat_aes.encrypt(treatment)

        # Codificar en base64
        passwordSalt = b64encode(passwordSalt).decode('utf-8')
        diagnosis_ciphertext = b64encode(diagnosis_ciphertext).decode('utf-8')
        treatment_ciphertext = b64encode(treatment_ciphertext).decode('utf-8')
        diagnosis_nonce = b64encode(diagnosis_nonce).decode('utf-8')
        treatment_nonce = b64encode(treatment_nonce).decode('utf-8')

        # Insertar en la base de datos
        insert_query = """INSERT INTO expediente (nombre, diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce) 
                          VALUES (%s, %s, %s, %s, %s, %s)"""
        record_to_insert = (name, diagnosis_ciphertext, treatment_ciphertext, passwordSalt, diagnosis_nonce, treatment_nonce)
        cursor.execute(insert_query, record_to_insert)

    mydb.commit()
    print("Records inserted successfully")

except Exception as err:
    print(f"\nSomething went wrong: {err}")
    sys.exit()

finally:
    if mydb:
        cursor.close()
        mydb.close()
        print("DBMS connection is closed")

# Sobrescribir el contenido de las variables para evitar que se
# puedan obtener los datos a través de un volcado de memoria RAM
clearmem(key)
clearmem(password)
clearmem(diagnosis)
clearmem(treatment)

print("\nVariables después de sobreescribir su contenido:")
print(f"AES encryption key: '{key.hex()}'")
print(f"Password: '{password}'")
print(f"Diagnosis: '{diagnosis}'")
print(f"Treatment: '{treatment}'")
