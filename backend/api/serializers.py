from rest_framework import serializers
from .models import Project, Paper, ProjectPaper, SearchHistory, ProjectNote, LiteratureReview


class ProjectSerializer(serializers.ModelSerializer):
    papers_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'tags', 'created_at', 'updated_at', 'papers_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_papers_count(self, obj):
        return obj.project_papers.count()


class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'doi', 'arxiv_id', 'semantic_scholar_id', 'url',
            'abstract', 'authors', 'year', 'venue', 'publication_date', 'citation_count',
            'has_pdf', 'pdf_url', 'pdf_text',
            'abstract_summary_short', 'abstract_summary_medium', 'abstract_summary_long',
            'pdf_summary_short', 'pdf_summary_medium', 'pdf_summary_long',
            'key_findings', 'methodology_gaps', 'knowledge_gaps', 'future_directions',
            'source', 'processing_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaperListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing papers"""
    class Meta:
        model = Paper
        fields = [
            'id', 'title', 'authors', 'year', 'venue', 'citation_count',
            'has_pdf', 'source', 'abstract', 'created_at'
        ]


class ProjectPaperSerializer(serializers.ModelSerializer):
    paper = PaperListSerializer(read_only=True)
    paper_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProjectPaper
        fields = ['id', 'project', 'paper', 'paper_id', 'notes', 'tags', 'importance', 'added_at']
        read_only_fields = ['id', 'added_at']


class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = [
            'id', 'query', 'project', 'limit', 'summary_level',
            'year_from', 'year_to', 'open_access_only', 'databases',
            'results_count', 'papers_found', 'search_duration_seconds', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectNote
        fields = ['id', 'project', 'title', 'content', 'note_type', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class LiteratureReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiteratureReview
        fields = [
            'id', 'project', 'title', 'content', 'papers_included',
            'review_type', 'detail_level', 'markdown_content', 'latex_content', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed project serializer with papers and notes"""
    papers = ProjectPaperSerializer(source='project_papers', many=True, read_only=True)
    notes = ProjectNoteSerializer(many=True, read_only=True)
    
    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['papers', 'notes']
