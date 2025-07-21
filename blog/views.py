from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Prefetch
from blog.models import Comment, Post, Tag


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': getattr(post, 'comments_count', 0),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.first().title if post.tags.exists() else '',
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': getattr(tag, 'posts_count', 0),
    }


def index(request):
    most_popular_posts_qs = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_tags_with_posts_count()
        .fetch_with_comments_count()
    )
    most_popular_posts = list(most_popular_posts_qs[:5])

     most_fresh_posts_qs = (
        Post.objects.order_by('-published_at')
        .select_related('author')
        .prefetch_tags_with_posts_count()
        .annotate(comments_count=Count('comments'))
    )
    most_fresh_posts = list(most_fresh_posts_qs[:20])
    
    popular_tags = list(Tag.objects.popular()[:5])

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
     post = get_object_or_404(
        Post.objects.select_related('author')
        .prefetch_tags_with_posts_count()
        .fetch_with_comments_count(),
        slug=slug
    )

    comments = post.comments.select_related('author').all()

    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in comments]

    related_tags = post.tags.all()

    context = {
        'post': serialize_post(post),
        'comments': serialized_comments,
        'tags': [serialize_tag(tag) for tag in related_tags],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag = get_object_or_404(Tag.objects.with_posts_count(), title=tag_title)

    related_posts_qs = (
        Post.objects.filter(tags__title=tag_title)
        .select_related('author')
        .prefetch_tags_with_posts_count()
        .fetch_with_comments_count()
    )
    related_posts = list(related_posts_qs[:20])

    popular_tags = list(Tag.objects.popular()[:5])

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_tags_with_posts_count()
        .fetch_with_comments_count()
    )
    most_popular_posts = list(most_popular_posts_qs[:5])

    context = {
        'tag': serialize_tag(tag),
        'posts': [serialize_post(post) for post in related_posts],
        'popular_tags': [serialize_tag(t) for t in popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
