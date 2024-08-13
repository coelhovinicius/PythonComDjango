from django.shortcuts import render, redirect
from .models import Empresas, Documento, Metricas
from django.contrib import messages
from django.contrib.messages import constants
from investidores.models import PropostaInvestimento
from django.http import HttpResponse

# ToDo: Realizar validação de campos - OK

def cadastrar_empresa(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    if request.method == "GET":
        #print(Empresas.tempo_existencia_choices)
        return render(request, 'cadastrar_empresa.html', 
                      {'tempo_existencia': Empresas.tempo_existencia_choices, 
                       'areas': Empresas.area_choices})
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        cnpj = request.POST.get('cnpj')
        site = request.POST.get('site')
        tempo_existencia = request.POST.get('tempo_existencia')
        descricao = request.POST.get('descricao')
        data_final = request.POST.get('data_final')
        percentual_equity = request.POST.get('percentual_equity')
        estagio = request.POST.get('estagio')
        area = request.POST.get('area')
        publico_alvo = request.POST.get('publico_alvo')
        valor = request.POST.get('valor')
        pitch = request.FILES.get('pitch')
        logo = request.FILES.get('logo')

        #print(request.user)

        try:
            empresa = Empresas(
                user=request.user,
                nome=nome,
                cnpj=cnpj,
                site=site,
                tempo_existencia=tempo_existencia,
                descricao=descricao,
                data_final_captacao=data_final,
                percentual_equity=percentual_equity,
                estagio=estagio,
                area=area,
                publico_alvo=publico_alvo,
                valor=valor,
                pitch=pitch,
                logo=logo
            )
            empresa.save()

        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor.')
            return redirect('/empresarios/cadastrar_empresa')

        messages.add_message(request, constants.SUCCESS,'Empresa criada com sucesso!')
        return redirect('/empresarios/cadastrar_empresa')
    
def listar_empresas(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == "GET":
        # Obtém todas as empresas do usuário
        empresas = Empresas.objects.filter(user=request.user)
        # Obtém o termo de busca do parâmetro GET
        busca_empresa = request.GET.get('empresa')

        # Filtra as empresas com base no termo de busca, se fornecido
        if busca_empresa:
            empresas = empresas.filter(nome__icontains=busca_empresa)

        if 'limpar' in request.GET:
            # Exibe todas as empresas sem aplicar nenhum filtro
            empresas = Empresas.objects.filter(user=request.user)

        return render(request, 'listar_empresas.html', {'empresas': empresas})

    
'''def listar_empresas(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    if request.method == "GET":
        #Fazer os filtros das empresas
        empresas = Empresas.objects.filter(user=request.user)
        return render(request, 'listar_empresas.html', {'empresas': empresas})'''

def empresa(request, id):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    empresa = Empresas.objects.get(id=id)
    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, 'Erro de autenticação. Favor tente novamente.')
        return redirect('/empresarios/listar_empresas/')
    
    if request.method == "GET":
        documentos = Documento.objects.filter(empresa=empresa)
        propostas_investimentos = PropostaInvestimento.objects.filter(empresa=empresa)
        percentual_vendido = 0
        #total_captado = 0
        for pi in propostas_investimentos:
            if pi.status == 'PA':
                percentual_vendido += pi.percentual
                #total_captado += pi.valor

        total_captado = sum(propostas_investimentos.filter(status='PA').values_list('valor', flat=True))

        valuation_atual = 100 * float(total_captado) / float(percentual_vendido) if percentual_vendido != 0 else 0
        proposta_enviada= propostas_investimentos.filter(status='PE')
        return render(request, 'empresa.html', {'empresa': empresa, 'documentos': documentos, 'proposta_enviada': proposta_enviada, 'percentual_vendido': int(percentual_vendido), 'total_captado': total_captado, 'valuation_atual': valuation_atual})
    
def add_doc(request, id):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get('titulo')
    arquivo = request.FILES.get('arquivo')
    extensao = arquivo.name.split('.')

    if empresa.user != request.user:
        messages.add_message(request, constants.ERROR, 'Erro ao anexar documento. Favor tente novamente.')
        return redirect('/empresarios/listar_empresas/')

    '''if not titulo:
        messages.add_message(request, constants.ERROR, 'Favor informar o título.')
        return redirect(f'/empresarios/empresa/{id}')'''

    if extensao[1] != 'pdf':
        messages.add_message(request, constants.ERROR, 'Favor anexar um arquivo em formato PDF.')
        return redirect(f'/empresarios/empresa/{id}')

    if not arquivo:
        messages.add_message(request, constants.ERROR, 'Arquivo não selecionado.')
        return redirect(f'/empresarios/empresa/{id}')

    documento = Documento(
        empresa=empresa,
        titulo=titulo,
        arquivo=arquivo
    )

    documento.save()
    messages.add_message(request, constants.SUCCESS, 'Arquivo cadastrado com sucesso.')
    return redirect(f'/empresarios/empresa/{empresa.id}')

def excluir_doc(request, id):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    documento = Documento.objects.get(id=id)
    if documento.empresa.user != request.user:
        messages.add_message(request, constants.ERROR, 'Erro de autenticação. Favor tentar novamente.')
        return redirect(f'empresarios/empresa/{empresa.id}')

    documento.delete()
    messages.add_message(request, constants.SUCCESS, 'Documento excluído com sucesso.')
    return redirect(f'/empresarios/empresa/{documento.empresa.id}')

def add_metrica(request, id):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    empresa = Empresas.objects.get(id=id)
    titulo = request.POST.get("titulo")
    valor = request.POST.get("valor")

    metrica = Metricas(
        empresa=empresa,
        titulo=titulo,
        valor=valor,
    )

    metrica.save()
    messages.add_message(request, constants.SUCCESS, "Métrica cadastrada com sucesso")
    return redirect(f'/empresarios/empresa/{empresa.id}')

def gerenciar_proposta(request, id):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')
    
    acao = request.GET.get('acao')
    pi = PropostaInvestimento.objects.get(id=id)

    if acao == 'aceitar':
        messages.add_message(request, constants.SUCCESS, 'Proposta aceita!')
        pi.status = 'PA'
    elif acao == 'recusar':
        messages.add_message(request, constants.WARNING, 'Infelizmente, sua proposta foi recusada.')
        pi.status = 'PR'

    pi.save()
    return redirect(f'/empresarios/empresa/{pi.empresa.id}')