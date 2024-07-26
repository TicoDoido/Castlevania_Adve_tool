import zlib
import os
from tkinter import filedialog
import struct
import tkinter as tk

def descomprimir_arquivos():
    caminhos_arquivos = filedialog.askopenfilenames(title="Selecione os arquivos")

    if caminhos_arquivos:
        for caminho_arquivo in caminhos_arquivos:
            try:
                with open(caminho_arquivo, 'rb') as file:
                    # Saltar os primeiros 8 bytes do arquivo, se necessário
                    file.seek(8)
                    dados_compactados = file.read()

                dados_descompactados = zlib.decompress(dados_compactados)

                nome_arquivo, extensao_arquivo = os.path.splitext(caminho_arquivo)
                nome_pasta_extraida = os.path.join(os.path.dirname(caminho_arquivo), "extraida")

                os.makedirs(nome_pasta_extraida, exist_ok=True)

                nome_arquivo_descompactado = os.path.join(nome_pasta_extraida, f"{os.path.basename(nome_arquivo)}_descompressed{extensao_arquivo}")

                with open(nome_arquivo_descompactado, 'wb') as file:
                    file.write(dados_descompactados)

                print(f"Descompressão de {os.path.basename(caminho_arquivo)} concluída com sucesso!")
            except zlib.error as e:
                print(f"Erro ao descomprimir {os.path.basename(caminho_arquivo)}: {e}")
            except Exception as e:
                print(f"Erro ao processar {os.path.basename(caminho_arquivo)}: {e}")
    else:
        print("Nenhum arquivo selecionado.")

def recompactar_arquivos():
    caminhos_arquivos = filedialog.askopenfilenames(title="Selecione os arquivos descompactados")

    if caminhos_arquivos:
        for caminho_arquivo in caminhos_arquivos:
            try:
                with open(caminho_arquivo, 'rb') as file:
                    dados_descompactados = file.read()

                dados_compactados = zlib.compress(dados_descompactados)

                nome_arquivo, extensao_arquivo = os.path.splitext(caminho_arquivo)
                nome_arquivo_original = nome_arquivo.replace("_descompressed", "")
                nome_pasta_recompactada = os.path.join(os.path.dirname(caminho_arquivo), "recompactada")

                os.makedirs(nome_pasta_recompactada, exist_ok=True)

                nome_arquivo_compactado = os.path.join(nome_pasta_recompactada, f"{os.path.basename(nome_arquivo_original)}{extensao_arquivo}")

                # Adicionar 4 bytes '6D 64 66 00' e o tamanho do arquivo descompactado (4 bytes em big-endian)
                cabecalho = b'\x6D\x64\x66\x00'
                tamanho_descompactado = struct.pack('<I', len(dados_descompactados))  # Big-endian


                with open(nome_arquivo_compactado, 'wb') as file:
                    file.write(cabecalho)
                    file.write(tamanho_descompactado)
                    file.write(dados_compactados)

                print(f"Recompressão de {os.path.basename(caminho_arquivo)} concluída com sucesso!")
            except Exception as e:
                print(f"Erro ao processar {os.path.basename(caminho_arquivo)}: {e}")
    else:
        print("Nenhum arquivo selecionado.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Esconder a janela principal do Tkinter

    while True:
        print("Escolha uma opção:")
        print("1. Descomprimir arquivos")
        print("2. Recompactar arquivos")
        print("3. Sair")
        escolha = input("Digite o número da sua escolha: ")

        if escolha == "1":
            descomprimir_arquivos()
        elif escolha == "2":
            recompactar_arquivos()
        elif escolha == "3":
            break
        else:
            print("Opção inválida, tente novamente.")
