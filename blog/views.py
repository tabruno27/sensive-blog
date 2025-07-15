from django.shortcuts import render
from django.db import models
from django.db.models import Count, Prefetch
from blog.models import Comment, Post, Tag



def get_related_posts_count(tag):
    return tag.posts.count()


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    tags = post.tags.all()
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in tags],
        'first_tag_title': tags[0].title if tags else None,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count if hasattr(tag, 'posts_count') else tag.posts.count(),
    }


def index(request):
    tag_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(tag_prefetch)
        .fetch_with_comments_count()
    )

    most_fresh_posts = (
        Post.objects.order_by('-published_at')
        .select_related('author')
        .prefetch_related(tag_prefetch)
        .fetch_with_comments_count()
    )

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).popular()[:5]

    context = {
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    tag_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

    post = (
        Post.objects.select_related('author')
        .prefetch_related('likes')
        .prefetch_related(tag_prefetch)
        .annotate(comments_count=Count('comments'))
        .get(slug=slug)
    )

    comments = Comment.objects.filter(post=post).select_related('author')
    serialized_comments = [{
        'text': comment.text,
        'published_at': comment.published_at,
        'author': comment.author.username,
    } for comment in comments]

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes.count(),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in post.tags.all()],
    }

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(tag_prefetch)
        .fetch_with_comments_count()[:5]
    )

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).popular()[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_optimized(tag) for tag in popular_tags],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    tag_prefetch = Prefetch(
        'tags',
        queryset=Tag.objects.annotate(posts_count=Count('posts'))
    )

    tag = Tag.objects.annotate(posts_count=Count('posts')).get(title=tag_title)

    most_popular_posts = (
        Post.objects.popular()
        .select_related('author')
        .prefetch_related(tag_prefetch)
        .fetch_with_comments_count()[:5]
    )

    related_posts = (
        tag.posts.select_related('author')
        .prefetch_related(tag_prefetch)
        .annotate(comments_count=Count('comments'))[:20]
    )

    popular_tags = Tag.objects.annotate(posts_count=Count('posts')).popular()[:5]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})