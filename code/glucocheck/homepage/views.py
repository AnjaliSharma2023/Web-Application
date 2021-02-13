from django.shortcuts import render

# Create your views here.
def homepage(request):
    ''' Snippet of the code for inputting the user name into the template
    if request.user.is_authenticated:
        context = {'username': request.user.name} # or however you reference the user name
    else:
        context = {'username': 'Sign-In/Up'}
    '''
    context = {'username': 'Sign-In/Up'}
    return render(request, 'homepage/homepage.html', context)