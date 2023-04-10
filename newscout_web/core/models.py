import spacy
import random
import uuid
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import URLValidator
from django.contrib.auth.models import AbstractUser
from simple_history.models import HistoricalRecords

nlp = spacy.load("en_core_web_sm")

class BaseModel(models.Model):
    """
    Base model to record the creation and modification datetime
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    modified_at = models.DateTimeField(auto_now=True, verbose_name="Last Modified At")

    class Meta:
        abstract = True


class HashTag(models.Model):
    """
    Stores hashtag topics
    """
    name = models.CharField(max_length=255)
    is_trending = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return self.name
    

class Domain(BaseModel):
    """
    Stores domains of the news sites
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    id = models.CharField(primary_key=True, max_length=255, blank=True)
    url = models.URLField(blank=True, null=True,validators=[URLValidator()])
    is_active = models.BooleanField(default=False)
    default_image = models.ImageField(
        upload_to="static/images/domain/", default="static/images/domain/default.png"
    )

    class Meta:
        verbose_name_plural = "Domain"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
    

class User(AbstractUser):
    """
    Base model to store users
    """
    username = None
    email = models.EmailField(max_length=255, unique=True)
    bio = models.TextField(null=True)
    is_writer = models.BooleanField(default=False)
    is_editor = models.BooleanField(default=False)
    interested_hashtags = models.ManyToManyField(HashTag, blank=True)
    domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.CASCADE)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __unicode__(self):
        return self.first_name + " " + self.last_name
    
    def __str__(self):
        return self.first_name + " "+ self.last_name
        

class Category(BaseModel):
    """
    Model to store categories
    """
    name = models.CharField(max_length=255, blank=True, null=True)
    default_image_url = models.URLField()

    class Meta:
        verbose_name_plural = "Categories"

    @classmethod
    def get_default_image(cls, self, category):
        options = Category.objects.filter(name=category.name)
        if len(options) == 0:
            current = Category.objects.order_by("?").first()
        else:
            current = random.choice(options)
            return current.default_image_url

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
    

class CategoryAssociation(models.Model):
    """
    Model to store association between categories
    """
    parent = models.ForeignKey(
        Category, related_name="parent_category", on_delete=models.CASCADE
    )
    child = models.ForeignKey(
        Category, related_name="child_category", on_delete=models.CASCADE
    )

    def __unicode__(self):
        return "%s > %s " % (self.parent.name, self.child.name)
        

