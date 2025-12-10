import time
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import Project, Paper, ProjectPaper, SearchHistory, ProjectNote, LiteratureReview
from .serializers import (
    ProjectSerializer, ProjectDetailSerializer, PaperSerializer, PaperListSerializer,
    ProjectPaperSerializer, SearchHistorySerializer, ProjectNoteSerializer,
    LiteratureReviewSerializer
)
from services.search_service import SearchAgent
from services.pdf_service import PDFAgent
from services.llm_service import LLMAgent
from services.literature_review_service import LiteratureReviewAgent
from services.export_service import ExportAgent


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Project CRUD operations"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectSerializer
    
    @action(detail=True, methods=['post'])
    def add_paper(self, request, pk=None):
        """Add a paper to the project"""
        project = self.get_object()
        paper_id = request.data.get('paper_id')
        
        if not paper_id:
            return Response(
                {'error': 'paper_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            paper = Paper.objects.get(id=paper_id)
        except Paper.DoesNotExist:
            return Response(
                {'error': 'Paper not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already exists
        if ProjectPaper.objects.filter(project=project, paper=paper).exists():
            return Response(
                {'error': 'Paper already in project'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the relationship
        project_paper = ProjectPaper.objects.create(
            project=project,
            paper=paper,
            notes=request.data.get('notes', ''),
            tags=request.data.get('tags', []),
            importance=request.data.get('importance', 3)
        )
        
        serializer = ProjectPaperSerializer(project_paper)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'], url_path='papers/(?P<paper_id>[^/.]+)')
    def remove_paper(self, request, pk=None, paper_id=None):
        """Remove a paper from the project"""
        project = self.get_object()
        try:
            project_paper = ProjectPaper.objects.get(project=project, paper_id=paper_id)
            project_paper.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProjectPaper.DoesNotExist:
            return Response(
                {'error': 'Paper not in project'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def papers(self, request, pk=None):
        """Get all papers in a project"""
        project = self.get_object()
        project_papers = project.project_papers.all()
        serializer = ProjectPaperSerializer(project_papers, many=True)
        return Response(serializer.data)


class PaperViewSet(viewsets.ModelViewSet):
    """ViewSet for Paper operations"""
    queryset = Paper.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaperListSerializer
        return PaperSerializer
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Search for papers across databases"""
        query = request.data.get('query')
        if not query:
            return Response(
                {'error': 'query is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get search parameters
        limit = request.data.get('limit', 10)
        year_from = request.data.get('year_from')
        year_to = request.data.get('year_to')
        open_access_only = request.data.get('open_access_only', False)
        databases = request.data.get('databases', ['semantic_scholar', 'arxiv'])
        summary_level = request.data.get('summary_level', 'medium')
        project_id = request.data.get('project_id')
        
        # Perform search
        start_time = time.time()
        search_agent = SearchAgent()
        papers_data = search_agent.search_papers(
            query=query,
            limit=limit,
            year_from=year_from,
            year_to=year_to,
            open_access_only=open_access_only,
            databases=databases
        )
        search_duration = time.time() - start_time
        
        # Save papers to database
        saved_papers = []
        paper_ids = []
        
        for paper_data in papers_data:
            # Check if paper already exists by DOI or semantic_scholar_id or arxiv_id
            existing_paper = None
            if paper_data.get('doi'):
                existing_paper = Paper.objects.filter(doi=paper_data['doi']).first()
            if not existing_paper and paper_data.get('semantic_scholar_id'):
                existing_paper = Paper.objects.filter(
                    semantic_scholar_id=paper_data['semantic_scholar_id']
                ).first()
            if not existing_paper and paper_data.get('arxiv_id'):
                existing_paper = Paper.objects.filter(arxiv_id=paper_data['arxiv_id']).first()
            
            if existing_paper:
                saved_papers.append(existing_paper)
                paper_ids.append(existing_paper.id)
            else:
                # Create new paper
                paper = Paper.objects.create(
                    title=paper_data.get('title', ''),
                    doi=paper_data.get('doi'),
                    arxiv_id=paper_data.get('arxiv_id'),
                    semantic_scholar_id=paper_data.get('semantic_scholar_id'),
                    url=paper_data.get('url'),
                    abstract=paper_data.get('abstract'),
                    authors=paper_data.get('authors', []),
                    year=paper_data.get('year'),
                    venue=paper_data.get('venue'),
                    publication_date=paper_data.get('publication_date'),
                    citation_count=paper_data.get('citation_count', 0),
                    has_pdf=paper_data.get('has_pdf', False),
                    pdf_url=paper_data.get('pdf_url'),
                    source=paper_data.get('source'),
                )
                saved_papers.append(paper)
                paper_ids.append(paper.id)
        
        # Save search history
        search_history = SearchHistory.objects.create(
            query=query,
            project_id=project_id,
            limit=limit,
            summary_level=summary_level,
            year_from=year_from,
            year_to=year_to,
            open_access_only=open_access_only,
            databases=databases,
            results_count=len(saved_papers),
            papers_found=paper_ids,
            search_duration_seconds=search_duration
        )
        
        # Serialize and return
        serializer = PaperListSerializer(saved_papers, many=True)
        return Response({
            'papers': serializer.data,
            'count': len(saved_papers),
            'search_id': search_history.id,
            'duration': search_duration
        })
    
    @action(detail=True, methods=['post'])
    def summarize(self, request, pk=None):
        """Generate summary for a paper"""
        paper = self.get_object()
        level = request.data.get('level', 'medium')
        use_pdf = request.data.get('use_pdf', False)
        
        llm_agent = LLMAgent()
        
        # Get text to summarize
        if use_pdf and paper.pdf_text:
            text = paper.pdf_text
            field_prefix = 'pdf_summary'
        else:
            text = paper.abstract
            field_prefix = 'abstract_summary'
        
        if not text:
            return Response(
                {'error': 'No text available to summarize'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate summary
        summary = llm_agent.generate_summary(text, level)
        
        # Save summary
        field_name = f'{field_prefix}_{level}'
        setattr(paper, field_name, summary)
        paper.save()
        
        return Response({
            'summary': summary,
            'level': level,
            'source': 'pdf' if use_pdf else 'abstract'
        })
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Extract research gaps and key findings"""
        paper = self.get_object()
        
        llm_agent = LLMAgent()
        
        # Use PDF text if available, otherwise abstract
        text = paper.pdf_text if paper.pdf_text else paper.abstract
        
        if not text:
            return Response(
                {'error': 'No text available to analyze'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract gaps and findings
        gaps = llm_agent.extract_research_gaps(text)
        findings = llm_agent.extract_key_findings(text)
        
        # Save to paper
        paper.methodology_gaps = gaps.get('methodology_gaps', '')
        paper.knowledge_gaps = gaps.get('knowledge_gaps', '')
        paper.future_directions = gaps.get('future_directions', '')
        paper.key_findings = findings
        paper.save()
        
        return Response({
            'methodology_gaps': paper.methodology_gaps,
            'knowledge_gaps': paper.knowledge_gaps,
            'future_directions': paper.future_directions,
            'key_findings': paper.key_findings
        })
    
    @action(detail=True, methods=['post'])
    def download_pdf(self, request, pk=None):
        """Download and extract PDF text"""
        paper = self.get_object()
        
        if not paper.pdf_url:
            return Response(
                {'error': 'No PDF URL available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pdf_agent = PDFAgent()
        pdf_text = pdf_agent.download_and_extract(paper.pdf_url)
        
        if pdf_text:
            paper.pdf_text = pdf_text
            paper.has_pdf = True
            paper.save()
            return Response({
                'success': True,
                'text_length': len(pdf_text)
            })
        else:
            return Response(
                {'error': 'Failed to download or extract PDF'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class LiteratureReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Literature Review operations"""
    queryset = LiteratureReview.objects.all()
    serializer_class = LiteratureReviewSerializer
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a literature review"""
        project_id = request.data.get('project_id')
        paper_ids = request.data.get('paper_ids', [])
        review_type = request.data.get('review_type', 'thematic')
        detail_level = request.data.get('detail_level', 'medium')
        custom_instructions = request.data.get('custom_instructions', '')
        
        # Get papers
        if project_id:
            project = get_object_or_404(Project, id=project_id)
            papers = [pp.paper for pp in project.project_papers.all()]
        elif paper_ids:
            papers = Paper.objects.filter(id__in=paper_ids)
        else:
            return Response(
                {'error': 'Either project_id or paper_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not papers:
            return Response(
                {'error': 'No papers found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Prepare papers data
        papers_data = []
        for paper in papers:
            papers_data.append({
                'title': paper.title,
                'authors': paper.authors,
                'year': paper.year,
                'abstract': paper.abstract,
                'venue': paper.venue,
                'citation_count': paper.citation_count,
                'key_findings': paper.key_findings,
                'methodology_gaps': paper.methodology_gaps,
                'knowledge_gaps': paper.knowledge_gaps,
            })
        
        # Generate review
        lit_review_agent = LiteratureReviewAgent()
        review_content = lit_review_agent.generate_literature_review(
            papers=papers_data,
            review_type=review_type,
            detail_level=detail_level,
            custom_instructions=custom_instructions
        )
        
        # Save review
        review = LiteratureReview.objects.create(
            project_id=project_id,
            title=f"Literature Review - {review_type.title()}",
            content=review_content,
            papers_included=[p.id for p in papers],
            review_type=review_type,
            detail_level=detail_level,
            markdown_content=review_content
        )
        
        serializer = self.get_serializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SearchHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Search History (read-only)"""
    queryset = SearchHistory.objects.all()
    serializer_class = SearchHistorySerializer


class ProjectNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Project Notes"""
    queryset = ProjectNote.objects.all()
    serializer_class = ProjectNoteSerializer


class ExportViewSet(viewsets.ViewSet):
    """ViewSet for export operations"""
    
    @action(detail=False, methods=['post'])
    def papers(self, request):
        """Export papers in various formats"""
        paper_ids = request.data.get('paper_ids', [])
        export_format = request.data.get('format', 'json')
        
        if not paper_ids:
            return Response(
                {'error': 'paper_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        papers = Paper.objects.filter(id__in=paper_ids)
        export_agent = ExportAgent()
        
        # Convert papers to dict format
        papers_data = []
        for paper in papers:
            papers_data.append({
                'title': paper.title,
                'authors': paper.authors,
                'year': paper.year,
                'abstract': paper.abstract,
                'doi': paper.doi,
                'url': paper.url,
                'venue': paper.venue,
                'citation_count': paper.citation_count,
            })
        
        # Export based on format
        if export_format == 'bibtex':
            content = export_agent.export_bibtex(papers_data)
            content_type = 'text/plain'
        elif export_format == 'json':
            import json
            content = json.dumps(papers_data, indent=2)
            content_type = 'application/json'
        else:
            return Response(
                {'error': f'Unsupported format: {export_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'content': content,
            'format': export_format,
            'count': len(papers)
        })
    
    @action(detail=False, methods=['post'])
    def review(self, request):
        """Export literature review in various formats"""
        review_id = request.data.get('review_id')
        export_format = request.data.get('format', 'markdown')
        
        if not review_id:
            return Response(
                {'error': 'review_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review = get_object_or_404(LiteratureReview, id=review_id)
        export_agent = ExportAgent()
        
        if export_format == 'markdown':
            content = review.markdown_content or review.content
        elif export_format == 'latex':
            content = export_agent.export_latex(review.content, review.title)
        elif export_format == 'word':
            # Return URL for download instead of content
            return Response({
                'error': 'Word export requires file download endpoint',
                'format': export_format
            }, status=status.HTTP_501_NOT_IMPLEMENTED)
        else:
            return Response(
                {'error': f'Unsupported format: {export_format}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'content': content,
            'format': export_format,
            'title': review.title
        })


class StatisticsViewSet(viewsets.ViewSet):
    """ViewSet for dashboard statistics"""
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard statistics"""
        projects_count = Project.objects.count()
        papers_count = Paper.objects.count()
        searches_count = SearchHistory.objects.count()
        reviews_count = LiteratureReview.objects.count()
        
        # Recent activity
        recent_projects = Project.objects.order_by('-updated_at')[:5]
        recent_papers = Paper.objects.order_by('-created_at')[:5]
        recent_searches = SearchHistory.objects.order_by('-created_at')[:5]
        
        return Response({
            'counts': {
                'projects': projects_count,
                'papers': papers_count,
                'searches': searches_count,
                'reviews': reviews_count,
            },
            'recent': {
                'projects': ProjectSerializer(recent_projects, many=True).data,
                'papers': PaperListSerializer(recent_papers, many=True).data,
                'searches': SearchHistorySerializer(recent_searches, many=True).data,
            }
        })
