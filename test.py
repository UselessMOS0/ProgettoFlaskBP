import pandas as pd

credenziali = pd.read_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv')

print(credenziali)

utente = {"Username": 'gino',"Password": 'gino'}

credenziali = credenziali.append(utente,ignore_index=True)

print(credenziali)


credenziali.to_csv('/workspace/ProgettoFlaskBP/static/Files/credenziali.csv',index=False)