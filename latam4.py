from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import pandas as pd
import os
import sys


def parse_arguments():
    """Parse os argumentos passados via linha de comando."""
    args = {
        "origin": "",
        "destination": "",
        "data_inicial": "",
        "quantidade_dias_tentar": "",
        "tempo_de_viagem": "",
        "dias_a_mais_pode_durar": ""
    }

    for argv in sys.argv:
        if "=" in argv:
            key, value = argv.split("=")
            if key in args:
                args[key] = value if key == "data_inicial" else int(value)

    return args


def get_user_inputs(args):
    """Solicite entradas do usuário para os parâmetros que não foram fornecidos."""
    if not args["origin"]:
        args["origin"] = input("Digite o aeroporto de origem (ex: GRU): ") or "GRU"

    if not args["destination"]:
        args["destination"] = input("Digite o aeroporto de destino (ex: MIA): ") or "NYC"

    if not args["data_inicial"]:
        args["data_inicial"] = input("Digite a data inicial (YYYY-MM-DD): ") or \
                               (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

    if not args["quantidade_dias_tentar"]:
        args["quantidade_dias_tentar"] = int(input("Dias para tentar: ") or 9)

    if not args["tempo_de_viagem"]:
        args["tempo_de_viagem"] = int(input("Tempo de viagem (dias): ") or 6)

    if not args["dias_a_mais_pode_durar"]:
        args["dias_a_mais_pode_durar"] = int(input("Quantos dias a mais sua viagem pode durar? ") or 3)

    return args


def scrape_flights(args):
    """Realiza o scraping dos voos e retorna os resultados."""
    data_atual = datetime.strptime(args["data_inicial"], "%Y-%m-%d")
    data_final = data_atual + timedelta(days=args["quantidade_dias_tentar"])
    resultados = []

    while data_atual <= data_final:
        ida = data_atual

        for i in range(args["dias_a_mais_pode_durar"]):
            volta = ida + timedelta(days=args["tempo_de_viagem"] + i)
            outbound = ida.strftime("%Y-%m-%dT16:00:00.000Z")
            inbound = volta.strftime("%Y-%m-%dT16:00:00.000Z")

            url = f"https://www.latamairlines.com/br/pt/oferta-voos?origin={args['origin']}&outbound={outbound}&destination={args['destination']}&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=RECOMMENDED&inbound={inbound}"
            driver = setup_driver(url)

            try:
                accept_cookies(driver)
                resultados.extend(process_flight_list(driver, ida, volta, url))
            except Exception as e:
                print(f"Erro ao processar a página: {e}")
            finally:
                driver.quit()

        data_atual += timedelta(days=1)

    return resultados


def setup_driver(url):
    """Configura e retorna o driver do Selenium."""
    service = Service()
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    driver.implicitly_wait(50)
    return driver


def accept_cookies(driver):
    """Aceita os cookies, se o botão estiver presente."""
    try:
        accept_cookies_button = driver.find_element(By.XPATH, "//button[@id='cookies-politics-button']")
        accept_cookies_button.click()
    except:
        print("Botão de cookies não encontrado, continuando...")


def process_flight_list(driver, ida, volta, url):
    """Processa a lista de voos e retorna os resultados."""
    resultados = []
    list = driver.find_element(By.XPATH, "//ol[@aria-label='Voos disponíveis.']")
    list_items = list.find_elements(By.TAG_NAME, "li")
    list_items = [item for item in list_items if 'CreditCardBannerWrapper' not in item.get_attribute('class')]

    for item in list_items:
        origin_time = extract_element_text(item, ".//div[contains(@data-testid, 'flight-info-') and contains(@data-testid, '-origin')]")
        duration = extract_element_text(item, ".//div[contains(@class, 'flight-duration')]", "Duração\n")
        price = extract_element_text(item, ".//div[contains(@class, 'displayAmount')]", "BRL ")

        if not origin_time or not duration or not price:
            continue

        duration_hours = extract_duration_hours(duration)
        if duration_hours > 12:
            continue

        resultados.append({
            "ida": ida.strftime("%Y-%m-%d"),
            "dia da semana": ida.strftime("%A"),
            "ida hora": origin_time.split("\n")[0].strip(),
            "volta": volta.strftime("%Y-%m-%d"),
            "dia da semana volta": volta.strftime("%A"),
            "dias viagem": (volta - ida).days,
            "tempo de vôo": duration_hours,
            "preço": price,
            "url": url
        })

    return resultados


def extract_element_text(item, xpath, replace_text=""):
    """Extrai o texto de um elemento, se existir."""
    elements = item.find_elements(By.XPATH, xpath)
    if elements:
        return elements[0].text.replace(replace_text, "").strip()
    return None


def extract_duration_hours(duration):
    """Extrai apenas as horas da duração."""
    if "h" in duration:
        return int(duration.split("h")[0].strip())
    return 0


def save_results(resultados, origin, destination, data_inicial):
    """Salva os resultados em arquivos HTML e Excel."""
    df = pd.DataFrame(resultados)

    # Salvar em HTML
    html_file = f"resultados-{origin}-{destination}-{data_inicial}.html"
    df.to_html(html_file, index=False, escape=False, render_links=True)
    os.startfile(html_file)

    # Salvar em Excel
    excel_file = f"resultados-{origin}-{destination}-{data_inicial}.xlsx"
    df.to_excel(excel_file, index=False)
    os.startfile(excel_file)


if __name__ == "__main__":
    args = parse_arguments()
    args = get_user_inputs(args)
    resultados = scrape_flights(args)
    save_results(resultados, args["origin"], args["destination"], args["data_inicial"])