import urllib.request
import re

print("A procurar os IDs no site do SIGAA da UnB...")

url = "https://sigaa.unb.br/sigaa/public/turmas/listar.jsf"
# Fazer o pedido fingindo ser um navegador comum
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    # Procurar todas as opções no código HTML
    opcoes = re.findall(r'(.*?)', html)
    
    print("\n--- IDs Encontrados ---")
    for id_depto, nome in opcoes:
        nome_upper = nome.upper()
        if "COMPUTA" in nome_upper or "MATEM" in nome_upper or "FÍSIC" in nome_upper:
            print(f"ID: {id_depto} -> {nome.strip()}")
            
except Exception as e:
    print(f"Erro ao aceder ao SIGAA: {e}")