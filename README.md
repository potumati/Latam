### README

# LATAM Flight Scraper

Este projeto é um **web scraper** desenvolvido em Python que utiliza a biblioteca **Selenium** para buscar informações de voos no site da LATAM Airlines. Ele permite configurar parâmetros como origem, destino, data inicial, período de busca e duração da viagem, e salva os resultados em arquivos **HTML**, **Excel** e em um banco de dados **SQLite**.

---

## **Requisitos**

Certifique-se de ter os seguintes itens instalados no seu sistema:

1. **Python 3.7+**
2. **Google Chrome** (última versão)
3. **ChromeDriver** compatível com a versão do Google Chrome instalado.

### **Instalar Dependências**

Execute o seguinte comando no terminal para instalar as bibliotecas necessárias:

```bash
pip install selenium pandas openpyxl
```

---

## **Como Usar**

### **1. Executar o Script**

No terminal, navegue até o diretório do projeto:

```bash
cd d:\dev\Testes\Python\Latam
```

Execute o script com os parâmetros desejados:

```bash
python latam3.py --origin=GRU --destination=NYC --data_inicial=2025-11-01 --quantidade_dias_tentar=1 --tempo_de_viagem=7 --dias_a_mais_pode_durar=1
```

### **2. Parâmetros Disponíveis**

| Parâmetro                  | Descrição                                                                 | Exemplo            |
|----------------------------|---------------------------------------------------------------------------|--------------------|
| `--origin`                 | Código do aeroporto de origem (IATA).                                    | `--origin=GRU`     |
| `--destination`            | Código do aeroporto de destino (IATA).                                   | `--destination=NYC`|
| `--data_inicial`           | Data inicial para a busca (formato `YYYY-MM-DD`).                        | `--data_inicial=2025-11-01` |
| `--quantidade_dias_tentar` | Número de dias para tentar buscar voos a partir da data inicial.          | `--quantidade_dias_tentar=1` |
| `--tempo_de_viagem`        | Duração da viagem em dias.                                                | `--tempo_de_viagem=7` |
| `--dias_a_mais_pode_durar` | Quantos dias a mais a viagem pode durar (margem de flexibilidade).        | `--dias_a_mais_pode_durar=1` |

---

## **Resultados**

Os resultados da busca serão salvos nos seguintes formatos:

1. **HTML**:
   - Um arquivo HTML será gerado com uma tabela contendo os resultados.
   - O arquivo será salvo no mesmo diretório do script com o nome `resultados-<origin>-<destination>-<data_inicial>.html`.

2. **Excel**:
   - Um arquivo Excel será gerado com os mesmos dados.
   - O arquivo será salvo no mesmo diretório do script com o nome `resultados-<origin>-<destination>-<data_inicial>.xlsx`.

3. **Exibição no Terminal**:
   - Os resultados também serão exibidos no terminal.

---

## **Exemplo de Saída**

### **Terminal**
```plaintext
Ida: 2025-11-01 - Dia da semana: Monday - Volta: 2025-11-08 - Dia da semana: Monday - Duração viagem: 7 dias - Tempo de vôo: 8 horas - Preço: 3440,25
Ida: 2025-11-02 - Dia da semana: Tuesday - Volta: 2025-11-09 - Dia da semana: Tuesday - Duração viagem: 7 dias - Tempo de vôo: 9 horas - Preço: 3500,00
```

### **HTML**
O arquivo HTML conterá uma tabela com os seguintes campos:
- Ida
- Dia da semana (ida)
- Ida hora
- Volta
- Dia da semana (volta)
- Dias de viagem
- Tempo de voo
- Preço
- URL

---

## **Banco de Dados SQLite**

Os resultados podem ser salvos em um banco de dados SQLite chamado `resultados_voos.db`. Para isso, você pode ajustar o código para incluir a funcionalidade de salvar no banco de dados.

### **Estrutura da Tabela**
```sql
CREATE TABLE voos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ida TEXT,
    dia_da_semana_ida TEXT,
    ida_hora TEXT,
    volta TEXT,
    dia_da_semana_volta TEXT,
    dias_viagem INTEGER,
    tempo_de_voo TEXT,
    preco TEXT,
    url TEXT
);
```

---

## **Notas**

1. **ChromeDriver**:
   - Certifique-se de que o ChromeDriver está instalado e compatível com a versão do Google Chrome no seu sistema.
   - Você pode baixar o ChromeDriver em: [https://chromedriver.chromium.org/downloads](https://chromedriver.chromium.org/downloads).

2. **Modo Headless**:
   - O script está configurado para rodar no modo headless (sem abrir o navegador). Para visualizar o navegador, remova ou comente a linha:
     ```python
     options.headless = True
     ```

3. **Erros Comuns**:
   - **Botão de cookies não encontrado**: Certifique-se de que o site da LATAM não mudou sua estrutura.
   - **Versão incompatível do ChromeDriver**: Atualize o ChromeDriver para a versão correta.

---

## **Licença**

Este projeto é de uso livre e está sob a licença MIT.
