from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.crypto import get_random_string

STATUS = ((0, "Draft"), (1, "Published"))

class Post(models.Model):
    slug = models.SlugField(max_length=18, blank=True, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = CloudinaryField('image', default='placeholder')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    status = models.IntegerField(choices=STATUS, default=1)
    likes = models.ManyToManyField(User, related_name='post_like')

    def save(self, *args, **kwargs):
        self.create_slug()
        super(Post, self).save(*args, **kwargs)

    def create_slug(self):
        if not self.slug:
            slug_is_wrong = True
            while slug_is_wrong:
                self.slug = get_random_string(18, '0123456789')
                slug_is_wrong = False
                
                if Post.objects.filter(slug=self.slug).exists():
                    slug_is_wrong = True
    
    def number_of_likes(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments_author"
    )
    body = models.TextField()
    approved = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies'
    )

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"

class Report(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    reason = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.reporter} on {self.post.slug}"