from django.urls import path
from .views import index,login,fan,test,test_view,test_natija,student,student_info,contact,widgets,default_dashboard

urlpatterns = [
    path('dashboard/contact.html', contact, name='contact'),
    path('dashboard/widgets.html', widgets, name='widgets'),
    path('dashboard/dashboard.html', default_dashboard, name='default_dashboard'),
    path('', index, name='index'),
    path('login/',login, name='login'),
    path('student/<int:student_id>/', student_info, name='student_info'),
    path('fan/<int:sinf_id>/', fan, name='fan'),
    path('tests/<int:fan_id>/<int:sinf_id>/', test, name='tests'),
    path('quiz/<int:fan_id>/<int:sinf_id>/', test_view, name='quiz'),
    path('natija/<int:fan_id>/<int:sinf_id>/', test_natija, name='test_natija'),
    path('students/',student,name='student'),
]