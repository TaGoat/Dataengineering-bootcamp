class Student:
    def __init__(self, name, student_id):
        self._name = name
        self._student_id = student_id
        self._grades = []

    def get_name(self):
        return self._name

    def get_student_id(self):
        return self._student_id

    def get_grades(self):
        return self._grades

    def set_name(self, name):
        self._name = name

    def add_grade(self, grade):
        self._grades.append(grade)

    def calculate_average(self):
        total = sum(self._grades)
        average = total / len(self._grades)
        return round(average, 2)

    def catogrize_grade(self):
        average = self.calculate_average()
        if average >= 90:
            return "A"
        elif average >= 80:
            return "B"
        elif average >= 70:
            return "C"
        elif average >= 60:
            return "D"
        else:
            return "F"

    def __str__(self):
        return f"Student: {self._name} (ID: {self._student_id}) - Avg: {self.calculate_average()}"


class Classroom:
    def __init__(self):
        self.students = []

    def add_student(self, student):
        self.students.append(student)
        print(f"Add {student.get_name()} ")

    def remove_student(self, student_id):
        for student in self.students:
            if student.get_student_id() == student_id:
                self.students.remove(student)
                print(f" {student_id} removed.")
                break
            
    def search_student(self, student_id):
        for student in self.students:
            if student.get_student_id() == student_id:
                return student
        

    def calculate_classroom_average(self):
        total_sum = 0
        for student in self.students:
            total_sum += student.calculate_average()
            
        class_avg = total_sum / len(self.students)
        return round(class_avg, 2)

    @classmethod
    def get_class_info(cls):
        return "This is a Classroom"
