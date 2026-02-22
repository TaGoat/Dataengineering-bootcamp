from models import Student, Classroom
from utils import load_students_from_csv, save_students_to_csv, validate_positive_integer_input
import analytics

def display_menu():
    print("\n" + "="*40)
    print("      Student Management System       ")
    print("="*40)
    print("1. Add a new student")
    print("2. Add a grade for a student")
    print("3. View all students")
    print("4. View student details (Search)")
    print("5. Classroom Average")
    print("6. Show top performing student")
    print("7. Show lowest performing student")
    print("8. Show student rankings")
    print("9. Show grade distribution")
    print("10. Remove a student")
    print("0. Save and Exit")
    print("="*40)

def main():
    classroom = Classroom()
    filename = 'data.csv'

    print("Welcome to Student System ")
    
    load_students_from_csv(filename, classroom)

    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == '1':
            name = input("Enter student name: ").strip()
            student_id = input("Enter student ID: ").strip()
            if not name or not student_id:
                print("Name and ID cannot be empty.")
            elif classroom.search_student(student_id):
                print("A student with this ID already exists!")
            else:
                new_student = Student(name, student_id)
                classroom.add_student(new_student)

        elif choice == '2':
            student_id = input("Enter student ID to add a grade: ").strip()
            student = classroom.search_student(student_id)
            if student:
                grade = validate_positive_integer_input("Enter the grade (0-100): ")
                if grade <= 100:
                    student.add_grade(grade)
                    print(f"Grade {grade} added to {student.get_name()}.")
                else:
                    print("Grade cannot be greater than 100.")
            else:
                print("Student not found.")

        elif choice == '3':
            if not classroom.students:
                print("No students in the classroom.")
            else:
                print("\nList of Students:")
                for student in classroom.students:
                    print(student) 

        elif choice == '4':
            student_id = input("Enter student ID to search: ").strip()
            student = classroom.search_student(student_id)
            if student:
                print("\nStudent Details:")
                print(f"Name: {student.get_name()}")
                print(f"ID: {student.get_student_id()}")
                print(f"Grades: {student.get_grades()}")
                print(f"Average: {student.calculate_average()}")
                print(f"Grade Category: {student.catogrize_grade()}")
            else:
                print("Student not found.")

        elif choice == '5':
            avg = classroom.calculate_classroom_average()
            print(f"The overall classroom average is: {avg}")

        elif choice == '6':
            result = analytics.get_top_performing_student(classroom)
            print(result)

        elif choice == '7':
            result = analytics.get_lowest_performing_student(classroom)
            print(result)

        elif choice == '8':
            ranked = analytics.get_students_ranking(classroom)
            if not ranked:
                print("No students to rank.")
            else:
                print("\nStudent Rankings:")
                for i, student in enumerate(ranked, 1):
                    print(f"{i}. {student.get_name()} ({student.calculate_average()})")

        elif choice == '9':
            dist = analytics.get_grade_distribution(classroom)
            print("\nGrade Distribution:")
            for grade, count in dist.items():
                print(f"Grade {grade}: {count} students")

        elif choice == '10':
            student_id = input("Enter student ID to remove: ").strip()
            classroom.remove_student(student_id)

        elif choice == '0':
            print("Saving data...")
            save_students_to_csv(filename, classroom)
            print("Exiting program")
            break

        else:
            print("Invalid choice. Please try again.")

main()
