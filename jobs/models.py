from django.db import models
from django.conf import settings
from django.utils.text import slugify



# ==========================
# CHOICES
# ==========================

JOB_TYPE_CHOICES = [
    ('full_time', 'Full Time'),
    ('part_time', 'Part Time'),
    ('contract', 'Contract'),
    ('remote', 'Remote'),
    ('internship', 'Internship'),
]

EXPERIENCE_CHOICES = [
    ('junior', 'Junior'),
    ('mid', 'Mid-level'),
    ('senior', 'Senior'),
    ('lead', 'Lead'),
]



# ==========================
# CATEGORY MODEL
# ==========================

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# ==========================
# TAG MODEL
# ==========================

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
        