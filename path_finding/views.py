# path_finding/views.py

from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Student
from .models import TestSession, TestAnswer

def path_finding_home(request):
    """
    Display all students and allow selecting one.
    Once selected, show if that student has a test session or not.
    """
    students = Student.objects.all()

    selected_student_id = request.GET.get('student_id')
    selected_student = None
    existing_session = None
    enrollment_date = None
    if selected_student_id:
        selected_student = get_object_or_404(Student, pk=selected_student_id)
        # Grab the most recent session if you allow multiple attempts
        existing_session = TestSession.objects.filter(student=selected_student).first()
        user = selected_student.student  
        enrollment_date = user.enrollment_date

    context = {
        'students': students,
        'selected_student': selected_student,
        'existing_session': existing_session,
        'student_id': selected_student_id,
        'enrollment_date': enrollment_date,


    }
    return render(request, 'path_finding/path_finding_home.html', context)


def create_test_session(request, student_id):
    """
    Creates a new TestSession for the given student.
    If you only allow one session, you might check first if one exists.
    """
    student = get_object_or_404(Student, pk=student_id)
    session = TestSession.objects.create(student=student)
    return redirect('fill_test', session_id=session.id)


def fill_test_view(request, session_id):
    """
    Page where the student answers the test.
    If POST, we save answers and mark the session as complete (if desired).
    """
    session = get_object_or_404(TestSession, pk=session_id)

    if request.method == 'POST':
        # Example of saving answers:
        # Q1, Q2, etc. from form input
        q1 = request.POST.get('q1')
        q2 = request.POST.get('q2')
        
        # If using a separate TestAnswer model:
        if q1:
            TestAnswer.objects.create(test_session=session, question_id=1, answer_text=q1)
        if q2:
            TestAnswer.objects.create(test_session=session, question_id=2, answer_text=q2)
        
        # Mark session as complete if you want:
        session.is_complete = True
        session.save()
        
        return redirect('path_finding_home')
    
    return render(request, 'path_finding/fill_test.html', {'session': session})


def generate_results_view(request, session_id):
    """
    Placeholder for where you'd feed the student's saved answers
    into an ML model to compute the recommended career path.
    """
    session = get_object_or_404(TestSession, pk=session_id)
    # In real code, you'd retrieve the session's answers and call your ML logic
    # answers = session.test_answers.all()
    # result = my_ml_function(answers)
    result = "Your career recommendation goes here (dummy for now)."

    return render(request, 'path_finding/results.html', {
        'session': session,
        'result': result
    })
