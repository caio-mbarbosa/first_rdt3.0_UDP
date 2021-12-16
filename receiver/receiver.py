from socket import *
import os


# Abrindo um socket UDP e setando o ip, porta e númeero de bytes do buffer
server_ip = gethostbyname(gethostname())
server_port = 6789
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind((server_ip, server_port))
buffer_size = 1024


###### Etapa 1: Recebendo e salvando o arquivo ######

print("======= Envio do arquivo ========")

# Recebendo o nome do arquivo enviado pelo cliente
file_name, client_ip_port_tuple = server_socket.recvfrom(buffer_size)
file_size, client_ip_port_tuple = server_socket.recvfrom(buffer_size)


file_size = int(file_size.decode())
file_name = file_name.decode().strip()
print("Nome do arquivo: ", file_name)

# Criando um arquivo novo em modo de escrita binário
f = open(file_name, 'wb')

state = 0
received_bytes = 0
while received_bytes < file_size:
    
    if(state == 0): 
        porcentagem = (100*received_bytes)/file_size 
        print("{:.2f}".format(porcentagem) + "%" +" recebido", end="\r")
        
        # Estado que estamos esperando receber um pacote com 1o byte do header == 0
        transmitter_pkt, client_ip_port_tuple = server_socket.recvfrom(buffer_size)

        if(transmitter_pkt[:1] == b'0'):
            received_bytes += len(transmitter_pkt[1:])
            f.write(transmitter_pkt[1:])
            server_socket.sendto(b'0', client_ip_port_tuple)
            state = 1
            

    if(state == 1 and received_bytes < file_size):
        porcentagem = (100*received_bytes)/file_size  
        print("{:.2f}".format(porcentagem) + "%" +" recebido", end="\r")

        # Estado que estamos esperando receber um pacote com 1o byte do header == 1
        transmitter_pkt, client_ip_port_tuple = server_socket.recvfrom(buffer_size)

        if(transmitter_pkt[:1] == b'1'):
            received_bytes += len(transmitter_pkt[1:])
            f.write(transmitter_pkt[1:]) # cara, esse write aq ta certo msm?
            server_socket.sendto(b'1', client_ip_port_tuple)
            state = 0
        
print("'" + file_name + "'" + " foi recebido com sucesso")

f.close()
server_socket.close()
