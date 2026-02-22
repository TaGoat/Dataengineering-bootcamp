def get_top_performing_student(classroom):
    top_student = classroom.students[0]
    for student in classroom.students:
        if student.calculate_average() > top_student.calculate_average():
            top_student = student
    
    return f"Top: {top_student.get_name()} with average {top_student.calculate_average()}"

def get_lowest_performing_student(classroom):
    lowest_student = classroom.students[0]
    for student in classroom.students:
        if student.calculate_average() < lowest_student.calculate_average():
            lowest_student = student
            
    return f"Lowest {lowest_student.get_name()} with average {lowest_student.calculate_average()}"

def get_students_ranking(classroom):
    ranked_students = sorted(
        classroom.students,
        key=lambda student: student.calculate_average(),
        reverse=True
    )
    return ranked_students

def get_grade_distribution(classroom):
    distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    for student in classroom.students:
        grade_category = student.catogrize_grade()
        if grade_category in distribution:
            distribution[grade_category] += 1
            
    return distribution
