from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .forms import EmailForm, CommentForm
from taggit.models import Tag
from django.db.models import Count

# Create your views here.

# class PostView(ListView):
#
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/list.html'

def post_list(request, tag_slug=None):

    object_list = Post.published.all()
    tag = None
    if tag:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/list.html', {'posts': posts, 'page': page, 'tag': tag})


def post_detail(request, year, month, day, post):

    post = get_object_or_404(Post,
                             status='published',
                             publish__year=year,
                             publish__month=month,
                             publish__day=day,
                             slug=post)

    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_id = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_id).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/detail.html', {'post': post, 'comment_form': comment_form, 'new_content': new_comment,
                                                'comments': comments, 'similar_posts': similar_posts})

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == 'POST':
        email_form = EmailForm(request.POST)
        if email_form.is_valid():
            cd = email_form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} recommend you reading {}'.format(cd['name'], post.title)
            message = 'Read {} at {}/n {}\'s comments {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, cd['name'], cd['to'])
            sent = True

    else:
        email_form = EmailForm()

    return render(request, 'blog/share.html', {'post': post, 'email_form': email_form, 'sent': sent, })









