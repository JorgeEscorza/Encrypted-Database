import MySQLdb
import config2
from base64 import b64decode
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Cipher import AES
from getpass import getpass

password = getpass()

def decrypt_data(encrypted_data, passwordSalt, nonce, tag, additional_data):
    # Decodificamos la información requerida
    encrypted_data = b64decode(encrypted_data)
    passwordSalt = b64decode(passwordSalt)
    nonce = b64decode(nonce)
    tag = b64decode(tag)

    # Derivamos la clave de cifrado a partir de la contraseña y la sal
    key = scrypt(password, passwordSalt, 32, N=2**14, r=8, p=1)

    # Ahora creamos un objeto AES para descifrar los datos
    aes_cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    aes_cipher.update(additional_data)

    # Intentamos descifrar los datos y verificamos la etiqueta de autenticación
    try:
        decrypted_data = aes_cipher.decrypt_and_verify(encrypted_data, tag)
    except ValueError as e:
        print("Error de autenticación. Los datos pueden haber sido manipulados.")
        raise e

    return decrypted_data.decode('utf-8')

try:
    # Conexión a la base de datos
    mydb = MySQLdb.connect(
        user=config2.user, 
        passwd=config2.password, 
        db=config2.dbname
    )
    cursor = mydb.cursor()

    # Solicitamos el nombre del paciente
    paciente = input("Introduzca el nombre del paciente: ")

    # Comprobamos que sea un nombre válido
    if any(char.isdigit() for char in paciente):
        raise ValueError("El nombre del paciente no puede contener números.")

    # Consultamos diagnóstico y tratamiento del paciente
    query = """SELECT diagnostico, tratamiento, passwordSalt, diag_nonce, treat_nonce, diag_tag, treat_tag 
               FROM expediente WHERE nombre = %s"""
    cursor.execute(query, (paciente,))

    # Obtenemos los resultados
    result = cursor.fetchone()

    # Comprobamos que exista el paciente en la BD o no
    if result:
        diagnosis_encrypted, treatment_encrypted, passwordSalt, diag_nonce, treat_nonce, diag_tag, treat_tag = result
        diagnosis = decrypt_data(diagnosis_encrypted, passwordSalt, diag_nonce, diag_tag, b'diagnosis')
        treatment = decrypt_data(treatment_encrypted, passwordSalt, treat_nonce, treat_tag, b'treatment')

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
    if 'mydb' in locals():
        mydb.close()
