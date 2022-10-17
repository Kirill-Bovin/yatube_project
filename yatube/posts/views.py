from django.shortcuts import render

# Create your views here.
def index(request):    
    template = 'posts/index.html'
    title = 'Главная страница'
    context = {
        'title': title,
    } 
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title': title,
    } 
        
    return render(request, template, context)