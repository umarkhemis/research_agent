from django.db import models
from django.utils import timezone


class Project(models.Model):
    """Research project containing multiple papers and searches"""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects'
        ordering = ['-updated_at']

    def __str__(self):
        return f"Project: {self.name}"


class Paper(models.Model):
    """Academic paper with metadata and analysis"""
    # Identifiers
    title = models.CharField(max_length=500)
    doi = models.CharField(max_length=255, unique=True, null=True, blank=True, db_index=True)
    arxiv_id = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    semantic_scholar_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    url = models.URLField(max_length=500, null=True, blank=True)
    
    # Metadata
    abstract = models.TextField(null=True, blank=True)
    authors = models.JSONField(default=list, blank=True)
    year = models.IntegerField(null=True, blank=True, db_index=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    publication_date = models.CharField(max_length=50, null=True, blank=True)
    citation_count = models.IntegerField(default=0)
    
    # PDF info
    has_pdf = models.BooleanField(default=False)
    pdf_url = models.URLField(max_length=500, null=True, blank=True)
    pdf_text = models.TextField(null=True, blank=True)
    
    # AI Analysis
    abstract_summary_short = models.TextField(null=True, blank=True)
    abstract_summary_medium = models.TextField(null=True, blank=True)
    abstract_summary_long = models.TextField(null=True, blank=True)
    pdf_summary_short = models.TextField(null=True, blank=True)
    pdf_summary_medium = models.TextField(null=True, blank=True)
    pdf_summary_long = models.TextField(null=True, blank=True)
    
    key_findings = models.TextField(null=True, blank=True)
    methodology_gaps = models.TextField(null=True, blank=True)
    knowledge_gaps = models.TextField(null=True, blank=True)
    future_directions = models.TextField(null=True, blank=True)
    
    # Source database
    source = models.CharField(max_length=50, null=True, blank=True)
    
    # Processing status
    processing_status = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'papers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Paper: {self.title[:50]}..."


class ProjectPaper(models.Model):
    """Association between projects and papers"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_papers')
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE, related_name='project_papers')
    
    # Paper-specific notes in this project
    notes = models.TextField(null=True, blank=True)
    tags = models.JSONField(default=list, blank=True)
    importance = models.IntegerField(default=3)  # 1-5 scale
    
    added_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'project_papers'
        unique_together = [['project', 'paper']]

    def __str__(self):
        return f"ProjectPaper: {self.project.name} - {self.paper.title[:30]}"


class SearchHistory(models.Model):
    """History of searches performed"""
    query = models.CharField(max_length=500, db_index=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='searches', null=True, blank=True)
    
    # Search parameters
    limit = models.IntegerField(null=True, blank=True)
    summary_level = models.CharField(max_length=20, null=True, blank=True)
    year_from = models.IntegerField(null=True, blank=True)
    year_to = models.IntegerField(null=True, blank=True)
    open_access_only = models.BooleanField(default=False)
    databases = models.JSONField(default=list, blank=True)
    
    # Results
    results_count = models.IntegerField(null=True, blank=True)
    papers_found = models.JSONField(default=list, blank=True)
    
    # Timing
    search_duration_seconds = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'search_history'
        ordering = ['-created_at']

    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class ProjectNote(models.Model):
    """General notes for a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='notes')
    
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField()
    note_type = models.CharField(max_length=50, null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_notes'
        ordering = ['-created_at']

    def __str__(self):
        return f"Note: {self.title or 'Untitled'}"


class LiteratureReview(models.Model):
    """Generated literature reviews"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='literature_reviews', null=True, blank=True)
    
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField()
    papers_included = models.JSONField(default=list, blank=True)
    
    # Generation parameters
    review_type = models.CharField(max_length=50, null=True, blank=True)
    detail_level = models.CharField(max_length=20, null=True, blank=True)
    
    # Export formats (cached)
    markdown_content = models.TextField(null=True, blank=True)
    latex_content = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'literature_reviews'
        ordering = ['-created_at']

    def __str__(self):
        return f"Review: {self.title or 'Untitled'}"
