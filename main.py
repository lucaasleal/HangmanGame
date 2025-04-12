from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
from time import sleep
from random import choice
from temas import *  # Importa o dicionário de temas e palavras

# ---------------------------
# Configuração do LCD 20x4 via I2C
# ---------------------------
i2c = SoftI2C(sda=Pin(4), scl=Pin(5), freq=400000)
lcd = I2cLcd(i2c, 0x27, 4, 20)

# ---------------------------
# Definição dos botões físicos
# ---------------------------
bot_direita = Pin(12, Pin.IN, Pin.PULL_UP)
bot_ok = Pin(11, Pin.IN, Pin.PULL_UP)
bot_esquerda = Pin(10, Pin.IN, Pin.PULL_UP)

# ---------------------------
# Variáveis globais de jogo
# ---------------------------
letras_descobertas = []
alfabeto = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alfabeto_game = alfabeto.copy()
indice_letra = 0
letras_usadas = []
erros = 0
max_erros = 6

# ---------------------------
# Caracteres personalizados no LCD (setas e boneco)
# ---------------------------
seta_esquerda = bytearray([0b00010, 0b00110, 0b01110, 0b11110, 0b01110, 0b00110, 0b00010, 0b00000])
seta_direita  = bytearray([0b01000, 0b01100, 0b01110, 0b01111, 0b01110, 0b01100, 0b01000, 0b00000])
lcd.custom_char(0, seta_esquerda)
lcd.custom_char(1, seta_direita)

head       = bytearray([0b00100, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110, 0b00100])
body       = bytearray([0b00100, 0b01110, 0b10101, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100])
arm_left   = bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b00001, 0b00010, 0b00000, 0b00000])
arm_right  = bytearray([0b00000, 0b00000, 0b00000, 0b00000, 0b10000, 0b01000, 0b00000, 0b00000])
leg_left   = bytearray([0b00100, 0b01000, 0b01000, 0b10000, 0b10000, 0b10000, 0b00000, 0b00000])
leg_right  = bytearray([0b00100, 0b01010, 0b01010, 0b10001, 0b10001, 0b10001, 0b00000, 0b00000])
lcd.custom_char(2, head)
lcd.custom_char(3, body)
lcd.custom_char(4, arm_left)
lcd.custom_char(5, arm_right)
lcd.custom_char(6, leg_left)
lcd.custom_char(7, leg_right)

# ---------------------------
# Função de inicialização
# ---------------------------
def init():
    global letras_descobertas, letras_usadas, indice_letra, erros, alfabeto_game, palavra
    letras_descobertas = []
    letras_usadas = ["*"]
    indice_letra = 0
    erros = 0
    alfabeto_game = alfabeto.copy()
    
    lcd.clear()

    # Tela inicial com efeito piscante
    counter = 0
    while bot_ok.value():
        lcd.move_to(4, 0)
        lcd.putstr("H_NGM_N G_ME" if counter % 2 == 0 else "HANGMAN GAME")
        lcd.move_to(4, 3)
        lcd.putstr("RED -> Jogar")
        counter += 1
        sleep(0.5)

    lcd.clear()
    tema_escolhido = selecionar_tema()
    palavra = choice(temas[tema_escolhido]).upper()

    for letra in palavra:
        letras_descobertas.append('_' if letra != ' ' else ' ')
    
    sleep(1)
    atualizar_display()

# ---------------------------
# Seleção de tema
# ---------------------------
def selecionar_tema():
    opcoes = list(temas.keys())
    indice = 0

    while True:
        lcd.clear()
        lcd.move_to(2, 0)
        lcd.putstr("SELECIONE O TEMA")
        lcd.move_to(2, 1)
        lcd.putstr(opcoes[indice])
        lcd.move_to(7, 2)
        lcd.putchar(chr(0)); lcd.putstr(" OU "); lcd.putchar(chr(1))
        lcd.move_to(3, 3)
        lcd.putstr("RED -> confirma")

        while True:
            if not bot_direita.value():
                indice = (indice + 1) % len(opcoes)
                sleep(0.3)
                break
            if not bot_esquerda.value():
                indice = (indice - 1) % len(opcoes)
                sleep(0.3)
                break
            if not bot_ok.value():
                sleep(0.3)
                return opcoes[indice]

# ---------------------------
# Mostra letras vizinhas no LCD
# ---------------------------
def mostrar_letras_vizinhas():
    lcd.move_to(9, 3)
    for i in range(-3, 4):
        idx = (indice_letra + i) % len(alfabeto_game)
        if idx == indice_letra:
            lcd.putstr(" "); lcd.putchar(chr(1)); lcd.putstr(alfabeto_game[idx]); lcd.putchar(chr(0)); lcd.putstr(" ")
        else:
            lcd.putstr(alfabeto_game[idx])

# ---------------------------
# Exibe a palavra oculta com letras descobertas
# ---------------------------
def mostrar_frase_lcd(frase):
    linhas = [frase[i:i+14] for i in range(0, len(frase), 14)]
    for i in range(min(3, len(linhas))):
        lcd.move_to(5, i)
        for letra in linhas[i]:
            lcd.putstr(letra if letra in letras_descobertas or letra == ' ' else "_")

# ---------------------------
# Atualiza o display com a forca, boneco e letras
# ---------------------------
def atualizar_display():
    lcd.clear()
    lcd.move_to(0, 0); lcd.putstr("+-+")
    lcd.move_to(0, 1); lcd.putstr("|")
    lcd.move_to(0, 2); lcd.putstr("|")
    lcd.move_to(0, 3); lcd.putstr("|")
    mostrar_frase_lcd(palavra)
    mostrar_letras_vizinhas()

    if erros >= 1: lcd.move_to(2, 1); lcd.putchar(chr(2))  # Cabeça
    if erros >= 2: lcd.move_to(2, 2); lcd.putchar(chr(3))  # Corpo
    if erros >= 3: lcd.move_to(1, 2); lcd.putchar(chr(4))  # Braço esq
    if erros >= 4: lcd.move_to(3, 2); lcd.putchar(chr(5))  # Braço dir
    if erros >= 5: lcd.move_to(2, 3); lcd.putchar(chr(6))  # Perna esq
    if erros == 6: lcd.move_to(2, 3); lcd.putchar(chr(7))  # Perna dir

# ---------------------------
# Loop principal do jogo
# ---------------------------
init()
while True:
    atualizou = False

    if not bot_direita.value():
        indice_letra = (indice_letra + 1) % len(alfabeto_game)
        atualizou = True
        sleep(0.2)

    if not bot_esquerda.value():
        indice_letra = (indice_letra - 1) % len(alfabeto_game)
        atualizou = True
        sleep(0.2)

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

    if "_" not in letras_descobertas:
        atualizar_display()
        sleep(2)
        lcd.clear()
        lcd.move_to(4, 0); lcd.putstr("Voce venceu!")
        lcd.move_to(0, 1); lcd.putstr("O item era:")
        lcd.move_to(0, 2); lcd.putstr(f'"{palavra}"')
        sleep(3)
        init()

    if erros >= max_erros:
        atualizar_display()
        sleep(2)
        lcd.clear()
        lcd.move_to(4, 0); lcd.putstr("Game Over :(")
        lcd.move_to(0, 1); lcd.putstr("O item era:")
        lcd.move_to(0, 2); lcd.putstr(f'"{palavra}"')
        sleep(3)
        init()

    if atualizou:
        atualizar_display()