class Article(BaseModel):
    """
    Model to store 
    """
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable = False)
    domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=600)
    category = models.ForeignKey(Category, blank=True, null=True, on_delete=models.CASCADE)
    hash_tags = models.ManyToManyField(HashTag, blank=True, default=None)
    source_url = models.TextField(validators=[URLValidator()])
    cover_image = models.TextField(validators=[URLValidator()])
    blurb = models.TextField(blank=True, null=True)
    full_text = models.TextField()
    published_on = models.DateTimeField()
    is_active = models.BooleanField(default=False)
    popular = models.BooleanField(default=False)
    avg_rating = models.FloatField(blank=True, null=True)
    rating_count = models.FloatField(blank=True, null=True)
    edited_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    edited_on = models.DateTimeField(auto_now=True)
    indexed_on = models.DateTimeField(default=timezone.now)
    spam = models.BooleanField(default=False)
    default_image_url = models.URLField()
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="author",
    )
    slug = models.SlugField(max_length=250, allow_unicode=True, blank=True, null=True)  # type: ignore
    history = HistoricalRecords(history_change_reason_field=models.TextField(null=True), inherit=True)

    def __unicode__(self):
        return "{} - {} - {} - {} -{}\n".format(
            self.author, self.title, self.published_on, self.domain, self.hash_tags
        )
    
    def __str__(self):
        return self.title    

    def save(self, *args, **kwargs):
        super(Article, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = "{0}-{1}".format(slugify(self.title), self.pk)
            self.save()

        if not self.source_url:
            self.source_url = "http://newscout.in/news/aricle/{0}-{1}".format(
                slugify(self.title), self.pk
            )
            self.save()

    def entities(self):
        """
        this method is used to extract entities using spaCy
        """
        results = []
        doc = nlp(f"{self.title} {self.blurb}")
        white_listed_labels = ["PRODUCT", "PERSON", "ORG", "GPE"]
        for ent in doc.ents:
            if ent.label_ in white_listed_labels:
                results.append((ent.text, ent.label_))
        return list(set(results))
    
class ArticleMedia(BaseModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    image_url =  models.TextField(validators=[URLValidator()], blank=True, null=True)
    video_url = models.TextField(validators=[URLValidator()], blank=True, null=True)

    def __unicode__(self):
        return "%s > %s" % (self.article, self.article.title)
    
    def __str__(self):
        return "%s > %s" % (self.article, self.article.title)
    

class ArticleInteraction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    rating = models.FloatField(null=True)
    like = models.BooleanField(null=True,default=False)
    bookmarked = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s -> %s" % (self.article, self.rating)
    
    def __str__(self):
        return "%s : %s" % (self.article, self.rating)
    

class SubMenu(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    hash_tags = models.ManyToManyField(HashTag)
    icon = models.ImageField(upload_to="static/icons/", blank=True, null=True)

    def __unicode__(self):
        return self.category.name

    def __str__(self):
        return self.category.name
    

class Menu(models.Model):
    domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    submenu = models.ManyToManyField(SubMenu)
    icon = models.ImageField(upload_to="static/icons/", blank=True, null=True)

    def __unicode__(self):
        return self.category.name

    def __str__(self):
        return self.category.name
    

class Devices(models.Model):
    device_id = models.CharField(max_length=255, blank=True, null=True)
    device_name = models.CharField(max_length=255, blank=True, null=True)
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.CASCADE
    )

    def __unicode__(self):
        return "device_id = {}, device_name = {}".format(self.device_id, self.device_name)
    
    def __str__(self):
        return "device_id = {}, device_name = {}".format(self.device_id, self.device_name)
    

class Notification(models.Model):
    breaking_news = models.BooleanField(default=False)
    daily_edition = models.BooleanField(default=False)
    personalized = models.BooleanField(default=False)
    device = models.ForeignKey(Devices, on_delete=models.CASCADE)

    def __unicode__(self):
        return "breaking_news={}, daily_edition={}, personalized={}".format(self.breaking_news, self.daily_edition, self.personalized)
    

class SocialAccount(models.Model):
    """
    this model is used to store social account details
    """
    provider = models.CharField(max_length=200)
    social_account_id = models.CharField(max_length=200)
    image_url = models.CharField(max_length=250, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Social Accounts"

    def __str__(self):
        return "{0} {1}".format(self.user, self.social_account_id)
    


class ScoutFrontier(models.Model):
    """
    this model is used for sourcing new articles at
    higher frequency
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    url = models.URLField(default="http://nowhe.re")

    def __str__(self):
        return "%s -> %s" % (self.category, self.url)

    def __unicode__(self):
        return "%s -> %s" % (self.category, self.url)
    

class ScoutedItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.URLField(default="http://nowhe.re")

    def __str__(self):
        return "%s -> %s" % (self.category, self.title)

    def __unicode__(self):
        return "%s -> %s" % (self.category, self.title)
    

class TrendingArticle(BaseModel):
    """
    this model is used to store trending article cluster
    """

    domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.CASCADE)
    articles = models.ManyToManyField(Article)
    active = models.BooleanField(default=True)
    score = models.FloatField(default=0.0)

    def __str__(self):
        return self.articles.first()

    def __unicode__(self):
        return self.articles.first()
    

class DailyDigest(BaseModel):
    device = models.ForeignKey(Devices, blank=True, null=True, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, blank=True, null=True, on_delete=models.CASCADE)
    articles = models.ManyToManyField(Article)

    def __unicode__(self):
        return self.device
    

class Comment(BaseModel):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=250)
    reply = models.ForeignKey(
        "Comment",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    def __str__(self):
        return self.comment
    

SUBS_TYPE = (
    ("Basic", "Basic"),
    ("Silver", "Silver"),
    ("Gold", "Gold"),
)

class Subscription(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subs_type = models.CharField(choices=SUBS_TYPE, max_length=50)
    expires_on = models.DateTimeField(blank=True, null=True)
    auto_renew = models.BooleanField(default=True)
    payement_mode = models.CharField(choices=SUBS_TYPE, max_length=50)

    def __str__(self):
        return "{self.user}, {self.sub_typ}"