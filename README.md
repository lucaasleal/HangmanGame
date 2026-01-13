# H_NGM_N GAME

## 💀 Jogo da Forca no Raspberry Pi Pico

Um jogo da forca (Hangman) completo, rodando direto no **Raspberry Pi Pico** usando **MicroPython**, com interface em um **LCD 20x4 via I2C** e botões físicos para navegação e interação! 😍

---

## 🎮 Funcionalidades

- Exibição em LCD 20x4 com I2C
- Três botões: Esquerda, Direita e OK
- Escolha de temas (dicionário externo)
- Lógica completa do jogo da forca
- Feedback visual com o boneco da forca animado (via caracteres personalizados)
- Mensagens de vitória e derrota

---

## 📦 Instalação

### 1️⃣ Requisitos

- [Thonny IDE](https://thonny.org/)
- Firmware **MicroPython** instalado no Raspberry Pi Pico
- Arquivos do projeto:
  - `main.py` (código principal)
  - `temas.py` (dicionário de palavras por tema)

### 2️⃣ Instalar o MicroPython no Pi Pico

1. Conecte o Pico ao PC segurando o botão **BOOTSEL**
2. Ele aparecerá como um **dispositivo USB**
3. No Thonny, vá em:
   - `Executar > Selecionar Interpretador`
   - Selecione **MicroPython (Raspberry Pi Pico)**
4. O Thonny vai oferecer para instalar o firmware. Aceite.

### 3️⃣ Enviar os arquivos

1. Abra o `main.py` no Thonny
2. Vá em `Arquivo > Salvar Como... > Raspberry Pi Pico`
3. Faça o mesmo com `temas.py`

> ⚠️ **Importante**: o Raspberry Pi Pico **não suporta subpastas** na memória. Todos os arquivos devem estar no **nível raiz da memória**.

---

## 📋 Esquema de Pinagem

| Função          | GPIO | Pino Físico | Descrição                       |
|-----------------|------|-------------|---------------------------------|
| SDA (I2C)       | GP4  | 6           | Comunicação com LCD             |
| SCL (I2C)       | GP5  | 7           | Comunicação com LCD             |
| Botão Direita   | GP12 | 16          | Avança letra                    |
| Botão OK        | GP11 | 15          | Seleciona letra                 |
| Botão Esquerda  | GP10 | 14          | Volta letra                     |
| VCC (LCD + Bot) | 3V3  | 36          | Alimentação 3.3V                |
| GND (Geral)     | GND  | 38 ou outro | Terra comum para LCD e botões   |

---

## 📂 Estrutura dos Arquivos

```bash
.
├── main.py        # Código principal do jogo
└── temas.py       # Dicionário com temas e palavras

```

## Esquemático
![image](https://github.com/user-attachments/assets/83254919-b0e7-4179-83c1-a05802e6078f)

