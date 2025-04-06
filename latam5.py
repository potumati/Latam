from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
import os
import sys
import sqlite3




#python latam3.py --origin=GRU --destination=NYC --data_inicial=2025-11-01 --quantidade_dias_tentar=1 --tempo_de_viagem=7 --dias_a_mais_pode_durar=1

origin = ""
destination = ""
data_inicial = ""
quantidade_dias_tentar = ""
tempo_de_viagem = ""
dias_a_mais_pode_durar = ""


for argv in sys.argv:
    if "=" in argv:
        key, value = argv.split("=")
        if key == "--origin":
            origin = value
        elif key == "--destination":
            destination = value
        elif key == "--data_inicial":
            data_inicial = value
        elif key == "--quantidade_dias_tentar":
            quantidade_dias_tentar = int(value)
        elif key == "--tempo_de_viagem":
            tempo_de_viagem = int(value)
        elif key == "--dias_a_mais_pode_durar":
            dias_a_mais_pode_durar = int(value)

if origin == "":
    origin = input("Digite o aeroporto de origem (ex: GRU): ")
    if origin == "":
        origin = "GRU"

if destination == "":
    destination = input("Digite o aeroporto de destino (ex: MIA): ")
    if destination == "":
        destination = "NYC"

if data_inicial == "":
    data_inicial = input("Digite a data inicial (YYYY-MM-DD): ")
    if data_inicial == "":
        data_inicial = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

if quantidade_dias_tentar == "":
    quantidade_dias_tentar = input("Dias para tentar: ")
    if quantidade_dias_tentar == "":
        quantidade_dias_tentar = 9
quantidade_dias_tentar = int(quantidade_dias_tentar)

if tempo_de_viagem == "":
    tempo_de_viagem = input("Tempo de viagem (dias): ")
    if tempo_de_viagem == "":
        tempo_de_viagem = 6
tempo_de_viagem = int(tempo_de_viagem)

if dias_a_mais_pode_durar == "":
    dias_a_mais_pode_durar = input("Quantos dias a mais sua viagem pode durar? ")
    if dias_a_mais_pode_durar == "":
        dias_a_mais_pode_durar = 3
dias_a_mais_pode_durar = int(dias_a_mais_pode_durar)

data_atual = datetime.strptime(data_inicial, "%Y-%m-%d")
data_final = data_atual + timedelta(days=quantidade_dias_tentar)

# Conectar ao banco de dados SQLite (ou criar um novo arquivo de banco de dados)
db_name = f"resultados_voos{origin}-{destination}.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

hoje = datetime.now().strftime("%Y-%m-%d")

# Criar a tabela para armazenar os resultados, se ainda não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS voos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dia_consulta TEXT,
    ida TEXT,
    dia_da_semana_ida TEXT,
    ida_hora TEXT,
    volta TEXT,
    dia_da_semana_volta TEXT,
    dias_viagem INTEGER,
    tempo_de_voo TEXT,
    preco REAL,
    url TEXT
)
""")
conn.commit()
conn.close()

# Lista para armazenar os resultados
resultados = []

while data_atual <= data_final:
    ida = data_atual

    for i in range(dias_a_mais_pode_durar):
        volta = ida + timedelta(days=tempo_de_viagem + i)

        outbound = ida.strftime("%Y-%m-%dT16:00:00.000Z")
        inbound = volta.strftime("%Y-%m-%dT16:00:00.000Z")

        service = Service()
        options = webdriver.ChromeOptions()
        options.headless = True

        driver = webdriver.Chrome(service=service, options=options)
        url = f"https://www.latamairlines.com/br/pt/oferta-voos?origin={origin}&outbound={outbound}&destination={destination}&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=RECOMMENDED&inbound={inbound}"
        driver.get(url)

        driver.implicitly_wait(50)

        accept_cookies_button = driver.find_element(By.XPATH, "//button[@id='cookies-politics-button']")
        accept_cookies_button.click()

        list = driver.find_element(By.XPATH, "//ol[@aria-label='Voos disponíveis.']")
        list_items = list.find_elements(By.TAG_NAME, "li")
        list_items = [item for item in list_items if 'CreditCardBannerWrapper' not in item.get_attribute('class')]

        for item in list_items:
            # Localizar o elemento com data-testid que contém "flight-info-" e termina com "-origin"
            origin_elements = item.find_elements(By.XPATH, ".//div[contains(@data-testid, 'flight-info-') and contains(@data-testid, '-origin')]")

            if origin_elements:
                origin_time = origin_elements[0].text
            else:
                origin_time = "-"
                print("Origin time not found, skipping...")

            duration_elements = item.find_elements(By.XPATH, ".//div[contains(@class, 'flight-duration')]")
            if duration_elements:
                duration = duration_elements[0].text.replace("Duração\n", "")
            else:
                duration = "-"
                print("Duration not found, skipping...")
                continue

            price_elements = item.find_elements(By.XPATH, ".//div[contains(@class, 'displayAmount')]")
            for price_element in price_elements:
                price = price_element.text.replace("BRL ", "")

            # GET ONLY HOUR FROM DURATION
            if "h" in duration:
                duration = duration.split("h")[0].strip()
            else:
                duration = "0"

            # Ignore if duration is greater than 12 hours
            if int(duration) > 12:
                continue

            # Pegar apenas horário da origin_time (23:05\nGRU)
            origin_time = origin_time.split("\n")[0].strip()

            resultado = {
                "ida": ida.strftime("%Y-%m-%d"),
                "dia da semana": ida.strftime("%A"),
                "ida hora": origin_time,
                "volta": volta.strftime("%Y-%m-%d"),
                "dia da semana volta": volta.strftime("%A"),
                "dias viagem": (volta - ida).days,
                "tempo de vôo": duration,
                "preço": price,
                "url": url
            }

            price = price.replace("BRL ", "").replace(".", "").replace(",", ".")
            price = float(price)

            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()
            cursor.execute("""
    INSERT INTO voos (dia_consulta, ida, dia_da_semana_ida, ida_hora, volta, dia_da_semana_volta, dias_viagem, tempo_de_voo, preco, url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        hoje,
        resultado['ida'],
        resultado['dia da semana'],
        resultado['ida hora'],
        resultado['volta'],
        resultado['dia da semana volta'],
        resultado['dias viagem'],
        resultado['tempo de vôo'],
        price,
        resultado['url']
    ))
            conn.commit()
            conn.close()

            # Adicionar os resultados na lista
            resultados.append(resultado)

        driver.quit()
        print(f"Data: {ida.strftime('%Y-%m-%d')} - {volta.strftime('%Y-%m-%d')} - Resultados encontrados: {len(resultados)}")
    data_atual += timedelta(days=1)

# Mostrar todos os resultados juntos
for resultado in resultados:
    print(f"Ida: {resultado['ida']} - Dia da semana: {resultado['dia da semana']} - Volta: {resultado['volta']} - Dia da semana: {resultado['dia da semana volta']} - Duração viagem: {resultado['dias viagem']} dias - Tempo de vôo: {resultado['tempo de vôo']} horas - Preço: {resultado['preço']}")

df = pd.DataFrame(resultados)

# Salvar dados em arquivo HTML com tabela e link no URL
#df.to_html(f"resultados-{origin}-{destination}-{data_inicial}.html", index=False, escape=False, render_links=True)
#os.startfile(f"resultados-{origin}-{destination}-{data_inicial}.html")

# Salvar os resultados em um arquivo Excel
df.to_excel(f"resultados-{origin}-{destination}-{data_inicial}.xlsx", index=False)
#os.startfile(f"resultados-{origin}-{destination}-{data_inicial}.xlsx")

