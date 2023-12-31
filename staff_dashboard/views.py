from django.shortcuts import render, redirect
from django.contrib import messages
from .update_menu import update_mess_menu
from .models import Menu, FoodRating, Food
from django.db.models import Avg, Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import os
from student_dashboard.models import Complaints
from student_dashboard.models import Attendance
from django.contrib.auth.models import User
from .export_bills import export_bills
from django.http import HttpResponse
from contextlib import contextmanager


@login_required(login_url="login")
def dashboard_view(request):
    if not request.user.is_staff:
        return redirect("studentdashboard")
    all_menus = Menu.objects.filter(
        date__year=(timezone.now()).year, date__month=(timezone.now()).month
    )
    overall_item_ratings = {}

    for menu in all_menus:
        food_ratings = FoodRating.objects.filter(menu=menu)
        if not food_ratings.exists():
            continue
        item_ratings = food_ratings.annotate(average_rating=Avg("rating")).order_by(
            "-average_rating"
        )
        menu.item_ratings = item_ratings
        menu.overall_avg_rating = round(
            food_ratings.aggregate(average_rating=Avg("rating"))["average_rating"], 2
        )
    dates = [timezone.now().date() - timedelta(days=i) for i in range(5)]
    meals = ["Breakfast", "Lunch", "Dinner"]
    attendance_counts = []
    for meal in meals:
        meal_data = {"meal": meal, "counts": [], "dates": []}
        for date in dates:
            count = (
                Attendance.objects.filter(meal=meal, date=date)
                .values("user")
                .annotate(count=Count("user"))
                .count()
            )
            meal_data["counts"].append(count)
        attendance_counts.append(meal_data)

    context = {
        "all_menus": all_menus,
        "overall_item_ratings": overall_item_ratings,
        "month": timezone.now().strftime("%B"),
        "last_five_days": dates,
        "attendance_counts": attendance_counts,
    }

    if request.method == "POST":
        if "update_menu" in request.FILES:
            if request.FILES["update_menu"].name.split(".")[-1] != "xlsx":
                messages.error(request, "Please upload a valid excel file")
            with open("mess-menu.xlsx", "wb+") as destination:
                for chunk in request.FILES["update_menu"].chunks():
                    destination.write(chunk)
            (data, err) = update_mess_menu()
            os.remove("mess-menu.xlsx")
            if err:
                messages.error(request, data)
                return redirect("staffdashboard")
            else:
                for date, meals in data.items():
                    # check if menu for date already exists
                    if Menu.objects.filter(date=date).exists():
                        menu = Menu.objects.get(date=date)
                        menu.save()
                        for food in meals["BREAKFAST"]:
                            if not Food.objects.filter(
                                menu=menu, meal="Breakfast", item=food
                            ):
                                food = Food(menu=menu, meal="Breakfast", item=food)
                                food.save()
                        for food in meals["LUNCH"]:
                            if not Food.objects.filter(
                                menu=menu, meal="Lunch", item=food
                            ):
                                food = Food(menu=menu, meal="Lunch", item=food)
                                food.save()
                        for food in meals["DINNER"]:
                            if not Food.objects.filter(
                                menu=menu, meal="Dinner", item=food
                            ):
                                food = Food(menu=menu, meal="Dinner", item=food)
                                food.save()
                    else:
                        menu = Menu(date=date)
                        menu.save()
                        for food in meals["BREAKFAST"]:
                            food = Food(menu=menu, meal="Breakfast", item=food)
                            food.save()
                        for food in meals["LUNCH"]:
                            food = Food(menu=menu, meal="Lunch", item=food)
                            food.save()
                        for food in meals["DINNER"]:
                            food = Food(menu=menu, meal="Dinner", item=food)
                            food.save()
                messages.success(request, "Menu updated successfully!")
                return redirect("staffdashboard")
        else:
            messages.error(request, "Please upload a file")
            return redirect("staffdashboard")

    return render(request, "staff_dashboard/dashboard.html", context)


@login_required(login_url="login")
def complaints_feedback_view(request):
    context = {}
    complaints = Complaints.objects.all().order_by("-complaint_date")
    context["complaints"] = complaints
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        complaint = Complaints.objects.get(complaint_id=complaint_id)
        complaint.complaint_status = "Resolved"
        complaint.save()
        messages.success(request, "Complaint resolved successfully!")
        return redirect("staffcomplaints")
    return render(request, "staff_dashboard/complaints.html", context)


@login_required(login_url="login")
def delete_complaint_view(request):
    if request.method == "POST":
        complaint_id = request.POST.get("complaint_id")
        complaint = Complaints.objects.get(complaint_id=complaint_id)
        complaint.delete()
        try:
            for file in os.listdir("static/media"):
                if file.startswith(complaint_id):
                    os.remove(os.path.join("static/media", file))
        except:
            pass
        messages.success(request, "Complaint deleted successfully!")
        return redirect("staffcomplaints")
    return redirect("staffcomplaints")


@login_required(login_url="login")
def calculate_fees(request):
    if request.method == "POST":
        student_name = request.POST.get("student_name")
        if student_name:
            try:
                student = User.objects.get(username=student_name)
            except User.DoesNotExist:
                messages.error(request, "Please enter a valid student name.")
                return redirect("calculate_fees")
            meal_costs = {"Breakfast": 80, "Lunch": 180, "Dinner": 150}

            # Get the student's attendance data
            user_attendance = Attendance.objects.filter(user=student)

            total_fees = 0
            meal_counts = {"Breakfast": 0, "Lunch": 0, "Dinner": 0}
            for attendance in user_attendance:
                meal_counts[attendance.meal] += 1
                total_fees += meal_costs.get(attendance.meal, 0)
            context = {
                "student": student,
                "meal_counts": meal_counts,
                "total_fees": total_fees,
                "user_attendance": True,
            }

            return render(request, "staff_dashboard/calc_fees.html", context)
        else:
            messages.error(request, "Please enter a valid student name.")

    return render(request, "staff_dashboard/calc_fees.html")


@contextmanager
def open_and_delete(filename):
    with open(filename, "rb") as file:
        yield file
    os.remove(filename)


@login_required(login_url="login")
def export_fees(request):
    file_path = export_bills()
    with open_and_delete(file_path) as fh:
        response = HttpResponse(
            fh.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "inline; filename=" + os.path.basename(
            file_path
        )

    return response
