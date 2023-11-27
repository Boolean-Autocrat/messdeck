import pandas as pd
from student_dashboard.models import User, Attendance
import datetime

time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")


def export_bills():
    students = User.objects.all()
    data = []

    for student in students:
        if student.is_staff:
            continue
        user_attendance = Attendance.objects.filter(user=student)
        meal_costs = {"Breakfast": 80, "Lunch": 180, "Dinner": 150}
        total_fees = sum(
            meal_costs.get(attendance.meal, 0) for attendance in user_attendance
        )
        data.append(
            {
                "Student Name": student.get_full_name(),
                "Total Fees": total_fees,
            }
        )
    df = pd.DataFrame(data)
    df.to_excel(f"bills_export-{time}.xlsx", index=False)
    return f"bills_export-{time}.xlsx"
