import shutil
import os

#Versão atual 1.1 
# Busca e corrige divergencia de produtos entre arquivo de pedido e arquivo de retorno running 

'''Versão 1.1 Incluir print com diretório para disponibilização do retorno
'''
#Versão 1.2: Eliminar necessidade do usuário copiar o arquivo para o diretório correto realizando a cópia automaticamente ao final do processo


NUM_PED = '0125437403P' #Numero pedido running, disponivel em qualquer um dos arquivos da van ex.: RETORNO_20221125 *00115399503P* _29767463000165.TXT
DIR_PROJECT = 'C:\\Users\\felipe.santos\\Documents\\Projects\\ean_secundario\\files\\' # Caminho para salvar arquivos 

if os.path.isdir(f'{DIR_PROJECT}Saida'): pass 
else: os.mkdir(f'{DIR_PROJECT}Saida')

def find_retorno(num_ped,diret):
    dir = diret
    for root, dirs, files in os.walk(dir):
        str_match = list(filter(lambda x: num_ped in x, files))
        for item in str_match:
            copy_file(root,item)

def find_pedido(num_ped,diret):
    dir = diret
    for root, dirs, files in os.walk(dir):
        str_match = list(filter(lambda x: num_ped in x, files))
        for item in str_match:
            copy_file(root,item)

def copy_retorno_correto(path):
    #incluir nome do arquivo para copiar para o diretório correto eliminando interação do usuário
    dir = f'{DIR_PROJECT}\\Saida'
    filename_copy = ''
    for root, dirs, files in os.walk(dir):
        str_match = list(filter(lambda x: NUM_PED in x, files))
        for item in str_match:
            filename_copy = item

    try:
        source_copy = f'{DIR_PROJECT}Saida\\{filename_copy}'
        destination = f'{path}\\{filename_copy}'

        print(source_copy,destination)

        #shutil.copy(source_copy, destination) 

    except shutil.SameFileError:
        print('Diretório fonte e destino são iguais')

def identificar_pasta(dir):
    projetos = {'P':'Hypera','D':'Daut','M':'Medquimica','J':'Marjan','G':'Genom'}
    sigla = NUM_PED[-1:]
    projeto = projetos[sigla]

    if dir[3] == 'p':
        print(f'Diretório de disponibilização do retorno: G:\phlogrunning\{projeto}\Retorno')
        copy_retorno_correto(f'G:\phlogrunning\{projeto}\Retorno')
    else:
        print(f'Diretório de disponibilização do retorno: G:\logrunning\{projeto}\Retorno')
        copy_retorno_correto(f'G:\logrunning\{projeto}\Retorno')

def copy_file(diret,filename):
    try:
        source = f'{diret}\\{filename}'
        destination = f'{DIR_PROJECT}{filename}'

        shutil.copy(source, destination) 

        if filename[0] == 'R': identificar_pasta(diret)

    except shutil.SameFileError:
        print('Diretório fonte e destino são iguais')

def find_name_pedido(num_ped):
    dir = f'{DIR_PROJECT}'
    for root, dirs, files in os.walk(dir):
        str_match = list(filter(lambda x: num_ped in x, files))
        for item in str_match:
            if item[0] == 'P':
                return str(item)

def find_name_retorno(num_ped):
    dir = f'{DIR_PROJECT}'
    for root, dirs, files in os.walk(dir):
        str_match = list(filter(lambda x: num_ped in x, files))
        for item in str_match:
            if item[0] == 'R':
                return str(item)

find_retorno(NUM_PED,'G:\logrunning')
find_pedido(NUM_PED,'H:\RUNNING')

name_pedido = find_name_pedido(NUM_PED)
name_retorno = find_name_retorno(NUM_PED)

#Busca diretório phlogrunning
if name_pedido == None:
    dir_retorno = 'G:\phlogrunning'
    dir_pedido = 'H:\RUNNINGPHLOG'

    find_retorno(NUM_PED,dir_retorno)
    find_pedido(NUM_PED,dir_pedido)

    name_pedido = find_name_pedido(NUM_PED)
    name_retorno = find_name_retorno(NUM_PED)

