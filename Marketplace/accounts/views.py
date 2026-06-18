from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse

def test_account(request):
    return JsonResponse({"message": "Accounts OK"})