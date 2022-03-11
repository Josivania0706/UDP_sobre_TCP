import socket
import threading
import sys
import time

#5000 C:/Users/josiv/OneDrive/Área de Trabalho/ArquivosPy/TCP sobre UDP/
clients = []                            #Lista com todos os Clientes conectados
idsClients = []                         #Armazena os ids dos Clientes
estadoClients = []                      #Armazena os estados dos Clientes
msgsClientes = []                       #Armazena se os Clientes já enviaram mensagem- True ou False
addressClients = []                     #Armazena os dados address dos Clientes para poder enviar
clienteAdd = []
clientsEnviaram = []
contadorID = 0                          #Contador de quantos clientes já se conectaram
porta =  ""                                  #Porta do Servidor para estabelecer conexão
caminho = ''                               #Caminho no qual o Servidor armazenará os arquivos recebidos
syn = 'SYN'
seq = 4320
possuiSYN = ''

def inicio():
    
  global porta
  global caminho

  print('\nEntre com o número de porta e o diretório onde os arquivos serão salvos.\n')
  print('\nFormato: 5000 /save\n')
  porta_caminho = input("$ ./server ")
  quebrar_string = porta_caminho.split()  #Divide a string
  portaa = quebrar_string[0]
  caminhoo = quebrar_string[1]

  #Verificar se a porta de conexão é válida
  if int(portaa) >= 0 and int(portaa) <= 1023 or int(portaa) >= 49152 and int(portaa) <= 65535:
      print('\nA porta informada não pode ser utilizada.\n')
      sys.exit()  #Encerra a execução do programa
  
  #inicializar ip,host e caminho do arquivo
  porta = portaa
  caminho = caminhoo

def main():
  servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
  try:
      servidor.bind(('localhost', int(porta))) # aguarde a conexão
  except:
      return print('\nNão foi possível iniciar o servidor!\n')
  print ("aguardando conexão")

  while True:
      thread = threading.Thread(target=messagesTreatment, args=[servidor])
      thread.start()

def messagesTreatment(servidor):
  global contadorID         #Contador para ir criando os ids dos Clientes
  global seq
  ipEnviadoCliente = ''
  global msg_decodificada      #Armazena a mensagem enviada após sua decodificação
  global possuiSYN                  #Confirma se a mensagem enviada possui sinalizador SYN
  buscaID = ""              #Recebe a posição que o id se encontra na mensagem para poder extraí-lo
  auxID = ""                #Armazena o id extraido
  auxADDRESS = ""           #Armazena o address do cliente
  global clienteAdd
  #print('\nEsperando por clientes...\n')

  while True:
    try:
      time.sleep(10)
      msg, address = servidor.recvfrom(1024)
      print("\nEndereço: ",address[1])
      msg_decodificada = msg.decode()        #Mensagem enviada pelo Cliente decodificada
    
      print(msg_decodificada)

      #adicionar id para cada cliente que enviou msg
      if address[1] not in clienteAdd:
        clienteAdd.append(address[1])
        global contadorID
        contadorID = contadorID + 1          #Incrementado o contador para produzir um novo id
        print("ID= ",contadorID)
        msgsClientes.append(False)

      if "Vazio" in msg_decodificada:
        #Interromper conexão do cliente
        #Quando o cliente receber a mensagem acima, ele de ser cancelado -> sys.exit()
        servidor.sendto('ERROR: Nenhum arquivo enviado durante 10 segundos!'.encode(), address)
        index = str(contadorID)+'.txt'
        novoArq = open(str(index), 'w')
        novoArq.write("ERROR")
        novoArq.close()

      print('\nDeseja encerrar o Servidor? (S/N)\n')
      msgEncerramento = input('')
     
      if msgEncerramento == 'S' or msgEncerramento == 's':
        #Encerre o Servidor
        count = 0
        
        for i in msgsClientes:
          if i != True:
            count = i + 1
            aux = str(count)+".txt"
            novoArq = open(str(aux), "w")
            novoArq.write("")
            novoArq.close()
        sys.exit()  #Encerra a execução do programa

      elif msgEncerramento == 'N' or msgEncerramento == 'n':
        #Dê continuidade à execução
        #O cliente não enviou algo durante os 10 segundos
   
        #Recebe do cliente algum sinal - SIGQUIT/SIGTERM
        if 'SIGQUIT' in msg_decodificada or 'SIGTERM' in msg_decodificada:
          for i in msgsClientes:
            if i != True:
              count = i + 1
              aux = str(count)+".txt"
              novoArq = open(str(aux), "w")
              novoArq.write("")
              novoArq.close()
          print('\n0\n')
          sys.exit()  #Encerra a execução do programa

        #Como nenhuma das opções de encerrar o Servidor ou Cliente foi validada, o Cliente enviou algo
        else:
          addressClients.append(address)

          #Verifica se o pacote possui o sinalizador SYN
          
          if syn not in msg_decodificada:
            possuiSYN = 'False'
          else:
            possuiSYN = 'True'

          if possuiSYN == 'True':
            #Como o cliente acabou de enviar o SYN, o Servidor mantém ele como fechado pois a operação
            #só será realizada quando o Cliente não enviar o pacote com o SYN
            estadoClients.append('CLOSED')
            seq = seq + 1
            servidor.sendto(f'seq={seq}, ack=12345, id={contadorID}, SYN, ACK'.encode(), address)

          elif possuiSYN == 'False' and msg_decodificada[0]=='s':
            #Buscar id do Cliente
            buscaID = msg_decodificada.find('d')
            buscaID += 2
            auxID = msg_decodificada[buscaID] #Recebe o valor do id
            #Uma vez armazendo o id, posso subtrair 1, e terei acesso ao seu estado e address
            estadoClients.insert(int(auxID)-1,'LISTEN')
            auxADDRESS = addressClients[int(auxID) - 1]
            seq += 1
            servidor.sendto(f'seq={seq}, ack=12346, id={contadorID}, ACK'.encode(), address)

          #A mensagem enviada não é nenhum pacote, mas sim o arquivo
          else:
            print("Foi enviado um pacote e será criado um arquivo!!!")
            pegaArquivo = msg_decodificada.split(". ")  #Divide a string
            print(msg_decodificada)
            auxID = pegaArquivo[0]                  #Recebe o valor do id que será passado junto com o arquivo
            msgsClientes.insert(int(auxID)-1,True) #Saber que o Cliente enviou algo
            arquivo = pegaArquivo[2]                #Recebe o arquivo
            auxADDRESS = addressClients[int(auxID) - 1]  #Recebe o valor do address
            
            file_size = len(arquivo)              #Recebe o tamanho do arquivo         
           
            if estadoClients[int(auxID) - 1] == 'LISTEN':
              #O servidor só armazenará os arquivos de até 100 MB
              if file_size > 104857600:
                print('\nArquivo não suportado! Tamanho excede à 100 MB!\n')
                servidor.sendto('Arquivo não suportado! Tamanho excede à 100 MB!'.encode(), auxADDRESS)
              
              else:
                aux = str(auxID)+".txt"
                novoArq = open(str(aux), "w")
                novoArq.write(arquivo)
                novoArq.close()
                print("O arquivo foi criado!!!")
            else:
              print('\nO Cliente não possui estado LISTEN!\n')
    except:
      print('\nNão foi possível manter servidor ligado!\n')
      print('\n0\n')
      sys.exit()  #Encerra a execução do programa


if __name__== "__main__":
    inicio()
    main()
