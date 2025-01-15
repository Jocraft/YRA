from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Student
from .questions import QUESTIONS, QUESTIONS_AR, calculate_vark_scores
from .models import LearningStyleTest

@login_required
def learning_methods(request):
    students = Student.objects.all()
    selected_student = None
    latest_test = None
    group_count = request.GET.get('group_count', '4')  # Default to 4 groups

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
        'group_count': group_count,
    }
    
    # Print the context for debugging
    print(f"Context latest_test: {context['latest_test']}")
    return render(request, 'learning_methods/learning.html', context)

@login_required
def fill_test(request, student_id):
    # Get language preference from query parameter, default to English
    lang = request.GET.get('lang', 'en')
    questions = QUESTIONS_AR if lang == 'ar' else QUESTIONS

    # Get previously answered questions from session
    session_key = f'test_answers_{student_id}'
    saved_answers = request.session.get(session_key, {})

    if request.method == 'POST':
        student = get_object_or_404(Student, id=student_id)
        
        # Get all answers (now multiple per question)
        answers = {}
        for i in range(len(QUESTIONS)):
            q_num = f'q{i+1}'
            # getlist gets all selected values for each question
            answers[q_num] = ','.join(request.POST.getlist(q_num))
        
        # If this is a final submission (not just language switch)
        if 'submit_test' in request.POST:
            # Calculate VARK scores
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
            
            # Clear session data after successful submission
            if session_key in request.session:
                del request.session[session_key]
            
            return redirect('learning_methods:results', student_id=student_id)
        else:
            # Save answers to session for language switch
            request.session[session_key] = answers
            # Redirect to same page with new language
            new_lang = 'ar' if lang == 'en' else 'en'
            return redirect(f'{request.path}?lang={new_lang}')

    context = {
        'questions': questions,
        'student_id': student_id,
        'current_lang': lang,
        'saved_answers': saved_answers,
    }
    return render(request, 'learning_methods/fill_test.html', context)

@login_required
def results(request, student_id):
    student = Student.objects.get(id=student_id)
    latest_test = LearningStyleTest.objects.filter(student=student).first()
    group_count = request.GET.get('group_count', '4')  # Get group count from URL
    
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
    
    # Calculate combined groups based on group_count
    combined_groups = {}
    if group_count in ['2', '3']:
        # Calculate VA group (Visual + Aural)
        va_score = percentages['V'] + percentages['A']
        # Calculate RK group (Read/Write + Kinesthetic)
        rk_score = percentages['R'] + percentages['K']
        
        combined_groups['VA'] = va_score / 2  # Average of V and A
        combined_groups['RK'] = rk_score / 2  # Average of R and K
        
        if group_count == '3':
            # Simplified logic for Special class:
            # If any two of these conditions are met, classify as Special
            conditions_met = 0
            
            # Condition 1: No single score dominates (max score < 35%)
            if max(percentages.values()) < 35:
                conditions_met += 1
            
            # Condition 2: No score is too low (min score > 15%)
            if min(percentages.values()) > 15:
                conditions_met += 1
            
            # Condition 3: VA and RK groups are within 25% of each other
            if abs(combined_groups['VA'] - combined_groups['RK']) < 25:
                conditions_met += 1
            
            # If at least 2 conditions are met, classify as Special
            if conditions_met >= 2:
                combined_groups['S'] = sum(percentages.values()) / 4  # Average of all scores
                # Make Special class slightly more attractive by boosting its score
                combined_groups['S'] *= 1.1  # 10% boost to encourage Special classification
    
    # Determine dominant styles based on group count
    if group_count == '4':
        # Original logic for 4 groups
        max_percentage = max(percentages.values())
        dominant_styles = [
            style for style, pct in percentages.items() 
            if pct == max_percentage
        ]
    else:
        # Logic for 2 or 3 groups
        max_combined = max(combined_groups.values())
        dominant_styles = [
            group for group, score in combined_groups.items()
            if score == max_combined
        ]
    
    context = {
        'results': results,
        'percentages': percentages,
        'combined_groups': combined_groups,
        'dominant_styles': dominant_styles,
        'student_id': student_id,
        'test_date': latest_test.date_taken,
        'group_count': group_count,
    }
    return render(request, 'learning_methods/results.html', context)
