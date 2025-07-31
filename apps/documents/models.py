"""
Document models for the RAG system.
"""
import os
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.core.files.storage import default_storage
from apps.core.models import (
    BaseModel, ProcessingStatusModel, MetadataModel, SoftDeleteModel
)


def document_upload_path(instance, filename):
    """Generate upload path for documents."""
    return f"documents/{instance.knowledge_base.id}/{instance.id}/{filename}"


class Document(BaseModel, ProcessingStatusModel, MetadataModel, SoftDeleteModel):
    """
    A document that can be processed and indexed into a knowledge base.
    """
    knowledge_base = models.ForeignKey(
        'knowledge_bases.KnowledgeBase',
        on_delete=models.CASCADE,
        related_name='documents'
    )

    title = models.CharField(
        _('Title'),
        max_length=500,
        help_text=_('Document title or filename')
    )

    content = models.TextField(
        _('Content'),
        blank=True,
        help_text=_('Extracted text content from the document')
    )

    # File Information
    file = models.FileField(
        _('File'),
        upload_to=document_upload_path,
        null=True,
        blank=True,
        help_text=_('Original document file')
    )

    file_type = models.CharField(
        _('File type'),
        max_length=10,
        choices=[
            ('pdf', 'PDF'),
            ('docx', 'Microsoft Word'),
            ('txt', 'Text File'),
            ('md', 'Markdown'),
            ('xlsx', 'Excel'),
            ('png', 'PNG Image'),
            ('jpg', 'JPEG Image'),
            ('jpeg', 'JPEG Image'),
        ],
        blank=True
    )

    file_size = models.PositiveBigIntegerField(
        _('File size'),
        default=0,
        help_text=_('File size in bytes')
    )

    mime_type = models.CharField(
        _('MIME type'),
        max_length=100,
        blank=True
    )

    # Content Metrics
    char_count = models.PositiveIntegerField(
        _('Character count'),
        default=0,
        help_text=_('Number of characters in the document')
    )

    word_count = models.PositiveIntegerField(
        _('Word count'),
        default=0,
        help_text=_('Number of words in the document')
    )

    token_count = models.PositiveIntegerField(
        _('Token count'),
        default=0,
        help_text=_('Estimated number of tokens in the document')
    )

    # Processing Information
    language = models.CharField(
        _('Language'),
        max_length=10,
        default='en',
        choices=[
            ('en', 'English'),
            ('fr', 'French'),
            ('de', 'German'),
            ('nl', 'Dutch'),
            ('auto', 'Auto-detect'),
        ]
    )

    quality_score = models.FloatField(
        _('Quality score'),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Quality score of the extracted content (0-1)')
    )

    # Chunking Information
    chunk_count = models.PositiveIntegerField(
        _('Chunk count'),
        default=0,
        help_text=_('Number of chunks generated from this document')
    )

    # Upload Information
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_documents'
    )

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        db_table = 'docs_document'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['knowledge_base', 'status']),
            models.Index(fields=['file_type']),
            models.Index(fields=['language']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Override save to update file information."""
        if self.file:
            self.file_size = self.file.size
            # Extract file extension
            _, ext = os.path.splitext(self.file.name)
            if ext:
                self.file_type = ext[1:].lower()

        # Update knowledge base document count
        is_new = not self.pk
        super().save(*args, **kwargs)

        if is_new:
            self.knowledge_base.increment_document_count()

    def delete(self, *args, **kwargs):
        """Override delete to update knowledge base statistics."""
        kb = self.knowledge_base
        super().delete(*args, **kwargs)
        kb.decrement_document_count()

    def calculate_content_metrics(self):
        """Calculate and update content metrics."""
        if self.content:
            self.char_count = len(self.content)
            self.word_count = len(self.content.split())
            # Simple token estimation (characters / 4)
            self.token_count = max(1, self.char_count // 4)
        else:
            self.char_count = 0
            self.word_count = 0
            self.token_count = 0

    def get_file_extension(self):
        """Get the file extension."""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''

    def is_image(self):
        """Check if the document is an image."""
        return self.file_type in ['png', 'jpg', 'jpeg']

    def is_text_based(self):
        """Check if the document is text-based."""
        return self.file_type in ['txt', 'md']

    def can_extract_text(self):
        """Check if text can be extracted from this document type."""
        return self.file_type in ['pdf', 'docx', 'txt', 'md', 'png', 'jpg', 'jpeg']


class DocumentChunk(BaseModel, MetadataModel):
    """
    A chunk of text extracted from a document for RAG processing.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks'
    )

    content = models.TextField(
        _('Content'),
        help_text=_('Text content of this chunk')
    )

    # Position Information
    chunk_index = models.PositiveIntegerField(
        _('Chunk index'),
        help_text=_('Sequential index of this chunk within the document')
    )

    start_char = models.PositiveIntegerField(
        _('Start character'),
        default=0,
        help_text=_('Starting character position in the original document')
    )

    end_char = models.PositiveIntegerField(
        _('End character'),
        default=0,
        help_text=_('Ending character position in the original document')
    )

    # Content Metrics
    char_count = models.PositiveIntegerField(
        _('Character count'),
        default=0
    )

    word_count = models.PositiveIntegerField(
        _('Word count'),
        default=0
    )

    token_count = models.PositiveIntegerField(
        _('Token count'),
        default=0
    )

    # Quality Metrics
    quality_score = models.FloatField(
        _('Quality score'),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Quality score of this chunk (0-1)')
    )

    coherence_score = models.FloatField(
        _('Coherence score'),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Coherence score of this chunk (0-1)')
    )

    # Embedding Information
    is_embedded = models.BooleanField(
        _('Is embedded'),
        default=False,
        help_text=_('Whether embeddings have been generated for this chunk')
    )

    embedding_model = models.CharField(
        _('Embedding model'),
        max_length=100,
        blank=True,
        help_text=_('Model used to generate embeddings')
    )

    # Semantic Information
    summary = models.TextField(
        _('Summary'),
        blank=True,
        help_text=_('AI-generated summary of this chunk')
    )

    keywords = models.JSONField(
        _('Keywords'),
        default=list,
        blank=True,
        help_text=_('Extracted keywords from this chunk')
    )

    entities = models.JSONField(
        _('Entities'),
        default=list,
        blank=True,
        help_text=_('Extracted named entities from this chunk')
    )

    class Meta:
        verbose_name = _('Document Chunk')
        verbose_name_plural = _('Document Chunks')
        db_table = 'docs_chunk'
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['is_embedded']),
            models.Index(fields=['quality_score']),
        ]

    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"

    def save(self, *args, **kwargs):
        """Override save to calculate metrics."""
        self.calculate_metrics()
        super().save(*args, **kwargs)

    def calculate_metrics(self):
        """Calculate content metrics for this chunk."""
        if self.content:
            self.char_count = len(self.content)
            self.word_count = len(self.content.split())
            # Simple token estimation
            self.token_count = max(1, self.char_count // 4)

    def get_context_window(self, window_size=1):
        """Get surrounding chunks for context."""
        chunks = DocumentChunk.objects.filter(
            document=self.document,
            chunk_index__range=(
                max(0, self.chunk_index - window_size),
                self.chunk_index + window_size
            )
        ).order_by('chunk_index')

        return list(chunks)

    def get_preview(self, max_length=200):
        """Get a preview of the chunk content."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[:max_length] + "..."


class DocumentProcessingTask(BaseModel, ProcessingStatusModel):
    """
    Track document processing tasks.
    """
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='processing_tasks'
    )

    task_type = models.CharField(
        _('Task type'),
        max_length=50,
        choices=[
            ('extract_text', _('Extract Text')),
            ('chunk_text', _('Chunk Text')),
            ('generate_embeddings', _('Generate Embeddings')),
            ('extract_entities', _('Extract Entities')),
            ('generate_summary', _('Generate Summary')),
            ('quality_assessment', _('Quality Assessment')),
        ]
    )

    task_id = models.CharField(
        _('Task ID'),
        max_length=255,
        blank=True,
        help_text=_('Celery task ID for tracking')
    )

    progress = models.FloatField(
        _('Progress'),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Task progress (0-1)')
    )

    result = models.JSONField(
        _('Result'),
        default=dict,
        blank=True,
        help_text=_('Task result data')
    )

    error_details = models.TextField(
        _('Error details'),
        blank=True,
        help_text=_('Detailed error information if task failed')
    )

    class Meta:
        verbose_name = _('Document Processing Task')
        verbose_name_plural = _('Document Processing Tasks')
        db_table = 'docs_processing_task'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', 'task_type']),
            models.Index(fields=['status']),
            models.Index(fields=['task_id']),
        ]

    def __str__(self):
        return f"{self.document.title} - {self.get_task_type_display()}"