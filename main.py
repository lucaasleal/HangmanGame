from machine import Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
from time import sleep, ticks_ms, ticks_diff #Biblioteca para cálculo do tempo
from random import choice
from temas import *  # Importa o dicionário de temas e palavras

#configuração do LCD 20x4 via I2C
i2c = SoftI2C(sda=Pin(0), scl=Pin(1), freq=400000)
lcd = I2cLcd(i2c, 0x27, 4, 20)
ultimo_segundo_som = -1

#botoes
bot_direita = Pin(8, Pin.IN, Pin.PULL_UP)
bot_ok = Pin(7, Pin.IN, Pin.PULL_UP)
bot_esquerda = Pin(6, Pin.IN, Pin.PULL_UP)

# Estados anteriores dos botões
estado_ant_direita = 1
estado_ant_esquerda = 1
estado_ant_ok = 1

#Variaveis globais
letras_descobertas = []
alfabeto = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alfabeto_game = alfabeto.copy()
indice_letra = 0
letras_usadas = []
erros = 0
max_erros = 6
tempo_total = 90000
tempo_inicio = 0
estado_ant_direita= estado_ant_esquerda= estado_ant_ok = False

#Deboucing timers
ultimo_tempo_direita = 0
ultimo_tempo_esquerda = 0
ultimo_tempo_ok = 0
tempo_debounce = 150 

#Custom chars usados
seta_esquerda = bytearray([0b00010, 0b00110, 0b01110, 0b11110, 0b01110, 0b00110, 0b00010, 0b00000])
seta_direita = bytearray([0b01000, 0b01100, 0b01110, 0b01111, 0b01110, 0b01100, 0b01000, 0b00000])
lcd.custom_char(0, seta_esquerda)
lcd.custom_char(1, seta_direita)

head = bytearray([0b00100, 0b00000, 0b01110, 0b10001, 0b10001, 0b10001, 0b01110, 0b00100])
body = bytearray([0b01110, 0b10101, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100])
arm_left = bytearray([0b00000, 0b00000, 0b00000, 0b00001, 0b00010, 0b00000, 0b00000, 0b00000])
arm_right = bytearray([0b00000, 0b00000, 0b00000, 0b10000, 0b01000, 0b00000, 0b00000, 0b00000])
leg_left = bytearray([0b01000, 0b01000, 0b10000, 0b10000, 0b10000, 0b00000, 0b00000, 0b00000])
leg_right = bytearray([0b01010, 0b01010, 0b10001, 0b10001, 0b10001, 0b00000, 0b00000, 0b00000])
lcd.custom_char(2, head)
lcd.custom_char(3, body)
lcd.custom_char(4, arm_left)
lcd.custom_char(5, arm_right)
lcd.custom_char(6, leg_left)
lcd.custom_char(7, leg_right)

#inicializacao da rodada
def init():
    global letras_descobertas, letras_usadas, indice_letra, erros, alfabeto_game, palavra, tempo_inicio
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
    palavra = choice(temas[tema_escolhido]).upper() #Escolha do tema e da palavra

    for letra in palavra:
        letras_descobertas.append('_' if letra != ' ' else ' ') 
    
    atualizar_display()
    tempo_inicio = ticks_ms()

#Selecao de tema pelo usuario
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
                while not bot_direita.value(): pass  # espera soltar
                indice = (indice + 1) % len(opcoes)
                break
            if not bot_esquerda.value():
                while not bot_esquerda.value(): pass
                indice = (indice - 1) % len(opcoes)
                break
            if not bot_ok.value():
                while not bot_ok.value(): pass
                return opcoes[indice]

#Fazer a rotação de letras
def mostrar_letras_vizinhas():
    lcd.move_to(9, 3)
    for i in range(-3, 4):
        idx = (indice_letra + i) % len(alfabeto_game)
        if idx == indice_letra:
            lcd.putstr(" "); lcd.putchar(chr(1)); lcd.putstr(alfabeto_game[idx]); lcd.putchar(chr(0)); lcd.putstr(" ")
        else:
            lcd.putstr(alfabeto_game[idx])

#Mostra o item com letras descobertas
def mostrar_frase_lcd(frase):
    linhas = [frase[i:i+14] for i in range(0, len(frase), 14)]
    for i in range(min(3, len(linhas))):
        lcd.move_to(5, i)
        linha = ""
        for letra in linhas[i]:
            linha += letra if letra in letras_descobertas or letra == ' ' else "_"

        # Verifica se deve adicionar hífen no final da linha
        if i < len(linhas) - 1:
            fim_atual = linhas[i][-1]
            inicio_prox = linhas[i + 1][0]
            if fim_atual != ' ' and inicio_prox != ' ':
                linha = linha + "-"  # substitui o último caractere por hífen

        lcd.putstr(linha)  # completa até 14 caracteres com espaços

#Desenha letras, forca e boneco
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

init() #Primeira inicialização

while True:
    atualizou = False

    # Verifica botões com detecção de borda (mudança de estado)
    valor_direita = bot_direita.value()
    valor_esquerda = bot_esquerda.value()
    valor_ok = bot_ok.value()

    # Direita pressionada
    if estado_ant_direita and not valor_direita:
        if ticks_diff(ticks_ms(), ultimo_tempo_direita) > tempo_debounce:
            indice_letra = (indice_letra + 1) % len(alfabeto_game)
            atualizou = True
            ultimo_tempo_direita = ticks_ms()

    # Esquerda pressionada
    if estado_ant_esquerda and not valor_esquerda:
        if ticks_diff(ticks_ms(), ultimo_tempo_esquerda) > tempo_debounce:
            indice_letra = (indice_letra - 1) % len(alfabeto_game)
            atualizou = True
            ultimo_tempo_esquerda = ticks_ms()


    # OK pressionado
    if estado_ant_ok and not valor_ok:
        if ticks_diff(ticks_ms(), ultimo_tempo_ok) > tempo_debounce:
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
                lcd.move_to(5, 1)
                lcd.putstr("Ja usada!")
                sleep(1)
                atualizou = True

            ultimo_tempo_ok = ticks_ms()


    # Atualiza estados anteriores
    estado_ant_direita = valor_direita
    estado_ant_esquerda = valor_esquerda
    estado_ant_ok = valor_ok

    # Verifica fim de jogo
    if "_" not in letras_descobertas:
        atualizar_display()
        sleep(0.5)
        lcd.clear()
        lcd.move_to(4, 0); lcd.putstr("Voce venceu!")
        lcd.move_to(0, 1); lcd.putstr("O item era:")
        lcd.move_to(0, 2); lcd.putstr(f'"{palavra}"')
        sleep(3)
        init()
    
    tempo_atual = ticks_ms()
    if erros >= max_erros or (tempo_atual-tempo_inicio)>=tempo_total:
        atualizar_display()
        sleep(0.5)
        lcd.clear()
        lcd.move_to(4, 0); lcd.putstr("Game Over :(")
        lcd.move_to(0, 1); lcd.putstr("O item era:")
        lcd.move_to(0, 2); lcd.putstr(f'"{palavra}"')
        sleep(3)
        init()

    if atualizou:
        atualizar_display()
        
    lcd.move_to(4, 3); lcd.putstr(f"{max((tempo_total - (tempo_atual - tempo_inicio)) // 1000, 0):02}s") #Atualizacao do tempo
    seg_restantes = max((tempo_total - (tempo_atual - tempo_inicio)) // 1000, 0)

    if seg_restantes <= 10 and seg_restantes != ultimo_segundo_som:
        music.buzzer.play("c4", 0.2)
        ultimo_segundo_som = seg_restantes
