from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from staff_dashboard.models import Menu, FoodRating
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Complaints, Attendance
from PIL import Image
import os


@login_required(login_url="login")
def dashboard_view(request):
    if request.user.is_staff:
        return redirect("staffdashboard")
    menus = Menu.objects.filter(
        date__year=(timezone.now()).year, date__month=(timezone.now()).month
    )
    current_time = timezone.now() + timezone.timedelta(hours=5, minutes=30)
    breakfast_start = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
    breakfast_end = current_time.replace(hour=9, minute=0, second=0, microsecond=0)
    lunch_start = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    lunch_end = current_time.replace(hour=14, minute=0, second=0, microsecond=0)
    dinner_start = current_time.replace(hour=19, minute=0, second=0, microsecond=0)
    dinner_end = current_time.replace(hour=21, minute=0, second=0, microsecond=0)

    can_mark_attendance = False
    already_marked = False

    if breakfast_start <= current_time <= breakfast_end:
        meal_type = "Breakfast"
    elif lunch_start <= current_time <= lunch_end:
        meal_type = "Lunch"
    elif dinner_start <= current_time <= dinner_end:
        meal_type = "Dinner"
    else:
        meal_type = None

    if meal_type:
        if not Attendance.objects.filter(
            user=request.user, meal=meal_type, date=timezone.now().date()
        ).exists():
            can_mark_attendance = True
        else:
            already_marked = True

    next_meal = None
    tomorrow = False
    if dinner_end <= current_time < breakfast_end + timezone.timedelta(
        days=1
    ) and current_time < timezone.now().replace(
        hour=23, minute=59, second=59, microsecond=59
    ):
        next_meal = "Breakfast"
        tomorrow = True
    elif dinner_end <= current_time < breakfast_end + timezone.timedelta(
        days=1
    ) and current_time >= timezone.now().replace(
        hour=23, minute=59, second=59, microsecond=59
    ):
        next_meal = "Breakfast"
    elif breakfast_end <= current_time < lunch_end:
        next_meal = "Lunch"
    elif lunch_end <= current_time < dinner_end:
        next_meal = "Dinner"

    if Menu.objects.filter(date=timezone.now().date()).exists():
        today_meal = Menu.objects.get(date=timezone.now().date())
    if Menu.objects.filter(
        date=timezone.now().date() + timezone.timedelta(days=1)
    ).exists():
        tomorrow_meal = Menu.objects.get(
            date=timezone.now().date() + timezone.timedelta(days=1)
        ).breakfast

    next_meal_content = None
    if tomorrow:
        next_meal_content = tomorrow_meal
    else:
        if next_meal_content is not None:
            next_meal_content = (
                today_meal.breakfast
                if next_meal == "Breakfast"
                else today_meal.lunch
                if next_meal == "Lunch"
                else today_meal.dinner
            )

    context = {
        "month": timezone.now().strftime("%B"),
        "menus": menus,
        "can_mark_attendance": can_mark_attendance,
        "already_marked": already_marked,
        "next_meal": next_meal,
        "next_meal_content": next_meal_content,
    }
    if request.method == "POST":
        menu_date = request.POST.get("menu_date")
        menu = Menu.objects.get(date=menu_date)
        for key, value in request.POST.items():
            if key.endswith("_rating"):
                item = key[:-7]
                rating = value
                if rating not in ["1", "2", "3", "4", "5"]:
                    messages.error(
                        request,
                        "Invalid rating for item: "
                        + item
                        + ". Please rate between 1 and 5.",
                    )
                    return redirect("studentdashboard")
                food_rating, created = FoodRating.objects.get_or_create(
                    menu=menu, item=item
                )
                food_rating.add_rating(rating)
                food_rating.save()
        messages.success(request, "Your ratings have been submitted.")
        return redirect("studentdashboard")
    return render(request, "student_dashboard/dashboard.html", context)


