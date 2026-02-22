import csv
from models import Student

def load_students_from_csv(filename, classroom):
    """students from a CSV file"""
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                student = Student(row['Name'], row['Student_id'])
                classroom.add_student(student)
    except FileNotFoundError:
        print(f"File {filename} not found")
    except Exception as e:
        print(f"error  {e}")

def save_students_to_csv(filename, classroom):
    """Save students to a CSV file."""
    try:
        with open(filename, mode='w', newline='') as file:
            fieldnames = ['Name', 'Student_id', 'grades']
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            writer.writeheader()
            for student in classroom.students:
                writer.writerow({
                    'Name': student.get_name(),
                    'Student_id': student.get_student_id(),
                    'grades': str(student.get_grades())
                })
        print(f"Data saved")
    except Exception as e:
        print(f"error  {e}")

def validate_positive_integer_input(prompt):
    while True:
        try:
            value = input(prompt)
            int_value = int(value)
            if int_value >= 0:
                return int_value
            else:
                print("Please enter a positive number")
        except ValueError:
            print("wrong input")
