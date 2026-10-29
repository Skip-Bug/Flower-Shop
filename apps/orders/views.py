from django.shortcuts import render


def quiz(request):
    return render(request, "quiz.html")


def quiz_step(request):
    return render(request, "quiz-step.html")


def result(request):
    return render(request, "result.html")


def order(request):
    return render(request, "order.html")


def order_step(request):
    return render(request, "order-step.html")

