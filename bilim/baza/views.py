import re,random
from.models import Fan,Savol,Javob,Student,UserResponse,Sinf
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
def default_dashboard(request):
    # Umumiy statistikalar
    total_students_tuman = Student.objects.count()
    total_boys_tuman = Student.objects.filter(jins='o\'g\'il bola').count()
    total_girls_tuman = Student.objects.filter(jins='qiz bola').count()
    total_schools = Student.objects.values('school').distinct().count()

    # Maktablar bo‘yicha o‘g‘il-qizlar soni
    schools = Student.objects.values('school').distinct()
    school_stats = []
    for s in schools:
        school_name = s['school']
        boys = Student.objects.filter(school=school_name, jins='o\'g\'il bola').count()
        girls = Student.objects.filter(school=school_name, jins='qiz bola').count()
        school_stats.append({'school': school_name, 'boys': boys, 'girls': girls})
    latest_user = UserResponse.objects.last()

    context = {
        'total_students_tuman': total_students_tuman,
        'total_boys_tuman': total_boys_tuman,
        'total_girls_tuman': total_girls_tuman,
        'total_schools': total_schools,
        'school_stats': school_stats,
        'latest_user': latest_user,
    }

    return render(request, 'pluto/dashboard.html', context)
def widgets(request):
    maktablar = Student.objects.values_list('school', flat=True).distinct()
    fanlar = Fan.objects.all()

    fan_reytinglar = []
    umumiy_reytinglar = []

    for maktab in maktablar:
        fan_natijalar = []
        jami_togri = 0
        jami_javob = 0

        for fan in fanlar:
            responses = UserResponse.objects.filter(
                user__in=Student.objects.filter(school=maktab).values_list('FISh', flat=True),
                savol__fan=fan
            )
            jami = responses.count()
            togri = responses.filter(javob__togri=True).count()

            # 0 bo'lsa ham 0% chiqadi
            foiz = round((togri / jami) * 100, 2) if jami > 0 else 0
            fan_natijalar.append({'fan': fan.nomi, 'foiz': foiz})

            jami_togri += togri
            jami_javob += jami

        umumiy_foiz = round((jami_togri / jami_javob) * 100, 2) if jami_javob > 0 else 0

        fan_reytinglar.append({'maktab': maktab, 'fanlar': fan_natijalar})
        umumiy_reytinglar.append({'maktab': maktab, 'foiz': umumiy_foiz})
    context = {
            'fan_reytinglar': fan_reytinglar,
            'umumiy_reytinglar': umumiy_reytinglar
        }
    return render(request,'pluto/widgets.html', context)
def contact(request):
    query = request.GET.get('fish', '')  # URL'dan fish nomi olamiz
    if query:
        students = Student.objects.filter(FISh__icontains=query)
    else:
        students = Student.objects.all()
    return render(request,'pluto/contact.html',context={'students':students})


def fan(request, sinf_id):
    sinf = get_object_or_404(Sinf, id=sinf_id)
    kitob = Fan.objects.filter(sinf=sinf)
    context = {'kitob':kitob, 'sinf':sinf}
    return render(request, 'science.html', context)

def index(request):
    return render(request,'index.html')

# Passportni tozalash va seriya+raqam ajratish
def clean_passport(raw):
    if not raw:
        return None, None

    raw = raw.upper().strip()  # Katta harf va bo'shliqni olib tashlash

    # Password tekshirish uchun tozalash (faqat harf va raqam)
    cleaned = re.sub(r'[^A-Z0-9]', '', raw)

    # Harf+raqam kombinatsiyasini ajratamiz
    m = re.match(r'^([A-Z]+)(\d+)$', cleaned)
    if not m:
        return None, None

    # Seriyani original ko‘rinishda saqlaymiz (bazaga mos)
    seriya_match = re.match(r'^[A-Z-]+', raw)
    seriya = seriya_match.group() if seriya_match else None
    raqam = m.group(2)

    return seriya, raqam

