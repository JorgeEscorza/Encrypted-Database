import MySQLdb
import config
from base64 import b64decode
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512
from Cryptodome.Cipher import AES
from getpass import getpass

password = getpass()

def decrypt_data(encrypted_data, salt, nonce):
    # Decodificamos la información requerida
    encrypted_data = b64decode(encrypted_data)
    salt = b64decode(salt)
    nonce = b64decode(nonce)

    # Derivamos la clave de cifrado a partir de la contraseña y la sal
    key = PBKDF2(password, salt, 32, count=1000000, hmac_hash_module=SHA512)

    # Ahora creamos un objeto AES para descifrar los datos y los desciframos
    aes_cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
    decrypted_data = aes_cipher.decrypt(encrypted_data)

    return decrypted_data.decode('utf-8')

try:
    # Conexión a la base de datos
    mydb = MySQLdb.connect(
        user=config.user, 
        passwd=config.password, 
        db=config.dbname)
    cursor = mydb.cursor()

    # Solicitamos el nombre del paciente
    paciente = input("Introduzca el nombre del paciente: ")

    # Comprobamos que sea un nombre válido
    if any(char.isdigit() for char in paciente):
        raise ValueError("El nombre del paciente no puede contener números.")

    # Consultamos diagnóstico y tratamiento del paciente
    query = "SELECT diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce FROM expediente WHERE nombre = %s"
    cursor.execute(query, (paciente,))

    # Obtenemos los resultados
    result = cursor.fetchone()

    # Comprobamos que exista el paciente en la BD o no
    if result:
        diagnosis_encrypted, treatment_encrypted, passwordSalt, diag_nonce, treat_nonce = result
        diagnosis = decrypt_data(diagnosis_encrypted, passwordSalt, diag_nonce)
        treatment = decrypt_data(treatment_encrypted, passwordSalt, treat_nonce)

        print(f"{paciente}:")
        print(f"Diagnóstico: {diagnosis}")
        print(f"Tratamiento: {treatment}")
    else:
        print(f"No se encontró al paciente {paciente}.")

except MySQLdb.Error as err:
    print(f"Error: {err}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'db' in locals():
        mydb.close()
