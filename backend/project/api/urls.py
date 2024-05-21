from django.urls import path
from . import views



urlpatterns = [
    path('create/mark',views.create_mark),
    path('create/subject',views.create_subject),
    path('test/data',views.printing_algorithm),
    path('export/pdf',views.convert_pngs_to_pdf),
    path('get/subjects',views.get_subjects),
    path('get/student',views.get_marks)

]
