import tkinter as tk
import random
import pygame
from PIL import Image, ImageTk

class SlotMachine:
    def __init__(self, master):
        self.master = master
        self.master.title("Caça-Níquel Virtual")

        # Configura a janela para tela cheia
        self.master.attributes('-fullscreen', True)

        # Inicializar Pygame
        pygame.mixer.init()
        self.spin_sound = pygame.mixer.Sound("spin_sound.wav")
        self.win_sound = pygame.mixer.Sound("win_sound.wav")
        self.insert_sound = pygame.mixer.Sound("insert_sound.wav")
        self.withdraw_sound = pygame.mixer.Sound("withdraw_sound.wav")
        self.exit_sound = pygame.mixer.Sound("exit_sound.wav")

        # Carregar e tocar a música de fundo
        pygame.mixer.music.load("background_music.mp3")
        pygame.mixer.music.play(-1)

        self.credits = 0
        self.bank_balance = 1000.00
        self.play_count = 0
        self.symbols = ['cereja', 'limão', 'laranja', 'melancia', 'estrela', 'trevo']
        self.payouts = {
            'cereja': 1.0,
            'limão': 2.0,
            'laranja': 3.0,
            'melancia': 4.0,
            'estrela': 5.0,
            'trevo': 10.0
        }
        self.total_winnings = 0
        self.is_spinning = False
        self.spin_result = []
        self.spin_count = 0
        self.level = 1  # Nível do jogador

        # Carregar e redimensionar imagens
        self.images = {}
        for symbol in self.symbols:
            img = Image.open(f"{symbol}.png")
            img = img.resize((100, 100))
            self.images[symbol] = ImageTk.PhotoImage(img)

        # Criar interface
        self.create_widgets()

    def create_widgets(self):
        self.title_label = tk.Label(self.master, text="Bem-vindo ao Caça-Níquel!", font=("Helvetica", 24))
        self.title_label.pack(pady=10)

        self.credits_label = tk.Label(self.master, text=f"Créditos: {self.credits:.2f}", font=("Helvetica", 20))
        self.credits_label.pack(pady=10)

        self.bank_balance_label = tk.Label(self.master, text=f"Banca: R$ {self.bank_balance:.2f}", font=("Helvetica", 20))
        self.bank_balance_label.pack(pady=10)

        self.level_label = tk.Label(self.master, text=f"Nível: {self.level}", font=("Helvetica", 20))
        self.level_label.pack(pady=10)

        self.credits_entry = tk.Entry(self.master, font=("Helvetica", 20))
        self.credits_entry.pack(pady=5)

        self.insert_button = tk.Button(self.master, text="Inserir Créditos", command=self.insert_credits, font=("Helvetica", 20), bg="lightblue")
        self.insert_button.pack(pady=5)

        self.result_frame = tk.Frame(self.master)
        self.result_frame.pack(pady=20)

        self.result_label = tk.Label(self.result_frame, text="", font=("Helvetica", 40))
        self.result_label.pack()

        self.result_text = tk.StringVar()
        self.result_message_label = tk.Label(self.master, textvariable=self.result_text, font=("Helvetica", 20))
        self.result_message_label.pack(pady=10)

        # Frame para os botões na horizontal
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack(pady=20)

        self.spin_button = tk.Button(self.button_frame, text="Girar!", command=self.start_spin, font=("Helvetica", 20), bg="lightgreen")
        self.spin_button.pack(side=tk.LEFT, padx=10)

        self.withdraw_button = tk.Button(self.button_frame, text="Sacar Ganhos", command=self.withdraw_winnings, font=("Helvetica", 20), bg="lightcoral", state=tk.DISABLED)
        self.withdraw_button.pack(side=tk.LEFT, padx=10)

        self.continue_button = tk.Button(self.button_frame, text="Continuar Jogando", command=self.continue_playing, font=("Helvetica", 20), state=tk.DISABLED)
        self.continue_button.pack(side=tk.LEFT, padx=10)

        self.exit_button = tk.Button(self.button_frame, text="Sair", command=self.exit_game, font=("Helvetica", 20), bg="lightcoral")
        self.exit_button.pack(side=tk.LEFT, padx=10)

        # Adiciona um botão para ver a tabela de pagamentos
        self.payout_button = tk.Button(self.master, text="Tabela de Pagamentos", command=self.show_payout_table, font=("Helvetica", 20), bg="lightyellow")
        self.payout_button.pack(pady=10)

    def insert_credits(self):
        try:
            amount = float(self.credits_entry.get())
            if amount > 0:
                self.credits += amount
                self.credits_label.config(text=f"Créditos: {self.credits:.2f}")
                self.credits_entry.delete(0, tk.END)
                self.result_text.set("Créditos inseridos com sucesso!")
                self.insert_sound.play()

                # Habilitar o botão "Girar!" se os créditos forem suficientes
                if self.credits >= 0.50:
                    self.spin_button.config(state=tk.NORMAL)
            else:
                self.result_text.set("Insira um valor positivo!")
        except ValueError:
            self.result_text.set("Insira um número válido!")

    def start_spin(self):
        if self.credits < 0.50:
            self.result_text.set("Você precisa de pelo menos R$ 0,50 para jogar!")
            return

        self.credits -= 0.50
        self.bank_balance += 0.50
        self.play_count += 1
        self.spin_count = 0

        self.is_spinning = True
        self.spin_button.config(state=tk.DISABLED)

        self.spin_sound.play()
        self.spin_symbols()

    def spin_symbols(self):
        if self.is_spinning and self.spin_count < 30:
            self.spin_result = [random.choice(self.symbols) for _ in range(3)]
            self.display_symbols()
            self.spin_count += 1
            self.master.after(100, self.spin_symbols)
        else:
            self.is_spinning = False
            self.spin_button.config(state=tk.NORMAL)
            self.check_result()

    def display_symbols(self):
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        for symbol in self.spin_result:
            img_label = tk.Label(self.result_frame, image=self.images[symbol])
            img_label.pack(side=tk.LEFT, padx=10)

    def check_result(self):
        final_spins = self.spin_result
        
        if self.check_win(final_spins):
            winnings = self.payouts[final_spins[0]]
            self.total_winnings += winnings
            self.bank_balance -= winnings
            self.result_text.set(f"Você ganhou R$ {winnings:.2f}! Você pode sacar ou continuar jogando.")
            self.withdraw_button.config(state=tk.NORMAL)
            self.continue_button.config(state=tk.NORMAL)
            self.win_sound.play()

            self.credits += winnings
            self.level_up()

        else:
            self.result_text.set("Tente novamente!")

        self.credits_label.config(text=f"Créditos: {self.credits:.2f}")
        self.bank_balance_label.config(text=f"Banca: R$ {self.bank_balance:.2f}")

        if self.credits <= 0:
            self.result_text.set("Seus créditos acabaram! Insira mais créditos.")
            self.spin_button.config(state=tk.DISABLED)

    def level_up(self):
        if self.total_winnings >= 10.0:
            self.level += 1
            self.total_winnings = 0
            self.level_label.config(text=f"Nível: {self.level}")
            self.result_text.set(f"Parabéns! Você subiu para o Nível {self.level}!")

    def withdraw_winnings(self):
        if self.total_winnings > 0:
            total_saque = self.total_winnings + self.credits
            message = f"Você sacou R$ {total_saque:.2f}."
            self.total_winnings = 0
            self.credits = 0
            self.credits_label.config(text=f"Créditos: {self.credits:.2f}")
            self.result_text.set(message)
            self.withdraw_sound.play()
            self.withdraw_button.config(state=tk.DISABLED)
            self.continue_button.config(state=tk.DISABLED)

    def continue_playing(self):
        self.withdraw_button.config(state=tk.DISABLED)
        self.continue_button.config(state=tk.DISABLED)

    def check_win(self, spins):
        return spins[0] == spins[1] == spins[2]

    def show_payout_table(self):
        payout_message = "Tabela de Pagamentos:\n"
        for symbol, payout in self.payouts.items():
            payout_message += f"{symbol.capitalize()}: R$ {payout:.2f}\n"
        self.result_text.set(payout_message)

    def exit_game(self):
        self.exit_sound.play()
        self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    slot_machine = SlotMachine(root)
    root.mainloop()
