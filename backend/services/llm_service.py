

from groq import Groq
from typing import Dict, Optional, List
import config
from utils.error_handler import logger, handle_errors, LLMError, ErrorContext
from agents.cache_manager import cache


class LLMAgent:
    """Handles all LLM operations using Groq"""
    
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise LLMError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
        logger.info(f"LLM Agent initialized with model: {self.model}")
    
    @handle_errors
    def summarize_text(
        self,
        text: str,
        detail_level: str = "medium",
        paper_id: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the given text
        
        Args:
            text: Text to summarize
            detail_level: 'short', 'medium', or 'long'
            paper_id: Optional paper ID for caching
            
        Returns:
            Summary text
        """
        
        if text is None or not text:
            logger.warning("Cannot summarize: text is None or empty")
            return None
            
        with ErrorContext(f"Summarizing text (level: {detail_level})"):
            # Check cache if paper_id provided
            if paper_id:
                cache_key = f"summary_{paper_id}_{detail_level}"
                cached_summary = cache.get(cache_key)
                if cached_summary:
                    logger.info(f"Cache hit for summary: {paper_id}")
                    return cached_summary
            
            # Determine prompt based on detail level
            prompts = {
                "short": "Provide a 2-3 sentence summary highlighting only the main contribution and findings.",
                "medium": "Provide a comprehensive paragraph (4-6 sentences) summarizing the key objectives, methodology, findings, and implications.",
                "long": "Provide a detailed multi-paragraph summary covering: 1) Research objectives and motivation, 2) Methodology and approach, 3) Key findings and results, 4) Implications and significance."
            }
            
            prompt = prompts.get(detail_level, prompts["medium"])
            
            # Truncate text if too long (to avoid token limits)
            max_chars = 15000
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
                logger.warning(f"Text truncated to {max_chars} characters")
            
            # Make LLM call
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert academic research assistant. Provide clear, concise, and accurate summaries of research papers."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nText to summarize:\n{text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Cache the result if paper_id provided
            if paper_id:
                cache.set(cache_key, summary)
            
            logger.info("Summary generated successfully")
            return summary
    
    @handle_errors
    def identify_research_gaps(
        self,
        text: str,
        paper_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Identify research gaps from paper text
        
        Args:
            text: Full paper text
            paper_id: Optional paper ID for caching
            
        Returns:
            Dictionary with methodology_gaps, knowledge_gaps, and future_directions
        """
        with ErrorContext("Identifying research gaps"):
            # Check cache
            if paper_id:
                cache_key = f"gaps_{paper_id}"
                cached_gaps = cache.get(cache_key)
                if cached_gaps:
                    logger.info(f"Cache hit for research gaps: {paper_id}")
                    return cached_gaps
            
            # Truncate if needed
            max_chars = 20000
            if len(text) > max_chars:
                # Try to keep conclusion/future work sections
                text = text[-max_chars:]
                logger.warning(f"Text truncated to last {max_chars} characters")
            
            prompt = """Analyze this research paper and identify:

1. **Methodology Gaps**: Limitations in the research methods, experimental design, data collection, or analysis techniques used.

2. **Knowledge Gaps**: Areas where the current understanding is incomplete, contradictory findings, or unexplored aspects of the topic.

3. **Future Directions**: Explicit suggestions for future research mentioned by the authors, and implicit opportunities you identify.

Provide your analysis in the following format:

METHODOLOGY GAPS:
[Your analysis here]

KNOWLEDGE GAPS:
[Your analysis here]

FUTURE DIRECTIONS:
[Your analysis here]

Paper text:
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert research analyst specializing in identifying research gaps and opportunities in academic papers."
                },
                {
                    "role": "user",
                    "content": prompt + text
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse the response
            gaps = self._parse_research_gaps(content)
            
            # Cache the result
            if paper_id:
                cache.set(cache_key, gaps)
            
            logger.info("Research gaps identified successfully")
            return gaps
    
    def _parse_research_gaps(self, text: str) -> Dict[str, str]:
        """Parse LLM response into structured gaps dictionary"""
        gaps = {
            "methodology_gaps": "",
            "knowledge_gaps": "",
            "future_directions": ""
        }
        
        # Split by sections
        sections = text.split("METHODOLOGY GAPS:")
        if len(sections) > 1:
            remaining = sections[1]
            
            if "KNOWLEDGE GAPS:" in remaining:
                parts = remaining.split("KNOWLEDGE GAPS:")
                gaps["methodology_gaps"] = parts[0].strip()
                remaining = parts[1]
                
                if "FUTURE DIRECTIONS:" in remaining:
                    parts = remaining.split("FUTURE DIRECTIONS:")
                    gaps["knowledge_gaps"] = parts[0].strip()
                    gaps["future_directions"] = parts[1].strip()
                else:
                    gaps["knowledge_gaps"] = remaining.strip()
            else:
                gaps["methodology_gaps"] = remaining.strip()
        else:
            # If parsing fails, return the whole text as methodology gaps
            gaps["methodology_gaps"] = text.strip()
        
        return gaps
    
    def _call_llm(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        """
        Helper method to call the LLM with a prompt
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens in the response
            temperature: Temperature for response generation
            
        Returns:
            The LLM response text
        """
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content.strip()
    
    @handle_errors
    def extract_key_findings(
        self,
        text: str,
        paper_id: Optional[str] = None
    ) -> str:
        """
        Extract key findings from paper text
        
        Args:
            text: Full paper text
            paper_id: Optional paper ID for caching
            
        Returns:
            Key findings as formatted text
        """
        with ErrorContext("Extracting key findings"):
            # Check cache
            if paper_id:
                cache_key = f"findings_{paper_id}"
                cached_findings = cache.get(cache_key)
                if cached_findings:
                    logger.info(f"Cache hit for key findings: {paper_id}")
                    return cached_findings
            
            # Truncate if needed
            max_chars = 15000
            if len(text) > max_chars:
                text = text[:max_chars] + "..."
                logger.warning(f"Text truncated to {max_chars} characters")
            
            prompt = """Extract and list the key findings from this research paper. Focus on:
- Main results and discoveries
- Significant observations
- Important conclusions
- Novel contributions

Present as a bulleted list of clear, concise points.

Paper text:
"""
            
            messages = [
                {
                    "role": "system",
                    "content": "You are an expert at extracting and summarizing key research findings from academic papers."
                },
                {
                    "role": "user",
                    "content": prompt + text
                }
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            
            findings = response.choices[0].message.content.strip()
            
            # Cache the result
            if paper_id:
                cache.set(cache_key, findings)
            
            logger.info("Key findings extracted successfully")
            return findings
        
        
     # ==================== LITERATURE REVIEW GENERATION ====================
    
    @handle_errors#(default_return={})
    def detect_themes(self, papers: List[Dict]) -> Dict[str, List[str]]:
        """
        Detect main themes across papers
        
        Args:
            papers: List of paper dictionaries
            
        Returns:
            Dictionary mapping theme names to paper titles
        """
        # Create summary of all papers
        papers_summary = []
        for i, paper in enumerate(papers[:20], 1):  # Limit to 20 papers for context
            title = paper.get('title', 'Untitled')
            abstract = paper.get('abstract', '')[:300]  # Truncate abstracts
            papers_summary.append(f"{i}. {title}\nAbstract: {abstract}\n")
        
        papers_text = "\n".join(papers_summary)
        
        prompt = f"""You are an expert research analyst. Analyze these papers and identify 3-5 main THEMES that connect them.

        For each theme:
        1. Give it a descriptive name (2-4 words)
        2. List which paper numbers belong to that theme

        Papers:
        {papers_text}

        Format your response EXACTLY like this:

        THEME 1: [Theme name]
        Papers: 1, 3, 5

        THEME 2: [Theme name]
        Papers: 2, 4, 7

        ... etc"""
        
        with ErrorContext("Theme Detection"):
            response = self._call_llm(prompt, max_tokens=800, temperature=0.5)
            
            # Parse themes
            themes = {}
            current_theme = None
            
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('THEME'):
                    # Extract theme name
                    theme_name = line.split(':', 1)[1].strip()
                    current_theme = theme_name
                    themes[current_theme] = []
                elif line.startswith('Papers:') and current_theme:
                    # Extract paper indices
                    paper_nums = line.replace('Papers:', '').strip()
                    # Convert to actual paper titles
                    for num_str in paper_nums.split(','):
                        try:
                            idx = int(num_str.strip()) - 1
                            if 0 <= idx < len(papers):
                                themes[current_theme].append(papers[idx].get('title', ''))
                        except:
                            continue
            
            logger.info(f"Detected {len(themes)} themes across {len(papers)} papers")
            return themes
    
    @handle_errors#(default_return="")
    def generate_literature_review(
        self,
        papers: List[Dict],
        query: str,
        detail_level: str = "medium",
        review_type: str = "thematic"
    ) -> str:
        """
        Generate a comprehensive literature review
        
        Args:
            papers: List of paper dictionaries with summaries
            query: Original search query/topic
            detail_level: 'short', 'medium', or 'long'
            review_type: 'thematic', 'chronological', or 'methodological'
            
        Returns:
            Complete literature review text (5-10 pages for medium)
        """
        with ErrorContext("Literature Review Generation"):
            logger.info(f"Generating {detail_level} {review_type} literature review for {len(papers)} papers")
            
            # Step 1: Detect themes
            themes = self.detect_themes(papers)
            
            # Step 2: Generate introduction
            introduction = self._generate_introduction(query, papers, themes)
            
            # Step 3: Generate thematic sections
            thematic_sections = self._generate_thematic_sections(papers, themes, detail_level)
            
            # Step 4: Generate methodology section
            methodology_section = self._generate_methodology_section(papers)
            
            # Step 5: Generate synthesis
            synthesis = self._generate_synthesis(papers, themes)
            
            # Step 6: Generate research gaps
            gaps_section = self._generate_gaps_section(papers)
            
            # Step 7: Generate conclusion
            conclusion = self._generate_conclusion(query, papers, themes)
            
            # Step 8: Generate references
            references = self._generate_references(papers)
            
            # Combine all sections
            review = f"""# Literature Review: {query.title()}

        {introduction}

        ## Thematic Analysis

        {thematic_sections}

        ## Methodological Approaches

        {methodology_section}

        ## Synthesis of Findings

        {synthesis}

        ## Research Gaps and Future Directions

        {gaps_section}

        ## Conclusion

        {conclusion}

        ## References

        {references}
        """
            
            logger.info("Literature review generated successfully")
            return review
    
    def _generate_introduction(self, query: str, papers: List[Dict], themes: Dict) -> str:
        """Generate introduction section"""
        # Get year range
        years = [p.get('year') for p in papers if p.get('year') and isinstance(p.get('year'), int)]
        year_range = f"{min(years)}-{max(years)}" if years else "recent years"
        
        prompt = f"""Write a professional introduction for a literature review on "{query}".

        Context:
        - Number of papers reviewed: {len(papers)}
        - Time period: {year_range}
        - Main themes identified: {', '.join(themes.keys())}

        The introduction should:
        1. Provide context and background on the topic
        2. State the scope and purpose of this review
        3. Briefly mention the main themes to be discussed
        4. Be 2-3 paragraphs (200-300 words)

        Write in academic style, third person."""
        
        return self._call_llm(prompt, max_tokens=500)
    
    def _generate_thematic_sections(self, papers: List[Dict], themes: Dict, detail_level: str) -> str:
        """Generate sections for each theme"""
        sections = []
        
        for theme_name, paper_titles in themes.items():
            # Get full paper data for this theme
            theme_papers = [p for p in papers if p.get('title') in paper_titles]
            
            if not theme_papers:
                continue
            
            # Create summary of papers in this theme
            papers_info = []
            for paper in theme_papers[:10]:  # Limit to avoid token limits
                title = paper.get('title', 'Untitled')
                authors = ', '.join(paper.get('authors', [])[:2])
                year = paper.get('year', '')
                summary = paper.get('abstract_summary') or paper.get('abstract', '')[:200]
                papers_info.append(f"- {authors} ({year}): {title}\n  {summary}")
            
            papers_text = "\n\n".join(papers_info)
            
            prompt = f"""Write a section for a literature review about the theme: "{theme_name}"

            Papers in this theme:
            {papers_text}

            Your section should:
            1. Introduce the theme
            2. Synthesize the main findings from these papers
            3. Highlight agreements and disagreements
            4. Note any patterns or trends
            5. Be 2-3 paragraphs (300-400 words)

            Use citations like: (Author et al., Year)
            Write in academic style."""
            
            section_text = self._call_llm(prompt, max_tokens=600)
            sections.append(f"### {theme_name}\n\n{section_text}\n")
        
        return "\n".join(sections)
    
    def _generate_methodology_section(self, papers: List[Dict]) -> str:
        """Generate methodology overview section"""
        # Extract methodological info
        methods_info = []
        for paper in papers[:15]:
            if paper.get('key_findings'):
                methods_info.append(f"- {paper.get('title', 'Unknown')}: {paper['key_findings'][:150]}")
        
        methods_text = "\n".join(methods_info) if methods_info else "Various methodologies employed"
        
        prompt = f"""Analyze and summarize the methodological approaches used across these research papers.

        Papers and their methodologies:
        {methods_text}

        Create a section that:
        1. Categorizes the main methodological approaches (e.g., quantitative, qualitative, mixed-methods, computational, experimental)
        2. Notes the frequency of different approaches
        3. Discusses the strengths and limitations observed
        4. Be 2 paragraphs (200-250 words)

        Write in academic style."""
        
        return self._call_llm(prompt, max_tokens=500)
    
    def _generate_synthesis(self, papers: List[Dict], themes: Dict) -> str:
        """Generate synthesis section"""
        # Collect key findings
        findings = []
        for paper in papers[:20]:
            if paper.get('key_findings'):
                findings.append(f"- {paper.get('title')}: {paper['key_findings'][:150]}")
        
        findings_text = "\n".join(findings) if findings else "Various findings reported"
        
        prompt = f"""Synthesize the main findings across all reviewed papers.

        Key findings from papers:
        {findings_text}

        Main themes: {', '.join(themes.keys())}

        Your synthesis should:
        1. Identify areas of consensus
        2. Highlight contradictions or debates
        3. Note emerging trends
        4. Discuss the overall contribution to the field
        5. Be 2-3 paragraphs (300-350 words)

        Write in academic style, connecting findings across papers."""
        
        return self._call_llm(prompt, max_tokens=600)
    
    def _generate_gaps_section(self, papers: List[Dict]) -> str:
        """Generate research gaps section"""
        # Collect gap information
        all_gaps = {
            'methodology': [],
            'knowledge': [],
            'future': []
        }
        
        for paper in papers:
            if paper.get('research_gaps'):
                gaps = paper['research_gaps']
                if gaps.get('methodology_gaps'):
                    all_gaps['methodology'].append(gaps['methodology_gaps'][:150])
                if gaps.get('knowledge_gaps'):
                    all_gaps['knowledge'].append(gaps['knowledge_gaps'][:150])
                if gaps.get('future_directions'):
                    all_gaps['future'].append(gaps['future_directions'][:150])
        
        gaps_summary = f"""Methodology gaps mentioned:
        {chr(10).join(['- ' + g for g in all_gaps['methodology'][:10]])}

        Knowledge gaps mentioned:
        {chr(10).join(['- ' + g for g in all_gaps['knowledge'][:10]])}

        Future directions suggested:
        {chr(10).join(['- ' + g for g in all_gaps['future'][:10]])}"""
                
        prompt = f"""Analyze and synthesize the research gaps across all reviewed papers.

        {gaps_summary}

        Create a section that:
        1. Summarizes major methodology gaps
        2. Identifies key knowledge gaps
        3. Suggests priority areas for future research
        4. Be 2-3 paragraphs (300-350 words)

        Write in academic style."""
        
        return self._call_llm(prompt, max_tokens=600)
    
    def _generate_conclusion(self, query: str, papers: List[Dict], themes: Dict) -> str:
        """Generate conclusion section"""
        prompt = f"""Write a conclusion for a literature review on "{query}".

        Context:
        - {len(papers)} papers reviewed
        - Main themes: {', '.join(themes.keys())}

        The conclusion should:
        1. Summarize the state of research in this field
        2. Highlight the most important findings
        3. Note the significance of this work
        4. Suggest implications for future research
        5. Be 2 paragraphs (200-250 words)

        Write in academic style."""
        
        return self._call_llm(prompt, max_tokens=500)
    
    def _generate_references(self, papers: List[Dict]) -> str:
        """Generate references section"""
        references = []
        
        for i, paper in enumerate(papers, 1):
            authors = paper.get('authors', ['Unknown'])
            author_str = ', '.join(authors[:3])
            if len(authors) > 3:
                author_str += ' et al.'
            
            year = paper.get('year', 'n.d.')
            title = paper.get('title', 'Untitled')
            venue = paper.get('venue', '')
            url = paper.get('url', '')
            
            ref = f"{i}. {author_str} ({year}). {title}."
            if venue:
                ref += f" *{venue}*."
            if url:
                ref += f" {url}"
            
            references.append(ref)
        
        return "\n\n".join(references)


# Global LLM agent instance
llm_agent = LLMAgent()