pedido = open(f'{DIR_PROJECT}{name_pedido}','r')
pedidos = []

retorno = open(f'{DIR_PROJECT}{name_retorno}','r')
retornos = []

for line in retorno:
    linha = str(line)
    if linha[0] == '2':
        linha_exe = linha
        retornos.append(f'{line[1:14]}')

for line in pedido:
    linha = str(line)
    if linha[0] == '2':
        pedidos.append(f'{line[21:34]}')

divergencias = [item for item in pedidos if item not in retornos]


def verificar_pedido(ean):
    pedido = open(f'{DIR_PROJECT}{name_pedido}','r')
    for item in pedido:
        linha_pedido = str(item)
        if linha_pedido[21:34] == ean:
            return linha_pedido[34:39]
dic = {}   
if len(divergencias)== 0: 
    print('Sem divergencias')
else:
    for i in range(len(divergencias)):
        
        quantidade_solicitada = verificar_pedido(divergencias[i])
        dic[divergencias[i]] = quantidade_solicitada

def linhas_faltantes(divergencias):
    jurema = []
    for item in divergencias:
        qtd = dic[item]
        jurema.append(f'2{item}{linha_exe[14:34]}00000{linha_exe[39:47]}{qtd}13                                                0000000000000  0000000000000000000000000000000000000000000000000000')
    return jurema

def write_file(faltas):
    retorno = open(f'{DIR_PROJECT}{name_retorno}','r')
    cabecalho = ''
    itens = []
    rodape = ''
    for line in retorno:
        linha = str(line)
        if linha[0] == '2':
            itens.append(line)
        elif linha[0] == '3':
            rodape = line
        elif linha[0] == '1':
            cabecalho = line

    with open(f'{DIR_PROJECT}Saida\\{name_retorno}', 'w') as arquivo:
        #
        arquivo.write(f'{cabecalho}')
        #
        for line in itens:
            arquivo.write(line)
        #
        for iten in faltas:
            if iten != faltas[-1]:
                arquivo.write(f'{iten}\n')
            else: 
                arquivo.write(f'{iten}')
        

    arquivo.close()

    #rodape
    qtd_itens_atendidos = 0
    qtd_itens_nao_atendidos = 0
    numero_pedido = ''
    qtd_linhas = 0

    #conta linhas
    pedido = open(f'{DIR_PROJECT}Saida\\{name_retorno}','r')
    for line in pedido:
        qtd_linhas += 1

    #Verifica quantiade de itens atendidos e não atendidos
    pedido = open(f'{DIR_PROJECT}Saida\\{name_retorno}','r')
    for line in pedido:
        numero_pedido = line[14:34]
        linha = str(line)
        if linha[0] == '2' and linha[52:54] == '10':
            qtd_itens_atendidos += 1
        elif linha[0] == '2' and linha[52:54] != '10':
            qtd_itens_nao_atendidos +=1

    qtd_linhas += 1

    with open(f'{DIR_PROJECT}\\Saida\\{name_retorno}', 'a') as arquivo:
        arquivo.write(f'\n3{numero_pedido}{("0"*(5-len(str((qtd_linhas)))))}{str(qtd_linhas)}{("0"*(5-len(str(qtd_itens_atendidos))))}{qtd_itens_atendidos}{("0"*(5-len(str(qtd_itens_nao_atendidos))))}{qtd_itens_nao_atendidos}{"0"*14}')

    arquivo.close()

def clear_temp():
    dir = f'{DIR_PROJECT}Saida\\'
    for root, dirs, files in os.walk(dir):
        for file in files:
            os.remove(f'{root}{file}')

    dir = f'{DIR_PROJECT}'
    for root, dirs, files in os.walk(dir):
        for file in files:
            os.remove(f'{root}{file}')

faltas = linhas_faltantes(divergencias)
write_file(faltas)
#clear_temp()
