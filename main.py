from machine import Pin, SoftI2C
from HangmanGame.pico_i2c_lcd import I2cLcd
from time import sleep

#LCD Setup
i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
lcd = I2cLcd(i2c, 0x27, 4, 20)

#Botões 
bot_direita = Pin(10, Pin.IN, Pin.PULL_UP)
bot_ok = Pin(11, Pin.IN, Pin.PULL_UP)
bot_esquerda = Pin(12, Pin.IN, Pin.PULL_UP)

#Jogo
palavra = "TESTE"
letras_descobertas = ["_"] * len(palavra)
alfabeto = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alfabeto_game = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
indice_letra = 0
letras_usadas = []
erros = 0
max_erros = 6

seta_esquerda = bytearray([
    0b00010,
    0b00110,
    0b01110,
    0b11110,
    0b01110,
    0b00110,
    0b00010,
    0b00000
])
lcd.custom_char(0, seta_esquerda)

seta_direita = bytearray([
    0b01000,
    0b01100,
    0b01110,
    0b01111,
    0b01110,
    0b01100,
    0b01000,
    0b00000
])
lcd.custom_char(1, seta_direita)

def init():
    global letras_descobertas, letras_usadas, indice_letra, erros
    letras_descobertas = ["_"] * len(palavra)
    letras_usadas = []
    indice_letra = 0
    erros = 0
    lcd.clear()
    lcd.putstr("JOGO DA FORCA")
    sleep(1)
    alfabeto_game = alfabeto
    atualizar_display()


def mostrar_letras_vizinhas():
    lcd.move_to(11, 0)
    for i in range(-3, 4):  # mostra 2 antes e 1 depois da atual
        idx = (indice_letra + i) % len(alfabeto_game)  # índice circular
        if(idx==indice_letra):
            lcd.putchar(chr(1))  # Esquerda
            lcd.putstr(alfabeto_game[idx])
            lcd.putchar(chr(0)) 
        else: lcd.putstr(alfabeto_game[idx])
    
    
    
def atualizar_display():
    lcd.clear()
    lcd.move_to(0, 0)
    lcd.putstr("".join(letras_descobertas))
    mostrar_letras_vizinhas()
    lcd.move_to(0, 1)
    lcd.putstr(f"{alfabeto[indice_letra]} X:{erros}")

init()

while True:
    atualizou = False  # controle de atualização

    #Botão: Avançar letra
    if not bot_direita.value():  
        indice_letra = (indice_letra + 1) % len(alfabeto)
        atualizou = True
        sleep(0.2)
        
    if not bot_esquerda.value(): 
        indice_letra = (indice_letra - 1) % len(alfabeto)
        atualizou = True
        sleep(0.2)

    #Confirmar letra
    if not bot_ok.value():
        letra = alfabeto_game[indice_letra]
        alfabeto_game[indice_letra] = "*"
        if letra not in letras_usadas:
            letras_usadas.append(letra)
            if letra in palavra:
                for i, l in enumerate(palavra):
                    if l == letra:
                        letras_descobertas[i] = letra
            else:
                erros += 1
            atualizou = True
        else:
            lcd.clear()
            lcd.putstr("Ja usada!")
            sleep(1)
            atualizou = True
        sleep(0.2)

    # --- Vitória ---
    if "_" not in letras_descobertas:
        lcd.clear()
        lcd.putstr("Voce venceu!")
        lcd.move_to(0, 1)
        lcd.putstr(f'A Palavra era:')
        lcd.move_to(0, 2)
        lcd.putstr(f'"{palavra}"')
        sleep(3)
        init()
        continue

    # Derrota
    if erros >= max_erros:
        lcd.clear()
        lcd.putstr("Game Over :(")
        lcd.move_to(0, 1)
        lcd.putstr(f"{palavra}")
        sleep(3)
        init()
        continue

    # Atualizacao
    if atualizou:
        atualizar_display()


