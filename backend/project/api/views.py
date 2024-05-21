from .serializers import StudentSerializer,SubjectSerializer,MarkSerializer

from .models import Student, Mark,Subject
from .serializers import StudentSerializer, MarkSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import MarkSerializer
import os.path
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import shutil
from django.conf import settings
from reportlab.pdfgen import canvas
from PIL import Image
import os
from reportlab.lib.pagesizes import A4
import json

from django.http import HttpResponse


@api_view(['POST'])
def create_subject(request):
    subjects_data = request.data if isinstance(request.data, list) else [request.data]

    responses = []
    for data in subjects_data:
        serializer = SubjectSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            responses.append(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(responses, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_subjects(request):
    subjects = Subject.objects.all()

    # Serialize the subject data
    serializer = SubjectSerializer(subjects, many=True)

    # Return the serialized data as JSON response
    return Response(serializer.data)


@api_view(['POST'])
def create_mark(request):
    student_data = request.data.pop('student', None)

    # Check if a student with the same name already exists
    existing_student = Student.objects.filter(name=student_data.get('name')).first()

    if existing_student:
        # If a student with the same name already exists, use that student
        student_instance = existing_student
    else:
        # If not, create a new student
        student_serializer = StudentSerializer(data=student_data)
        if student_serializer.is_valid():
            student_instance = student_serializer.save()
        else:
            return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Now, iterate through the list of subjects in the request data
    # and create or update marks for each subject
    marks_data = request.data.pop('subjects', [])

    for mark_data in marks_data:
        # Fetch subject ID based on the subject name provided in the request
        subject_name = mark_data.pop('subject')
        subject_instance = Subject.objects.filter(name=subject_name).first()
        if subject_instance:
            mark_data['subject'] = subject_instance.pk
        else:
            return Response({"detail": f"Subject with name '{subject_name}' does not exist."},
                            status=status.HTTP_400_BAD_REQUEST)

        mark_data['student'] = student_instance.pk

        # Check if the mark entry already exists for this student and subject
        existing_mark = Mark.objects.filter(student=student_instance, subject=subject_instance).first()
        if existing_mark:
            # Update the existing mark entry
            serializer = MarkSerializer(existing_mark, data=mark_data)
        else:
            # Create a new mark entry
            serializer = MarkSerializer(data=mark_data)

        if serializer.is_valid():
            serializer.save()
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response("Marks created or updated successfully", status=status.HTTP_201_CREATED)

# @api_view(['POST'])
# def create_mark(request):
#     student_data = request.data.pop('student', None)
#
#     # Check if a student with the same name already exists
#     existing_student = Student.objects.filter(name=student_data.get('name')).first()
#
#     if existing_student:
#         # If a student with the same name already exists, use that student
#         student_instance = existing_student
#     else:
#         # If not, create a new student
#         student_serializer = StudentSerializer(data=student_data)
#         if student_serializer.is_valid():
#             student_instance = student_serializer.save()
#         else:
#             return Response(student_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     # Now, iterate through the list of subjects in the request data
#     # and create marks for each subject
#     marks_data = request.data.pop('subjects', [])
#
#     for mark_data in marks_data:
#         # Fetch subject ID based on the subject name provided in the request
#         subject_name = mark_data.pop('subject')
#         subject_instance = Subject.objects.filter(name=subject_name).first()
#         if subject_instance:
#             mark_data['subject'] = subject_instance.pk
#         else:
#             return Response({"detail": f"Subject with name '{subject_name}' does not exist."},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         mark_data['student'] = student_instance.pk
#         serializer = MarkSerializer(data=mark_data)
#         if serializer.is_valid():
#             serializer.save()
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     return Response("Marks created successfully", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def printing_algorithm(request):
    body_unicode = request.body.decode('utf-8')

    # Parse the JSON data
    data = json.loads(body_unicode)

    # Access the data
    exam_year_ad = data.get('exam_year_ad')
    exam_year_bs = data.get('exam_year_bs')
    date_of_issue = data.get('date_of_issue')


    # print(request)
    print(exam_year_ad,exam_year_bs,date_of_issue)
    students = Student.objects.all().order_by('symb_no')
    name_position = (908, 676)
    dob_bs_position = (537, 742)
    dob_ad_position = (1447, 742)
    reg_no_position = (609, 790)
    sym_no_position = (1474, 790)
    exam_date_bs_position = (1564, 849)
    exam_date_ad_position = (271, 909)
    date_of_issue_position = (563, 2730)
    gpa_position = (1738, 2220)
    image_path = os.path.join(settings.BASE_DIR, "static", 'marksheet.png')
    image = Image.open(image_path)
    for student in students:
        name = student.name
        dob_bs = student.dob_bs
        dob_ad = student.dob_ad
        reg_no = student.reg_no
        symb_no = student.symb_no
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        font_size2 = 40
        font_size1 = 32
        font_path = "arial.ttf"  # Path to the font file
        font_size = 40
        text_color = (0, 0, 0)
        bool_ng = False
        # Load font (if specified)
        if font_path:
            font = ImageFont.truetype(font_path, font_size)
            font1 = ImageFont.truetype(font_path, font_size1)
        else:
            font = ImageFont.load_default()
            font1 = ImageFont.load_default()
        (subj_posx, subj_posy) = (213, 1276)
        marks = Mark.objects.filter(student=student)
        total_gp = 0
        # print({
        #     'name':name,
        #     "dob_bs" : dob_bs,
        #     "dob_ad" : dob_ad,
        #     "reg_no" : reg_no,
        #     "symb_no" : symb_no,
        #     "marks":marks
        # })
        for mark in marks:
            total_gp +=mark.gpa
            if mark.final_grade == "NG":
                bool_ng = True
            draw.text(name_position, name, fill=text_color, font=font)
            draw.text(dob_bs_position, str(dob_bs), fill=text_color, font=font)
            draw.text(dob_ad_position, str(dob_ad), fill=text_color, font=font)
            draw.text(reg_no_position, str(reg_no), fill=text_color, font=font)
            draw.text(sym_no_position, str(symb_no), fill=text_color, font=font)
            draw.text(exam_date_bs_position, str(exam_year_bs), fill=text_color, font=font)
            draw.text(exam_date_ad_position, str(exam_year_ad), fill=text_color, font=font)
            draw.text(date_of_issue_position, str(date_of_issue), fill=text_color, font=font)


            draw.text((subj_posx, subj_posy), str(mark.subject.theory_subject_code), fill=text_color, font=font1)
            draw.text((455, subj_posy), mark.subject.name + " (TH)", fill=text_color, font=font1)
            draw.text((1010, subj_posy), str(mark.subject.theory_credit_hours), fill=text_color, font=font1)
            draw.text((1240, subj_posy), str(mark.theory_gp), fill=text_color, font=font1)
            draw.text((1430, subj_posy), str(mark.theory_grade), fill=text_color, font=font1)
            posy = subj_posy + 20
            draw.text((1722, posy), str(mark.final_grade), fill=text_color, font=font1)

            subj_posy += 45
            draw.text((subj_posx, subj_posy), str(mark.subject.practical_subject_code), fill=text_color, font=font1)
            draw.text((455, subj_posy), mark.subject.name + " (IN)", fill=text_color, font=font1)
            draw.text((1010, subj_posy), str(mark.subject.practical_credit_hours), fill=text_color, font=font1)
            draw.text((1240, subj_posy), str(mark.practical_gp), fill=text_color, font=font1)
            draw.text((1430, subj_posy), str(mark.practical_grade), fill=text_color, font=font1)

            subj_posy += 45


        draw.text(gpa_position, str((total_gp/6).__round__(2)) if bool_ng==False else str("NG"),
                  fill=text_color, font=font)
        export_path = os.path.join(settings.BASE_DIR, "static", "export", f'{name}.png')
        image.save(export_path)
    return Response()

@api_view(['GET'])
def convert_pngs_to_pdf(request):
    # Create a PDF canvas
    png_folder = os.path.join(settings.BASE_DIR,"static","export")  # Path to the folder containing PNG files
    output_pdf_path =os.path.join(settings.BASE_DIR,"static","output.pdf")
    c = canvas.Canvas(output_pdf_path, pagesize=A4)

    # Get a list of all PNG files in the folder
    png_files = [file for file in os.listdir(png_folder) if file.endswith('.png')]

    # Sort the list of PNG files to ensure proper ordering
    png_files.sort()

    # Loop through each PNG file
    for png_file in png_files:
        # Open the PNG file
        img = Image.open(os.path.join(png_folder, png_file))

        width_ratio = A4[0] / img.width
        height_ratio = A4[1] / img.height
        scaling_factor = min(width_ratio, height_ratio)

        # Calculate the new dimensions of the image
        new_width = img.width * scaling_factor
        new_height = img.height * scaling_factor

        # Get the size of the PNG image
        # Draw the PNG image onto the PDF canvas
        c.drawImage(os.path.join(png_folder, png_file), 0, 0, new_width, new_height)

        # Add a new page for the next image
        c.showPage()

    # Save the PDF
    c.save()
    # Response = 0
    if os.path.exists(output_pdf_path):
        with open(output_pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="output.pdf"'
            return response
    else:
        return HttpResponse("PDF file not found", status=404)

@api_view(['POST'])
def get_marks(request):

    # Access the data
    reg_no = request.data.get('reg_no')

    try:
        student = Student.objects.get(reg_no=reg_no)
        marks = Mark.objects.filter(student=student)
        serializer1 = StudentSerializer(student)
        serializer2 = MarkSerializer(marks,many=True)
        return Response({"student" : serializer1.data,"marks": serializer2.data}, status=status.HTTP_200_OK)
    except Student.DoesNotExist:
        return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)



