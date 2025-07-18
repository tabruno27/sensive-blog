from django.shortcuts import render
from django.db.models import Count, Prefetch
from django.http import Http404
from blog.models import Comment, Post, Tag


def serialize_post(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else None,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Tag.objects.prefetch_for_posts())
        .fetch_with_comments_count()[:5]
    )

    most_fresh_posts = (
        Post.objects.order_by('-published_at')
        .select_related('author')
        .prefetch_related(Tag.objects.prefetch_for_posts())
        .fetch_with_comments_count()
    )

    popular_tags = Tag.objects.popular()[:5]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Tag.objects.prefetch_for_posts())
        .fetch_with_comments_count()[:5]
    )

    popular_tags = Tag.objects.popular()[:5]

    post = (
        Post.objects.select_related('author')
        .prefetch_related('likes', Tag.objects.prefetch_for_posts())
        .annotate(comments_count=Count('comments'))
        .get(slug=slug)
    )

    comments = post.comments.select_related('author')

    context = {
        'post': {
            **serialize_post(post),
            'text': post.text,
            'likes_amount': post.likes.count(),
            'comments': [{
                'text': comment.text,
                'published_at': comment.published_at,
                'author': comment.author.username,
            } for comment in comments],
        },
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(Tag.objects.prefetch_for_posts())
        .fetch_with_comments_count()[:5]
    )

    popular_tags = Tag.objects.popular()[:5]

    tag = Tag.objects.with_posts_count().get(title=tag_title)

    related_posts = (
        tag.posts.select_related('author')
        .prefetch_related(Tag.objects.prefetch_for_posts())
        .annotate(comments_count=Count('comments'))[:20]
    )

    context = {
        'tag': tag.title,
        'posts': [serialize_post(post) for post in related_posts],
        'popular_tags': [serialize_tag(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