@login_required(login_url="login")
def feedback_view(request):
    if request.method == "POST":
        feedback = request.POST.get("complaint_description")
        if "complaint_file" in request.FILES:
            if len(request.FILES.getlist("complaint_file")) > 5:
                messages.error(request, "Please upload a maximum of 5 files!")
                return redirect("studentdashboard")
            for file in request.FILES.getlist("complaint_file"):
                if file.name.split(".")[-1] not in ["png", "jpg", "jpeg", "gif"]:
                    messages.error(
                        "Please upload only image files (png, jpg, jpeg, gif)!"
                    )
                    return redirect("studentdashboard")
        if feedback:
            complaint = Complaints(
                student=User.objects.get(username=request.user.username),
                complaint_description=feedback,
            )
            complaint.save()
            messages.success(request, "Thank you for your feedback!")
            complaint_id = complaint.complaint_id
            count = 1
            try:
                for file in request.FILES.getlist("complaint_file"):
                    with open(
                        f"media/complaints/{complaint_id}_{count}.{file.name.split('.')[-1]}",
                        "wb+",
                    ) as destination:
                        for chunk in file.chunks():
                            destination.write(chunk)
                    if file.name.split(".")[-1] != "png":
                        im = Image.open(
                            f"media/complaints/{complaint_id}_{count}.{file.name.split('.')[-1]}"
                        )
                        im.save(f"media/complaints/{complaint_id}_{count}.png", "png")
                        os.remove(
                            f"media/complaints/{complaint_id}_{count}.{file.name.split('.')[-1]}"
                        )
                    im = Image.open(f"media/complaints/{complaint_id}_{count}.png")
                    width, height = im.size
                    if height > 1200 or width > 1200:
                        if width > height and str(width)[0] == "1":
                            new_width = width / 2
                            new_height = height / 2
                        elif width < height and str(height)[0] == "1":
                            new_width = width / 2
                            new_height = height / 2
                        elif width > height:
                            new_width = int(width / (int(str(width)[0])))
                            new_height = int(height / (int(str(width)[0])))
                        else:
                            new_width = int(width / (int(str(height)[0])))
                            new_height = int(height / (int(str(height)[0])))
                        im = im.resize((int(new_width), int(new_height)))

                    im.save(
                        f"media/complaints/{complaint_id}_{count}.png",
                        "png",
                        optimize=True,
                        quality=50,
                    )
                    count += 1
                complaint.no_of_files = count - 1
            except:
                messages.error(request, "Error uploading files!")
            complaint.save()
        else:
            messages.error(request, "Please enter some feedback.")
        return redirect("studentdashboard")
    return redirect("studentdashboard")


@login_required(login_url="login")
def mark_attendance(request):
    current_time = timezone.now()
    breakfast_start = current_time.replace(hour=7, minute=0, second=0, microsecond=0)
    lunch_start = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    dinner_start = current_time.replace(hour=19, minute=0, second=0, microsecond=0)
    meal = None
    if (
        (
            current_time >= breakfast_start
            and current_time < breakfast_start + timezone.timedelta(hours=2)
        )
        or (
            current_time >= lunch_start
            and current_time < lunch_start + timezone.timedelta(hours=2)
        )
        or (
            current_time >= dinner_start
            and current_time < dinner_start + timezone.timedelta(hours=2)
        )
    ):
        meal = (
            "Breakfast"
            if current_time < lunch_start
            else ("Lunch" if current_time < dinner_start else "Dinner")
        )
        if not Attendance.objects.filter(
            user=request.user, meal=meal, date=timezone.now().date()
        ).exists():
            Attendance.objects.create(
                user=request.user, meal=meal, date=timezone.now().date()
            )
            messages.success(request, f"Attendance marked for {meal}.")
        else:
            messages.warning(request, f"Attendance already marked for {meal}.")
    else:
        messages.error(request, "Attendance can only be marked during mess hours.")

    return redirect("studentdashboard")
