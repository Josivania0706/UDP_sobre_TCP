import socket
import string
import threading
import sys
from typing import Final
import os
import time

#localhost 5000 C:/Users/josiv/OneDrive/Área de Trabalho/ArquivosPy/TCP sobre UDP/file.txt
#Variáveis
dst_ip = ''
dst_port = ''
Caminho = '' 
syn = 'SYN'
ConnectionID = '0'  
seq = '12345' 
Ack = '0'

def inicio():
    
    #ler a porta e caminho do arquivo
    print('\nEntre com o número do host ,o número de porta e o diretório onde os arquivos serão salvos.\n')
    print('\nFormato: localhost 5000 ./arquivoCliente/file.txt\n')
    porta_caminho = input("$ ./client ")
    quebrar_string = porta_caminho.split(" ",2)  #Divide a string
    host = quebrar_string[0]
    porta = quebrar_string[1]
    caminho = quebrar_string[2]


    #Verificar se a porta de conexão é válida
    if int(porta) >= 0 and int(porta) <= 1023 or int(porta) >= 49152 and int(porta) <= 65535:
        print('\nA porta informada não pode ser utilizada.\n')
        sys.exit()  #Encerra a execução do programa

    #inicializar ip,host e caminho do arquivo
    global dst_ip
    global dst_port
    global Caminho
    dst_ip = host  
    dst_port = porta 
    Caminho = caminho


def main():

    address = (dst_ip, int(dst_port))

    try:
        cliente = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        print("\nsocket craido")

    except:
        return print('\nNão foi possível enviar Mensagem para o servidor!\n')

    #enviar pacote com sequencia,ack, id e syn
    cliente.sendto(f'seq={seq}, ack={Ack}, id={ConnectionID}, SYN'.encode(), address)
   
    thread = threading.Thread(target=messagesTreatment, args=[cliente])
    thread.start()

def messagesTreatment(cliente):
    global src_ip 
    global src_port
    global dst_ip
    global dst_port 
    global syn  
    global ConnectionID  
    global seq 
    global Ack
    
    while True:
        
        msg, address = cliente.recvfrom(1024) #Mensagem recebida do servidor
        msg_decodificada = msg.decode()  
        print(msg_decodificada)
        
        #Sempre que o cliente não receber pacotes do servidor por mais de 10 segundos, ele 
        #deve abortar a conexão (feche o socket e saia com o código diferente de zero).
        if "ERROR" in msg_decodificada:
            print('\n1\n')
            sys.exit()  #Encerra a execução do programa

        if msg_decodificada[0] == 's' and 'ACK' in msg_decodificada and 'SYN' in msg_decodificada:
        #Espere uma resposta do servidor com SYN | ACK. O cliente deve registrar o ID 
        #de conexão retornado e usá-lo em todos os pacotes subsequentes.
            resposta = msg_decodificada.split(', ')  #Divide a string 
            resp = resposta[0].split('=')
            seq = resp[1]#atualizar num de seq
            respAck = resposta[1].split('ack=')
            Ack = respAck[1]#atualizar num de Ack
            respIDConnect = resposta[2].split('id=')
            ConnectionID = respIDConnect[1]#atualizar num do ID

            cliente.sendto(f'seq={seq}, ack={Ack}, id={ConnectionID}, ACK'.encode(), address)
        
        if 'SYN' not in msg_decodificada:
            print("Será enviado o pacote")
            #Envia o pacote UDP com a flag ACK incluindo a primeira parte do arquivo 
            #especificado
            enviar_Dados_Lidos_Do_Arquivo(cliente,address)


def enviar_Dados_Lidos_Do_Arquivo(cliente,address):
    global flag
    global Ack
    pacote = ''

    ConteudoArquivo = open(str(Caminho), 'r')
    file_size = os.path.getsize(r'C:/Users/josiv/OneDrive/Área de Trabalho/ArquivosPy/TCP sobre UDP/file.txt') 
    if file_size < 104857600:
        for linha in ConteudoArquivo:
            pacote = pacote + linha
        cliente.sendto(f'{ConnectionID}. ack={Ack}. SIGQUIT'.encode() , address)
    else:
        print('\nTransferência excede à 100 MB!\n')

    ConteudoArquivo.close()#fechar o arquivo
    
    time.sleep(2)
    print('\n0\n')
    sys.exit()  #Encerra a execução do programa

   
if __name__== "__main__":
    inicio()
    main()
