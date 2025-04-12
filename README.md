# AES-256 Encryption in CTR Mode with PBKDF2
This repository stores a way to configure a database which encrypts sensitive hospital data (or any kind of data) 
using AES-256 encryption algorithm.

## How to Start
```
$ python3 encrypt.py
```

## Package Installation
Make sure the following packages are installed on your system (I used a virtual machine with Debian 12).
```
# apt install mariadb-server python3-pycryptodome python3-mysqldb python3-securestring
```

## Database Schema Setup
```
# mysql < hospital_scheme.sql
```

## Tested versions
- Debian GNU/Linux 12
- Mariadb 10.11.6 
- Python 3.11.2
- PyCryptodome 3.11.0
- MySQLdb 1.4.6
- SecureString 0.2

## References
- https://cryptobook.nakov.com/
- https://pycryptodome.readthedocs.io/
- https://mysqlclient.readthedocs.io/
- https://www.sjoerdlangkemper.nl/2016/05/22/should-passwords-be-cleared-from-memory/
- https://www.sjoerdlangkemper.nl/2016/06/09/clearing-memory-in-python/

If you found this project interesting and want to collaborate, feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/jorge-luis-escorza-s%C3%A1nchez-9ab935325/).
I'm always open to new projects, opportunities and collaborations!
