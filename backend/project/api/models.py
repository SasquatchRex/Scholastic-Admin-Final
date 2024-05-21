from django.db import models
import decimal

class Student(models.Model):
    name = models.CharField(max_length=100)
    dob_bs = models.CharField(max_length=11)
    dob_ad = models.CharField(max_length=11)
    reg_no = models.IntegerField(unique=True)
    symb_no = models.IntegerField(unique=True)
    # roll_number = models.CharField(max_length=20, unique=True)
    # Add other student information fields as needed

    def __str__(self):
        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    theory_credit_hours = models.DecimalField(max_digits=5,decimal_places=2)
    practical_credit_hours = models.DecimalField(max_digits=5,decimal_places=2)
    theory_marks = models.DecimalField(max_digits=5,decimal_places=2)
    practical_marks = models.DecimalField(max_digits=5,decimal_places=2)
    theory_subject_code = models.CharField(max_length=5)
    practical_subject_code = models.CharField(max_length=5)


    def __str__(self):
        return self.name

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    theory_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    practical_marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    final_marks_obtained = models.DecimalField(max_digits=5,decimal_places=2,blank=True,null=True)
    theory_grade = models.CharField(max_length=2, blank=True, null=True)
    practical_grade = models.CharField(max_length=2, blank=True, null=True)
    final_grade = models.CharField(max_length=2, blank=True, null=True)
    theory_gp = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    practical_gp = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)


    GRADE_TO_GPA_MAPPING = {
        'A+': 4.0,
        'A': 3.6,
        'B+': 3.2,
        'B': 2.8,
        'C+': 2.4,
        'C': 2.0,
        'D+': 1.6,
        'NG': 0.0
    }

    def calculate_grade(self, marks_obtained, full_marks):
        percentage = (marks_obtained / full_marks) * 100

        if percentage >= 90:
            return 'A+'
        elif 80 <= percentage < 90:
            return 'A'
        elif 70 <= percentage < 80:
            return 'B+'
        elif 60 <= percentage < 70:
            return 'B'
        elif 50 <= percentage < 60:
            return 'C+'
        elif 40 <= percentage < 50:
            return 'C'
        elif 35 <= percentage < 50:
            return 'D'
        else:
            return 'NG'

    def calculate_gpa(self):
        self.theory_gp = self.GRADE_TO_GPA_MAPPING.get(self.theory_grade, 0.0)
        self.practical_gp = self.GRADE_TO_GPA_MAPPING.get(self.practical_grade, 0.0)
        total_credit_hours = self.subject.theory_credit_hours + self.subject.practical_credit_hours
        return ((decimal.Decimal(self.theory_gp) * self.subject.theory_credit_hours ) + (decimal.Decimal(self.practical_gp) * self.subject.practical_credit_hours)) / total_credit_hours


    def save(self, *args, **kwargs):
        self.theory_grade = self.calculate_grade(self.theory_marks_obtained, self.subject.theory_marks)
        self.practical_grade = self.calculate_grade(self.practical_marks_obtained, self.subject.practical_marks)

        # Calculate final grade based on theory and practical grades
        if self.theory_grade and self.practical_grade:
            if self.theory_grade == 'NG' or self.practical_grade == 'NG':
                self.final_grade = 'NG'
            else:
                # Use whichever is higher between theory and practical grades as final grade
                self.final_marks_obtained = self.theory_marks_obtained+self.practical_marks_obtained
                self.final_grade = self.calculate_grade(self.final_marks_obtained,self.subject.theory_marks+self.subject.practical_marks)

        self.gpa = self.calculate_gpa()
        super().save(*args, **kwargs)


    # You might want to add more fields such as exam type (midterm, final), etc.

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}"
