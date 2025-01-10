# path_finding/views.py

from django.shortcuts import render, get_object_or_404, redirect
from accounts.models import Student
from .models import TestSession, TestAnswer, Program
from .questions import QUESTIONS
from .llm_analyzer import analyze_answer
from course.models import Program

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
    """
    session = get_object_or_404(TestSession, pk=session_id)

    if request.method == 'POST':
        # Map question numbers to model fields
        field_mapping = {
            1: 'q1_numbers',
            2: 'q2_math',
            3: 'q3_problem_solving',
            4: 'q4_future_job',
            5: 'q5_tools',
            6: 'q6_tech_interest',
            7: 'q7_learning',
            8: 'q8_computer_skills',
            9: 'q9_projects',
            10: 'q10_goals'
        }
        
        # Store answers in the session model
        for question in QUESTIONS:
            answer_text = request.POST.get(f'q{question["order"]}')
            if answer_text:
                field_name = field_mapping[question['order']]
                setattr(session, field_name, answer_text)
        
        session.is_complete = True
        session.save()
        return redirect('generate_results', session_id=session.id)
    
    return render(request, 'path_finding/fill_test.html', {
        'session': session,
        'questions': QUESTIONS
    })


def generate_results_view(request, session_id):
    """
    Analyzes the student's test answers using LLM and recommends programs
    """
    session = get_object_or_404(TestSession, pk=session_id)
    programs = Program.objects.all()
    
    # Map field names to question numbers
    field_mapping = {
        1: 'q1_numbers',
        2: 'q2_math',
        3: 'q3_problem_solving',
        4: 'q4_future_job',
        5: 'q5_tools',
        6: 'q6_tech_interest',
        7: 'q7_learning',
        8: 'q8_computer_skills',
        9: 'q9_projects',
        10: 'q10_goals'
    }
    
    # Format all answers for LLM analysis
    qa_pairs = []
    for i in range(1, 11):
        question = next((q for q in QUESTIONS if q['order'] == i), None)
        if question:
            field_name = field_mapping[i]
            answer = getattr(session, field_name)
            qa_pairs.append({
                'question': question['text'],
                'answer': answer,
                'question_id': i
            })
    
    # Analyze answers
    if qa_pairs:
        answer_summary = "\n\n".join([
            f"Question {qa['question_id']}: {qa['question']}\n"
            f"Student's Answer: {qa['answer']}"
            for qa in qa_pairs
        ])
        
        result = analyze_answer(
            question="Based on all the student's answers to the career assessment questions, recommend suitable programs.",
            answer=answer_summary,
            programs=programs
        )
        
        # Store the LLM analysis result
        session.llm_analysis = result
        session.save()
    else:
        result = "No answers found to analyze."
    
    return render(request, 'path_finding/results.html', {
        'session': session,
        'qa_pairs': qa_pairs,
        'result': result
    })
