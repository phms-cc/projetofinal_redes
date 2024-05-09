import socket
import struct
import random

# Constantes para o endereço IP e a porta do servidor
IP_SERVIDOR = "15.228.191.109"
PORTA_SERVIDOR = 50000

# Função para criar uma requisição UDP, combinando o tipo de requisição e o identificador
def criar_requisicao(tipo_requisicao, identificador):
    req_res = 0 # 0000 para requisição
    tipo_and_res = (req_res << 4) | tipo_requisicao
    # Empacota os dados no formato especificado (big-endian, 1 byte para tipo/requisição e 2 bytes para identificador)
    return struct.pack(">BH", tipo_and_res, identificador)

# Função para analisar a resposta recebida do servidor, descompactando os dados
def analisar_resposta(resposta):
    if len(resposta) < 4:
        raise ValueError("Resposta muito curta para ser descompactada.")

    # Descompacta o tipo de requisição/resposta e o identificador
    tipo_and_res, identificador = struct.unpack(">BH", resposta[:3])
    req_res = (tipo_and_res & 0xF0) >> 4
    tipo_resposta = tipo_and_res & 0x0F
    tamanho = resposta[3] if len(resposta) >= 4 else 0

    # Extrai a resposta baseada no tamanho e no tipo de resposta
    if (tamanho > 0) and (len(resposta)) >= (4 + tamanho):

        if (tipo_resposta == 2):

            resposta_decimal = int.from_bytes(resposta[4:4 + tamanho], byteorder='big')
            texto_resposta = str(resposta_decimal)

        else:
            texto_resposta = resposta[4:4 + tamanho].decode("utf-8")
    else:
        texto_resposta = "Nenhum dado retornado"

    return tipo_resposta, identificador, texto_resposta

# Função para gerar um identificador aleatório para cada requisição

def gerar_identificador():
    return random.randint(1, 65535)

# Função para exibir o menu principal e retornar a escolha do usuário

def menu_principal():

    print("\n\nFaça sua requisição no servidor dos professores Ewerton e Fernando")
    print("\nProtocolo sendo utilizado: UDP\n")
    print("Selecione uma opção:")
    print("1: Data e hora atual")
    print("2: Mensagem motivacional para o fim do semestre")
    print("3: Quantidade de respostas emitidas pelo servidor até o momento")
    print("4: Sair")

    return input("\nDigite um NÚMERO entre 1 e 4: ")

# Função para processar a escolha do usuário, enviar a requisição e imprimir a resposta

def processar_escolha(escolha, identificador, socket_cliente):
    tipo_requisicao = int(escolha) - 1
    requisicao = criar_requisicao(tipo_requisicao, identificador)
    socket_cliente.sendto(requisicao, (IP_SERVIDOR, PORTA_SERVIDOR))
    resposta, _ = socket_cliente.recvfrom(256)
    tipo_resposta, identificador, texto_resposta = analisar_resposta(resposta)
    print(f"Resposta recebida (Tipo {tipo_resposta}, ID {identificador}):\n{texto_resposta}\n")

# Função principal que gerencia o fluxo do programa

def main():
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        while True:
            escolha = menu_principal()
            if escolha == "4":
                print("Saindo...")
                break
            identificador = gerar_identificador()
            processar_escolha(escolha, identificador, socket_cliente)
    finally:
        socket_cliente.close()

if __name__ == "__main__":
    main()
