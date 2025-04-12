#!/usr/bin/env python3

from getpass import getpass
from base64 import b64encode
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import MySQLdb
import config2
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
        user=config2.user,
        passwd=config2.password,
        db=config2.dbname
    )
    cursor = mydb.cursor()

    # Procesar cada registro
    for record_id, record in data.items():
        name = record['name']
        diagnosis = bytes(record['diagnosis'], 'utf-8')
        treatment = bytes(record['treatment'], 'utf-8')

        # Generar salt y clave con scrypt
        passwordSalt = get_random_bytes(16)
        key = scrypt(password, passwordSalt, 32, N=2**14, r=8, p=1)

        # Generar nonce y cifrar con AES GCM
        nonce = get_random_bytes(8)
        nonce2 = get_random_bytes(8)
        aes_cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        # Info adicional
        aes_cipher.update(b'diagnosis')
        diagnosis_ciphertext = aes_cipher.encrypt(diagnosis)
        diagnosis_tag = aes_cipher.digest()

        # Reiniciamos el objeto AES para cifrar el tratamiento (y que se pueda usar otra vez)
        aes_cipher = AES.new(key, AES.MODE_GCM, nonce=nonce2)

        # Info adicional
        aes_cipher.update(b'treatment')
        treatment_ciphertext = aes_cipher.encrypt(treatment)
        treatment_tag = aes_cipher.digest()

        # Codificar en base64
        passwordSalt = b64encode(passwordSalt).decode('utf-8')
        diagnosis_ciphertext = b64encode(diagnosis_ciphertext).decode('utf-8')
        treatment_ciphertext = b64encode(treatment_ciphertext).decode('utf-8')
        diagnosis_nonce = b64encode(nonce).decode('utf-8')
        treatment_nonce = b64encode(nonce2).decode('utf-8')
        diagnosis_tag = b64encode(diagnosis_tag).decode('utf-8')
        treatment_tag = b64encode(treatment_tag).decode('utf-8')

        # Insertar en la base de datos
        insert_query = """INSERT INTO expediente (nombre, diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce, diag_tag, treat_tag) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        record_to_insert = (name, diagnosis_ciphertext, treatment_ciphertext, passwordSalt, diagnosis_nonce, treatment_nonce, diagnosis_tag, treatment_tag)
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

# Función que sobreescribe el contenido de las variables (reemplaza con caracteres nulos)
def clearmem(data):
    if isinstance(data, str):
        data = list(data)
        for i in range(len(data)):
            data[i] = '\x00'
        data = ''.join(data)
    elif isinstance(data, bytes):
        data = bytearray(data)
        for i in range(len(data)):
            data[i] = 0
    elif isinstance(data, bytearray):
        for i in range(len(data)):
            data[i] = 0
    else:
        raise TypeError("Unsupported data type for clearing memory")
    return data

key = clearmem(key)
password = clearmem(password)
diagnosis = clearmem(diagnosis)
treatment = clearmem(treatment)

print("\nVariables después de sobreescribir su contenido:")
print(f"AES encryption key: '{key}'")
print(f"Password: '{password}'")
print(f"Diagnosis: '{diagnosis}'")
print(f"Treatment: '{treatment}'")
