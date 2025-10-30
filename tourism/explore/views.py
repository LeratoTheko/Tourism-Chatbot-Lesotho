from django.shortcuts import render

# Create your views here.
def base(request):
    return render(request, 'explore/landing/base.html', {})


def feature(request):
    return render(request, 'explore/landing/features.html', {})



def about(request):
    return render(request, 'explore/landing/about.html', {})




    