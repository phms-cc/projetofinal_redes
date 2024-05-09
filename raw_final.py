#JOAO VITOR ALVES FAHNING
#PEDRO HENRIQUE MARINHO SALVINO 
#RAINER TERROSO CARNEIRO

# Importações necessárias
import socket
import struct
import random

# Constantes para o endereço IP e a porta do servidor
IP_SERVIDOR = "15.228.191.109"

PORTA_SERVIDOR = 50000
PORTA_ORIGEM = 57981


# Função para criar uma requisição UDP, combinando o tipo de requisição e o identificador
def criar_requisicao(tipo_requisicao, identificador):
    req_res = 0  # 0000 para requisição
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
    if tamanho > 0 and len(resposta) >= (4 + tamanho):
        if tipo_resposta == 2:
            resposta_decimal = int.from_bytes(resposta[4:4 + tamanho], byteorder='big')
            texto_resposta = str(resposta_decimal)
        else:
            try:
                texto_resposta = resposta[4:4 + tamanho].decode("utf-8")
            except UnicodeDecodeError:
                texto_resposta = "Erro ao decodificar a resposta como UTF-8"
    else:
        texto_resposta = "Nenhum dado retornado"

    return tipo_resposta, identificador, texto_resposta



# Função para gerar um identificador aleatório para cada requisição
def gerar_identificador():
    return random.randint(1, 65535)



# Função para exibir o menu principal e retornar a escolha do usuário
def menu_principal():
    print("\n\nFaça sua requisição no servidor dos professores Ewerton e Fernando")
    print("\nProtocolo sendo utilizado: RAW e IP\n")
    print("Selecione uma opção:")
    print("1: Data e hora atual")
    print("2: Mensagem motivacional para o fim do semestre")
    print("3: Quantidade de respostas emitidas pelo servidor até o momento")
    print("4: Sair")
    return input("\nDigite um NÚMERO entre 1 e 4: ")


# Função para criar o cabeçalho UDP
def criar_cabecalho_udp(payload):
    # Comprimento do segmento UDP (cabeçalho + payload)
    comprimento_segmento = 8 + len(payload)
    # Checksum é calculado posteriormente
    checksum = 0
    # Empacota o cabeçalho UDP
    cabecalho_udp = struct.pack(">HHHH", PORTA_ORIGEM, PORTA_SERVIDOR, comprimento_segmento, checksum)
    return cabecalho_udp

# Função para obter o endereço IP do host local
def get_ip_address():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

# Função para calcular o checksum do segmento UDP
def calcular_checksum(segmento):
    # Pseudo cabeçalho IP
    pseudo_cabecalho_ip = struct.pack(">4s4sHH", socket.inet_aton(get_ip_address()), socket.inet_aton(IP_SERVIDOR), 0x11, len(segmento))
    # Concatena o pseudo cabeçalho IP com o segmento UDP
    dados_para_checksum = pseudo_cabecalho_ip + segmento
    # Adiciona um byte de preenchimento se o tamanho for ímpar
    if len(dados_para_checksum) % 2 != 0:
        dados_para_checksum += b'\x00'
    # Calcula o checksum
    checksum = 0
    for i in range(0, len(dados_para_checksum), 2):
        checksum += (dados_para_checksum[i] << 8) + dados_para_checksum[i + 1]
    # Realiza o wraparound
    checksum = (checksum >> 16) + (checksum & 0xFFFF)
    checksum += (checksum >> 16)
    # Complemento de um
    checksum = ~checksum & 0xFFFF
    return checksum


# Função para processar a escolha do usuário
def processar_escolha(escolha, identificador, socket_cliente):
    tipo_requisicao = int(escolha) - 1
    requisicao = criar_requisicao(tipo_requisicao, identificador)
    cabecalho_udp = criar_cabecalho_udp(requisicao)
    checksum = calcular_checksum(cabecalho_udp + requisicao)
    cabecalho_udp = struct.pack(">HHHH", PORTA_ORIGEM, PORTA_SERVIDOR, len(cabecalho_udp + requisicao), checksum)
    segmento_udp = cabecalho_udp + requisicao
    socket_cliente.sendto(segmento_udp, (IP_SERVIDOR, 0))
    resposta, _ = socket_cliente.recvfrom(256)
    # A resposta inclui o cabeçalho IP e o cabeçalho UDP, então precisamos pular os 20 bytes do cabeçalho IP e os 8 bytes do cabeçalho UDP
    tipo_resposta, identificador, texto_resposta = analisar_resposta(resposta[20 + 8:])
    print(f"Resposta recebida (Tipo {tipo_resposta}, ID {identificador}):\n{texto_resposta}\n")


# Função principal que controla o fluxo do programa
def main():
    socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
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