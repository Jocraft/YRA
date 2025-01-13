from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Student
from .questions import QUESTIONS, calculate_vark_scores
from .models import LearningStyleTest

@login_required
def learning_methods(request):
    students = Student.objects.all()
    selected_student = None
    latest_test = None

    student_id = request.GET.get('student')
    if student_id:
        # Use get_object_or_404 for better error handling
        selected_student = get_object_or_404(Student, id=student_id)
        # Add print statements for debugging
        print(f"Selected student: {selected_student}")
        
        # Check for existing test
        latest_test = LearningStyleTest.objects.filter(student_id=student_id).order_by('-date_taken').first()
        print(f"Latest test found: {latest_test}")

    context = {
        'active_page': 'learning_methods',
        'students': students,
        'student_id': student_id,
        'selected_student': selected_student,
        'latest_test': latest_test,
    }
    
    # Print the context for debugging
    print(f"Context latest_test: {context['latest_test']}")
    return render(request, 'learning_methods/learning.html', context)

@login_required
def fill_test(request, student_id):
    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        
        # Get all answers (now multiple per question)
        answers = {}
        for i in range(len(QUESTIONS)):
            q_num = f'q{i+1}'
            # getlist gets all selected values for each question
            answers[q_num] = ','.join(request.POST.getlist(q_num))
        
        # Calculate VARK scores (need to modify the calculation for multiple answers)
        results = calculate_vark_scores(answers)
        
        # Save to database
        test = LearningStyleTest(
            student=student,
            **answers,
            visual_score=results['V'],
            aural_score=results['A'],
            read_write_score=results['R'],
            kinesthetic_score=results['K']
        )
        test.save()
        
        return redirect('learning_methods:results', student_id=student_id)

    context = {
        'questions': QUESTIONS,
        'student_id': student_id,
    }
    return render(request, 'learning_methods/fill_test.html', context)

@login_required
def results(request, student_id):
    student = Student.objects.get(id=student_id)
    latest_test = LearningStyleTest.objects.filter(student=student).first()
    
    if not latest_test:
        return redirect('learning_methods:learning')
    
    results = {
        'V': latest_test.visual_score,
        'A': latest_test.aural_score,
        'R': latest_test.read_write_score,
        'K': latest_test.kinesthetic_score
    }
    
    # Calculate percentages
    total = sum(results.values())
    percentages = {
        style: (count / total) * 100 
        for style, count in results.items()
    }
    
    # Determine dominant styles
    max_percentage = max(percentages.values())
    dominant_styles = [
        style for style, pct in percentages.items() 
        if pct == max_percentage
    ]
    
    context = {
        'results': results,
        'percentages': percentages,
        'dominant_styles': dominant_styles,
        'student_id': student_id,
        'test_date': latest_test.date_taken,
    }
    return render(request, 'learning_methods/results.html', context)