def login(request):
    if request.method == "POST":
        passport = request.POST.get('passport', '').strip()
        password = request.POST.get('password', '').strip()

        seriya, raqam = clean_passport(passport)
        if not seriya or not raqam:
            return render(request, 'login.html', {'error': "Passport formati noto'g'ri!"})

        try:
            raqam = int(raqam)
        except ValueError:
            return render(request, 'login.html', {'error': "Passport raqami noto'g'ri!"})

        # Bazadan studentni qidiramiz
        try:
            student = Student.objects.get(seriya=seriya, raqami=raqam)
        except Student.DoesNotExist:
            return render(request, 'login.html', {'error': "Bunday o'quvchi topilmadi!"})

        # Password inputni tozalaymiz va katta harf bilan tekshiramiz
        password_input = re.sub(r'[^A-Za-z0-9]', '', password).upper()
        expected_password = f"{re.sub(r'[^A-Z0-9]', '', seriya)}{raqam}"

        if password_input != expected_password:
            return render(request, 'login.html', {'error': "Parol noto'g'ri!"})

        # Session-ga student id saqlaymiz
        request.session['student_id'] = student.id
        return redirect('student_info', student_id=student.id)

    return render(request, 'login.html')


from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Sinf

def student_info(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    # Session orqali kirish tekshiruvi
    if request.session.get('student_id') != student.id:
        return redirect('login')

    # Kerakli maydonlarni tekshiramiz
    required_fields = [
        student.FISh,
        student.seriya,
        student.raqami if student.raqami != 0 else None,
        student.sinf,
        student.school
    ]

    if not all(required_fields):
        return render(
            request,
            'student_info.html',
            {
                'student': student,
                'error_message': "Talabaning barcha ma'lumotlari to'liq emas!"
            }
        )

    if request.method == "POST":
        # ✅ SINFDAN RAQAM QISMINI AJRATAMIZ ("7-A" → "7")
        sinf_text = student.sinf.strip()  # Masalan: "7-B"
        sinf_raqam = ''.join([c for c in sinf_text if c.isdigit()])

        if not sinf_raqam:
            return render(request, 'student_info.html', {
                'student': student,
                'error_message': "Sinf nomida raqam topilmadi!"
            })

        # ✅ Shu raqamga mos sinfni topamiz
        sinf_obj = Sinf.objects.filter(nomi__startswith=sinf_raqam).first()

        if not sinf_obj:
            return render(request, 'student_info.html', {
                'student': student,
                'error_message': f"{sinf_raqam}-sinf uchun fanlar topilmadi!"
            })

        # ✅ FAN SAHIFASIGA O‘TAMIZ
        return redirect('fan', sinf_id=sinf_obj.id)

    return render(request, 'student_info.html', {'student': student})


def test(request, fan_id, sinf_id):
    fan = get_object_or_404(Fan, id=fan_id)
    sinf = get_object_or_404(Sinf, id=sinf_id)
    return render(request, 'test.html', {'fan': fan, 'sinf': sinf})


def test_view(request, fan_id, sinf_id):
    fan = get_object_or_404(Fan, id=fan_id)
    sinf = get_object_or_404(Sinf, id=sinf_id)
    # ✅ O'quvchi faqat o'z sinfiga kira oladi


    if 'savollar' not in request.session:
        savollar_queryset = Savol.objects.filter(fan=fan, sinf=sinf)
        savollar = random.sample(list(savollar_queryset), 2)
        request.session['savollar'] = [s.id for s in savollar]
        request.session['javoblar'] = {}
        request.session.modified = True
    else:
        savollar = list(Savol.objects.filter(id__in=request.session['savollar']))

    # ✅ SESSIONga tanlangan savollarni yozamiz
    request.session['savollar'] = [s.id for s in savollar]
    request.session.modified = True

    total_count = len(savollar)

    # Javoblar va variantlar uchun SESSION
    if 'javoblar' not in request.session:
        request.session['javoblar'] = {}
    if 'variantlar' not in request.session:
        request.session['variantlar'] = {}

    # Ko‘rsatilyotgan savol raqami
    if request.method == 'POST':
        current_index = int(request.POST.get('current_index', 1))
    else:
        current_index = 1

    time_left = 90  # Har savol uchun 90 soniya

    if current_index <= total_count and savollar:
        current_savol = savollar[current_index - 1]
        savol_id = str(current_savol.id)

        # Agar variantlar shuffle qilinmagan bo'lsa
        if savol_id not in request.session['variantlar']:
            variantlar = list(current_savol.javoblar.all())
            random.shuffle(variantlar)
            request.session['variantlar'][savol_id] = [v.id for v in variantlar]
            request.session.modified = True
        else:
            variant_ids = request.session['variantlar'][savol_id]
            variantlar = list(current_savol.javoblar.filter(id__in=variant_ids))
            variantlar.sort(key=lambda x: variant_ids.index(x.id))

        tanlangan_javob_id = request.session['javoblar'].get(savol_id)

    else:
        current_savol = None
        variantlar = []
        tanlangan_javob_id = None

    # POST (javob saqlash va navigatsiya)
    if request.method == 'POST':
        action = request.POST.get('action')
        auto_next = request.POST.get('auto_next') == '1'

        # Tanlangan javobni SESSIONga yozamiz
        for key, value in request.POST.items():
            if key.startswith('savol_'):
                savol_id = key.replace('savol_', '')
                request.session['javoblar'][savol_id] = value
                request.session.modified = True
                tanlangan_javob_id = value

        # Navigatsiya
        if action == 'previous' and current_index > 1:
            current_index -= 1
        elif (action == 'next' and current_index < total_count) or auto_next:
            current_index += 1
        elif action == 'finish' or current_index > total_count:
            return redirect('test_natija', fan_id=fan.id, sinf_id=sinf.id)

        if current_index <= total_count:
            current_savol = savollar[current_index - 1]
            savol_id = str(current_savol.id)

            if savol_id in request.session['variantlar']:
                variant_ids = request.session['variantlar'][savol_id]
                variantlar = list(current_savol.javoblar.filter(id__in=variant_ids))
                variantlar.sort(key=lambda x: variant_ids.index(x.id))
            else:
                variantlar = list(current_savol.javoblar.all())
                random.shuffle(variantlar)
                request.session['variantlar'][savol_id] = [v.id for v in variantlar]
                request.session.modified = True

            tanlangan_javob_id = request.session['javoblar'].get(savol_id)
        else:
            current_savol = None
            variantlar = []
            tanlangan_javob_id = None

    progress_percent = (current_index / total_count * 100) if total_count > 0 else 0

    context = {
        'current_savol': current_savol,
        'variantlar': variantlar,
        'current_index': current_index,
        'total_count': total_count,
        'has_previous': current_index > 1,
        'has_next': current_index < total_count,
        'tanlangan_javob_id': tanlangan_javob_id,
        'progress_percent': progress_percent,
        'time_left': time_left,
        'fan': fan,
        'sinf': sinf,
    }

    return render(request, 'quiz.html', context)
def test_natija(request, fan_id, sinf_id):
    javoblar = request.session.get('javoblar', {})      # {'savol_id': 'javob_id'}
    savollar_ids = request.session.get('savollar', [])  # [1, 3]

    umumiy_savollar = len(savollar_ids)
    togri_javoblar = 0


    for savol_id in savollar_ids:
        tanlangan_javob_id = javoblar.get(str(savol_id))
        if tanlangan_javob_id:
            try:
                javob = Javob.objects.get(id=tanlangan_javob_id)
                if javob.togri:  # ✅ Modelga mos ravishda
                    togri_javoblar += 1
            except Javob.DoesNotExist:
                continue

    foiz = (togri_javoblar / umumiy_savollar * 100) if umumiy_savollar > 0 else 0



    # SESSIONni tozalash
    if 'javoblar' in request.session:
        del request.session['javoblar']
    if 'savollar' in request.session:
        del request.session['savollar']

    context = {
        'togri_javoblar': togri_javoblar,
        'umumiy_savollar': umumiy_savollar,
        'foiz': foiz,
    }

    return render(request, 'natija.html', context)
def student(request):
    sinf_filter = request.GET.get('sinf', '')
    sinflar = Student.objects.values_list('sinf', flat=True).distinct()

    if sinf_filter:
        students = Student.objects.filter(sinf=sinf_filter)
    else:
        students = Student.objects.all()

    total_students = students.count()

    # O'g'il bolalarni tanlash
    boys = students.filter(jins='male')  # yoki 'gender' bo‘lishi mumkin
    boys_count = boys.count()

    # Qizlarni tanlash
    girls = students.filter(jins='female')
    girls_count = girls.count()

    context={
        'students': students,
        'sinflar': sinflar,
        'total_students': total_students,
        'tanlangan_sinf': sinf_filter,
        'boys': boys,
        'girls': girls,
        'boys_count': boys_count,
        'girls_count': girls_count,
    }
    return render(request, 'students.html', context)


