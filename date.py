from datetime import datetime, timedelta

data_inicial = input("Digite a data inicial (formato YYYY-MM-DD): ")
periodo = int(input("Digite o período em dias: "))
intervalo = int(input("Digite o intervalo em dias: "))

data_atual = datetime.strptime(data_inicial, "%Y-%m-%d")
data_final = data_atual + timedelta(days=periodo)

while data_atual <= data_final:
    ida = data_atual

    for i in range(3):
        volta = ida + timedelta(days=intervalo+i)
    #volta = data_atual + timedelta(days=intervalo)

    
        print(ida.strftime("%Y-%m-%d"))
        print(volta.strftime("%Y-%m-%d"))



    data_atual += timedelta(days=1)
    print("=====")