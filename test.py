import pandas as pd

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')

print(credenziali)

username = 'gino'
password = 'gino'

if username in credenziali.Username.tolist():
    utente = credenziali[credenziali.Username == username]

    if list(utente.Password)[0] == password:
        

