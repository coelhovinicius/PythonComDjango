from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Produto

def cadastrar(request):
    if request.method == "GET":
        status = request.GET.get('status')
        return render(request, 'cadastrar.html', {'status': status})
    elif request.method == "POST":
        produto = request.POST.get('produto')
        preco = request.POST.get('preco')
        
        prod = Produto(
            produto=produto,
            preco=preco
        )

        prod.save()

        return redirect('/produtos/cadastrar?status=1')
    
def listar(request):
    produtos = Produto.objects.all()
    return render(request, 'listar.html', {'produtos': produtos})

def excluir(request, id):
    produto = Produto.objects.get(id=id)
    produto.delete()
    return redirect('/produtos/listar')