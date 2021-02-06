from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def check_topic_owner(topic, request):
    """Make sure the user associated with a topic matches the currently logged in user."""
    if topic.owner != request.user:
        raise Http404


def index(request):
    """The home page for Leaning Log."""
    return render(request, 'learning_logs/index.html')


def topics(request):
    """Show all topics"""
    # If the user is authenticated, the user's topic and public topics will be shown
    if request.user.is_authenticated:
        topics = Topic.objects.filter(Q(public=True) | Q(owner=request.user)).order_by('date_added')
    # If not, only the public topics will be shown
    else:
        topics = Topic.objects.filter(public=True).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'learning_logs/topics.html', context)


@login_required()
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = get_object_or_404(Topic, id=topic_id)
    # Make sure the topic belongs to the current user.
    check_topic_owner(topic, request)

    # The minus sign in front of date_added, sorts the result in reverse order
    # The last entries added will be displayed in first
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'learning_logs/topic.html', context)


@login_required()
def new_topic(request):
    """Add a new topic."""
    if request.method != "POST":
        # Nenhum dado submetido; Cria um formulário em branco.
        form = TopicForm()
    else:
        # Dados de POST submetidos; processa os dados.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')

    # Mostra um formulário branco ou inválido.
    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)


@login_required()
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = get_object_or_404(Topic, id=topic_id)

    # Protect the page. Only the owner must have access
    check_topic_owner(topic, request)

    if request.method != "POST":
        # Nenhum dado submetido; Cria um formulário em branco.
        form = EntryForm()
    else:
        # Dados de POST submetidos; processa os dados.
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            form.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    # Mostra um formulário branco ou inválido.
    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required()
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    # Protect the page. Only the owner must have access
    check_topic_owner(topic, request)

    if request.method != "POST":
        # Requisição inicial; preenche previamente o formulário com a entrada atual
        form = EntryForm(instance=entry)
    else:
        # Dados de POST submetidos; processa os dados.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    # Se não for método POST e não for um form válido
    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)
