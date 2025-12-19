from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Note, Question, Answer
from ai_services.openai_client import correct_and_structure_note, verify_answer_accuracy, verify_publication_accuracy

@login_required
def note_list(request, note_id=None):
    notes = Note.objects.filter(user=request.user).order_by('-created_at')
    active_note = None
    is_creating = request.GET.get('new') == 'true'
    
    if note_id:
        active_note = get_object_or_404(Note, id=note_id, user=request.user)
    elif notes.exists() and not is_creating:
        active_note = notes.first()
        
    return render(request, 'notes/note_list.html', {
        'notes': notes,
        'active_note': active_note,
        'is_creating': is_creating,
        'now': timezone.now()
    })

@login_required
def note_create(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        ai_result = correct_and_structure_note(content)
        corrected = ai_result.get('corrected_content', '')
        title = ai_result.get('title', 'Note sans titre')
        if not corrected and 'content' in ai_result:
            corrected = ai_result['content']
        truth_score = ai_result.get('truth_score', 0)
        issues = ai_result.get('issues', [])
        note = Note.objects.create(
            user=request.user, title=title, original_content=content,
            corrected_content=corrected, truth_score=truth_score, issues=issues
        )
        return redirect('note_list_detail', note_id=note.id)
    return redirect('/notes/?new=true')

@login_required
def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_delete(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return redirect('note_list_detail', note_id=note_id)

@login_required
def community_list(request):
    questions_qs = Question.objects.select_related('user').all().order_by('-created_at')
    
    # Préparer les données pour le template (éviter les problèmes de rendu)
    feed_posts = []
    for q in questions_qs:
        username = q.user.username if q.user else "Utilisateur inconnu"
        if not username:
            username = "Utilisateur inconnu"
            
        feed_posts.append({
            'id': q.id,
            'content': q.content.strip() if q.content else "",
            'created_at': q.created_at,
            'author_name': username,
            'author_initial': username[0].upper() if username else "?",
            'author_profile_picture': q.user.profile_picture if q.user else None,
            'truth_score': getattr(q, 'truth_score', 0),
            'answers_count': q.answers.count(),
        })
    
    # Statistiques personnalisées pour la sidebar gauche
    user_questions_count = Question.objects.filter(user=request.user).count()
    user_answers_count = Answer.objects.filter(user=request.user).count()
    
    # Tendances pour la sidebar droite (données simulées pour le moment)
    trending_topics = [
        {'tag': '#Physique', 'title': 'Théorie de la relativité', 'count': '24 Q', 'progress': 85},
        {'tag': '#IA-Éthique', 'title': "L'impact des LLM sur le travail", 'count': '15 Q', 'progress': 65},
        {'tag': '#Biotech', 'title': 'Séquençage ADN 2.0', 'count': '12 Q', 'progress': 45},
    ]

    return render(request, 'notes/community_list.html', {
        'feed_posts': feed_posts,
        'user_q_count': user_questions_count,
        'user_a_count': user_answers_count,
        'trends': trending_topics
    })

@login_required
def community_post_create(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            ai_result = verify_publication_accuracy(content)
            Question.objects.create(
                user=request.user, 
                content=content,
                truth_score=ai_result.get('truth_score', 0),
                ai_feedback=ai_result.get('ai_feedback', '')
            )
    return redirect('community_list')

@login_required
def community_post_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all()
    return render(request, 'notes/community_post_detail.html', {
        'question': question,
        'answers': answers
    })

@login_required
def community_answer_create(request, question_id):
    if request.method == 'POST':
        question = get_object_or_404(Question, id=question_id)
        content = request.POST.get('content')
        if content:
            ai_result = verify_answer_accuracy(question.content, content)
            Answer.objects.create(
                user=request.user, question=question, content=content,
                truth_score=ai_result.get('truth_score', 0), ai_feedback=ai_result.get('ai_feedback', '')
            )
    return redirect('community_post_detail', question_id=question_id)
