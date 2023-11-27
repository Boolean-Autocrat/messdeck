from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from allauth.socialaccount.models import SocialAccount
from .models import Staff, Student
from django.contrib.auth.decorators import login_required


class CustomLoginView(View):
    template_name = "auth/login.html"

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.is_staff:
                return redirect("staffdashboard")
            else:
                return redirect("studentdashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return redirect("staffdashboard")
        elif request.user.is_authenticated:
            return redirect("studentdashboard")
        return render(request, self.template_name)


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def profile_view(request):
    hostel_names = [
        "Ram",
        "Budh",
        "Krishna",
        "Gandhi",
        "Shankar",
        "Vyas",
        "Vishwakarma",
        "Bhagirath",
        "Rana Pratap",
        "Ashok",
        "Malviya",
    ]
    mess_names = ["RB", "CVR", "MR", "SR", "KG", "SV", "Malviya", "AK-RP-VK"]
    context = {}
    if request.user.is_staff:
        if not Staff.objects.filter(user=request.user).exists():
            staff = Staff(user=request.user)
            staff.save()
        staff_user = Staff.objects.get(user=request.user)
        staff_dict = {
            "user": staff_user.user,
            "psrn": staff_user.psrn,
            "mess": staff_user.mess,
            "messes": mess_names,
        }
        context = {
            "staff": staff_dict,
        }
    else:
        if not Student.objects.filter(user=request.user).exists():
            student = Student(user=request.user)
            student.save()
        student_user = Student.objects.get(user=request.user)
        student_dict = {
            "user": student_user.user,
            "bits_id": student_user.bits_id,
            "hostel": student_user.hostel,
            "hostels": hostel_names,
            "messes": mess_names,
            "mess": student_user.mess,
        }
        context = {
            "student": student_dict,
        }
    if request.method == "POST":
        if request.user.is_staff:
            staff_user.psrn = request.POST.get("psrn")
            if request.POST.get("mess") not in mess_names:
                messages.error(request, "Invalid mess name")
                return redirect("profile")
            staff_user.mess = request.POST.get("mess")
            staff_user.save()
        else:
            student_user.bits_id = request.POST.get("bits_id")
            print(request.POST.get("hostel"))
            print(request.POST.get("bits_id"))
            if request.POST.get("hostel") not in hostel_names:
                messages.error(request, "Invalid hostel name")
                return redirect("profile")
            student_user.hostel = request.POST.get("hostel")
            student_user.save()
            if student_user.hostel == "Malviya":
                student_user.mess = "Malviya"
            elif (
                student_user.hostel == "Ashok"
                or student_user.hostel == "Rana Pratap"
                or student_user.hostel == "Vishwakarma"
            ):
                student_user.mess = "AK-RP-VK"
            elif student_user.hostel == "Ram" or student_user.hostel == "Budh":
                student_user.mess = "RB"
            elif student_user.hostel == "Krishna" or student_user.hostel == "Gandhi":
                student_user.mess = "KG"
            elif student_user.hostel == "Shankar" or student_user.hostel == "Vyas":
                student_user.mess = "SV"
            elif student_user.hostel == "Bhagirath":
                student_user.mess = "MR"
            student_user.save()
        messages.success(request, "Profile updated successfully")
        return redirect("profile")
    return render(request, "auth/profile.html", context)
