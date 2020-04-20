### To Do's ###
# - Preguntar donde almacenar consulta
# Por default que se guarde en Desktop
# Hacer una GUI para seleccionar más facil la info
# auto generacion de reporte sobre rango de consulta

import datetime
from datetime import timedelta
import pandas as pd
import re

dia_i = int(input("Dia inicio: "))
mes_i = int(input("Mes inicio: "))
anio_i = int(input("Año inicio: "))

dia_f = int(input("Dia fin: "))
mes_f = int(input("Mes fin: "))
anio_f = int(input("Año fin: "))


while True:
    sistema = input("SIN BCA o BCS: ").upper()
    if sistema in ("SIN","BCA","BCS"):
        break
    else:
        continue

while True:
    proceso = input("MDA o MTR: ").upper()
    if proceso in ("MDA","MTR"):
        break
    else:
        continue

while True:
    tipo_nodo = input("Nodo P o D: ").upper()
    if tipo_nodo in ("P","D"):
        break
    else:
        continue

if tipo_nodo == "D":
    nodo = input("Introduce nombre nodo: ").upper()
else:
    while True:
        nodo = input("Inserta NodoP: ").upper()
        if re.match('^[0-9]{2}[A-Z]{3}-[0-9]{3}$', nodo):
            break
        else:
            print("El formato debe ser ##XXX-###")
            continue


url_base = (
    "https://ws01.cenace.gob.mx:8082/SWPML/SIM/"
    + sistema
    + "/"
    + proceso
    + "/"
    + nodo
    + "/{}/{}/{}/{}/{}/{}/"
    + "JSON"
)

# convierte en formato de fecha los valores ingresados en el inicio
fecha_i = datetime.datetime(anio_i, mes_i, dia_i)
fecha_f = datetime.datetime(anio_f, mes_f, dia_f)

# regresa la cantidad de dias entre la fecha de inicio y la fecha final
plazo = (fecha_f - fecha_i).days + 1

# si el plazo es menor a una semana, solo hará 1 ronda (consulta minima es de 1 semana)
if plazo < 7:
    rondas = 1
    # si el plazo es mayor a 7 días, se asignan rondas = al ultimo numero multiplo de 7 en el plazo
else:
    rondas = (plazo - plazo % 7) / 7

    # con eso cubres los dias que no entran en las rondas (si plazo = 31, rondas = 4, dias_restantes = 3)
dias_restantes = plazo - rondas * 7

# crea listas de "inicio" y "fin" de los rangos de busqueda
lista_1, lista_2 = list(), list()

for i in range(0, int(rondas)):
    lista_1.append((fecha_i + timedelta(days=(7 * i))))
    lista_2.append((fecha_i + timedelta(days=(7 * i)) + timedelta(days=6)))

    # considera los "dias restantes" que quedan fuera del rango
lista_3 = list()
for i in range(0, int(dias_restantes)):
    lista_3.append(fecha_i + timedelta(days=7 * rondas) + timedelta(days=i))

lista_urls = list()
for i in range(0, int(rondas)):
    lista_urls.append(
        url_base.format(
            lista_1[i].year,
            f"{lista_1[i].month:02}",
            f"{lista_1[i].day:02}",
            lista_2[i].year,
            f"{lista_2[i].month:02}",
            f"{lista_2[i].day:02}",
        )
    )

lista_urls.append(
    url_base.format(
        lista_3[0].year,
        f"{lista_3[0].month:02}",
        f"{lista_3[0].day:02}",
        lista_3[-1].year,
        f"{lista_3[-1].month:02}",
        f"{lista_3[-1].day:02}",
    )
)


def url_into_df(url):
    json = pd.read_json(url)["Resultados"][0]["Valores"]
    data_frame = pd.DataFrame(json)

    return data_frame


df = pd.DataFrame()

for urlz in lista_urls:
    df_nuevo = url_into_df(urlz)
    df = pd.concat((df, df_nuevo))


df.to_csv(
    "{} {}.{}.{} - {}.{}.{}.csv".format(
        nodo, anio_i, mes_i, dia_i, anio_f, mes_f, dia_f
    )
)
