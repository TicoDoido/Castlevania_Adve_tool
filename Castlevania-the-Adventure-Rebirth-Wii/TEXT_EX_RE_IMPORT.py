import os
import struct
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_and_replace_bytes(file_path):
    with open(file_path, 'rb') as f:
        # Ler o valor no offset 24
        f.seek(24)
        skip_size = struct.unpack('<I', f.read(4))[0]  # 4 bytes em little endian
        print(f"skip_size: {skip_size}")
        
        # Avançar o cursor
        f.seek(24 + 4 + skip_size)
        current_position = f.tell()
        print(f"Current position after skip_size: {current_position}")
        
        # Ler o tamanho do bloco de ponteiros
        pointer_block_size = struct.unpack('<I', f.read(4))[0]  # 4 bytes em little endian
        print(f"pointer_block_size: {pointer_block_size}")
        
        # Avançar o cursor além do bloco de ponteiros
        f.seek(pointer_block_size * 4, os.SEEK_CUR)
        current_position = f.tell()
        print(f"Current position after pointer_block_size: {current_position}")

        # Ler o resto dos dados até o final do arquivo
        data = f.read()
        
        # Substituir bytes 00 por 5B66696D5D0A
        replaced_data = data.replace(b'\x00', b'\x5B\x66\x69\x6D\x5D\x0A')
        
        # Definir o nome do arquivo de saída
        output_file_path = file_path + '.txt'
        
        # Salvar o conteúdo no arquivo de saída
        with open(output_file_path, 'wb') as output_file:
            output_file.write(replaced_data)
        
        print(f"Operação terminada com sucesso. Arquivo salvo como {output_file_path}")
        messagebox.showinfo("Sucesso", f"Operação terminada com sucesso. Arquivo salvo como {output_file_path}")

def reinsert_content(txt_file_path):
    original_file_path = txt_file_path[:-4]  # Remover '.txt' do final para obter o nome do arquivo original
    if not os.path.exists(original_file_path):
        messagebox.showerror("Erro", "Arquivo original não encontrado!")
        return
    
    with open(txt_file_path, 'rb') as txt_file:
        data = txt_file.read()
        
        # Definir substituições desejadas
        replacements = [
            (b'\x5B\x66\x69\x6D\x5D\x0A', b'\x00'),  # Substituição original \x5B\x66\x69\x6D\x5D\x0A = [fim]\n , esse \n equivale a uma quebra de linha 
            (b'\xC3\xAD', b'\x22'),     # Exemplo adicional de substituição
            (b'\xC3\xA3', b'\x23'),     # ISSO SÓ FOI USADO PARA TRADIZIR PARA PT BR, a fonte foi editada
            (b'\xC3\xA1', b'\x24'),
            (b'\xC3\xA9', b'\x25'),
            (b'\xC3\xB3', b'\x26'),
            (b'\xC3\xB4', b'\x2A'),
            (b'\xC3\xA7', b'\x3C'),
            # Adicione mais duplas conforme necessário para outras substituições
        ]
        
        # Aplicar as substituições
        restored_data = data
        for old_bytes, new_bytes in replacements:
            restored_data = restored_data.replace(old_bytes, new_bytes)
    
    # Calcular novos ponteiros para restored_data
    pointers = []
    current_position = 0
    
    while current_position < len(restored_data):
        next_zero_byte = restored_data.find(b'\x00', current_position)
        if next_zero_byte == -1:
            break
        pointers.append(current_position)
        current_position = next_zero_byte + 1  # Mover para o próximo byte após 00
    
    # Adicionar ponteiro para o final dos dados se houver dados após o último byte 00
    if current_position < len(restored_data):
        pointers.append(current_position)
    
    with open(original_file_path, 'r+b') as original_file:
        # Ler o valor no offset 24
        original_file.seek(24)
        skip_size = struct.unpack('<I', original_file.read(4))[0]
        
        # Avançar o cursor além do bloco de ponteiros
        original_file.seek(24 + 4 + skip_size)
        
        # Ler o tamanho do bloco de ponteiros
        pointer_block_size = struct.unpack('<I', original_file.read(4))[0]
        
        # Posicionar o cursor corretamente para escrever os dados restaurados
        original_file.seek(24 + 4 + skip_size + 4 + pointer_block_size * 4)
        original_file.write(restored_data)
        
        # Escrever os novos ponteiros
        original_file.seek(24 + 4 + skip_size + 4)
        for pointer in pointers:
            original_file.write(struct.pack('<I', pointer))
    
    print(f"Operação de reinserção terminada com sucesso no arquivo {original_file_path}")
    messagebox.showinfo("Sucesso", f"Operação de reinserção terminada com sucesso no arquivo {original_file_path}")

def select_txt_file():
    txt_file_path = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
    if txt_file_path:
        reinsert_content(txt_file_path)

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Todos os Arquivos", "*.*")])
    if file_path:
        extract_and_replace_bytes(file_path)

# Configurar a janela principal do Tkinter
root = tk.Tk()
root.title("Extrator e Reinsersor de Dados Binários")
root.geometry("400x100")
root.resizable(False, False)  # Impedir redimensionamento

# Adicionar um botão para selecionar o arquivo para extração
extract_button = tk.Button(root, text="Selecionar Arquivo para Extrair", command=select_file)
extract_button.pack(pady=10)

# Adicionar um botão para selecionar o arquivo .txt para reinserção
reinsert_button = tk.Button(root, text="Selecionar Arquivo .txt para Reinserir", command=select_txt_file)
reinsert_button.pack(pady=10)

# Iniciar o loop principal do Tkinter
root.mainloop()
