from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
from django.utils.crypto import get_random_string
from django.db.models.signals import post_save
from django.dispatch import receiver

# Define status choices for posts
STATUS = ((0, "Draft"), (1, "Published"))


class Post(models.Model):
    # Unique identifier for the post
    slug = models.SlugField(max_length=18, blank=True, unique=True)
    # User who created the post
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    # Main text content of the post
    content = models.TextField()
    # Image associated with the post
    image = CloudinaryField('image', blank=True, null=True)
    # Timestamp for post creation
    created_on = models.DateTimeField(auto_now_add=True)
    # Timestamp for last update
    updated_on = models.DateTimeField(auto_now=True)
    # Publishing status of the post
    status = models.IntegerField(choices=STATUS, default=1)
    # Users who liked the post
    likes = models.ManyToManyField(User, related_name='post_like')

    def save(self, *args, **kwargs):
        self.create_slug()
        super(Post, self).save(*args, **kwargs)

    def create_slug(self):
        # Generate a unique random slug if not provided
        if not self.slug:
            slug_is_wrong = True
            while slug_is_wrong:
                self.slug = get_random_string(18, '0123456789')
                slug_is_wrong = False
                if Post.objects.filter(slug=self.slug).exists():
                    slug_is_wrong = True

    def number_of_likes(self):
        # Count the number of likes for the post
        return self.likes.count()


class Comment(models.Model):
    # Post that this comment belongs to
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments"
    )
    # User who wrote the comment
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments_author"
    )
    # Content of the comment
    body = models.TextField()
    # Whether the comment is approved or not
    approved = models.BooleanField(default=True)
    # Timestamp for comment creation
    created_on = models.DateTimeField(auto_now_add=True)
    # Parent comment for nested comments
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


class Follow(models.Model):
    # User who is following
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE)
    # User being followed
    following = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE)
    # Timestamp for when the follow relationship was created
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower} follows {self.following}"


class Report(models.Model):
    # Post being reported
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='reports')
    # User who reported the post
    reporter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reports')
    # Reason for reporting
    reason = models.TextField()
    # Timestamp for when the report was created
    created_on = models.DateTimeField(auto_now_add=True)
    # Whether the report has been reviewed
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"Report by {self.reporter} on {self.post.slug}"


class Profile(models.Model):
    # User associated with this profile
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    # Short biography of the user
    bio = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    # Create or update user profile when a User instance is saved
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()
