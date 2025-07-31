"""
Knowledge Base models for the RAG system.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.core.models import (
    SharedModel, ProcessingStatusModel, MetadataModel,
    VersionedModel, SoftDeleteModel
)


class KnowledgeBase(SharedModel, ProcessingStatusModel, MetadataModel, SoftDeleteModel):
    """
    A knowledge base contains documents and provides context for RAG operations.
    """
    name = models.CharField(
        _('Name'),
        max_length=200,
        help_text=_('Name of the knowledge base')
    )

    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Description of the knowledge base contents and purpose')
    )

    # Embedding Configuration
    embedding_model = models.CharField(
        _('Embedding model'),
        max_length=100,
        default='nomic-embed-text',
        help_text=_('Embedding model used for this knowledge base')
    )

    embedding_dimension = models.PositiveIntegerField(
        _('Embedding dimension'),
        default=768,
        help_text=_('Dimension of the embedding vectors')
    )

    # Processing Configuration
    chunk_size = models.PositiveIntegerField(
        _('Chunk size'),
        default=1000,
        validators=[MinValueValidator(100), MaxValueValidator(8000)],
        help_text=_('Size of text chunks for processing')
    )

    chunk_overlap = models.PositiveIntegerField(
        _('Chunk overlap'),
        default=200,
        validators=[MinValueValidator(0), MaxValueValidator(500)],
        help_text=_('Overlap between adjacent chunks')
    )

    # Vector Store Configuration
    vector_store_type = models.CharField(
        _('Vector store type'),
        max_length=50,
        choices=[
            ('pgvector', 'PostgreSQL pgvector'),
            ('qdrant', 'Qdrant'),
        ],
        default='pgvector'
    )

    # Statistics
    document_count = models.PositiveIntegerField(
        _('Document count'),
        default=0,
        help_text=_('Number of documents in this knowledge base')
    )

    chunk_count = models.PositiveIntegerField(
        _('Chunk count'),
        default=0,
        help_text=_('Number of text chunks in this knowledge base')
    )

    total_tokens = models.PositiveBigIntegerField(
        _('Total tokens'),
        default=0,
        help_text=_('Total number of tokens processed')
    )

    # Quality Metrics
    avg_chunk_quality = models.FloatField(
        _('Average chunk quality'),
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text=_('Average quality score of chunks (0-1)')
    )

    last_indexed_at = models.DateTimeField(
        _('Last indexed at'),
        null=True,
        blank=True,
        help_text=_('When the knowledge base was last fully indexed')
    )

    class Meta:
        verbose_name = _('Knowledge Base')
        verbose_name_plural = _('Knowledge Bases')
        db_table = 'kb_knowledge_base'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_public']),
            models.Index(fields=['status']),
            models.Index(fields=['embedding_model']),
        ]

    def __str__(self):
        return self.name

    def increment_document_count(self):
        """Increment the document count."""
        self.document_count = models.F('document_count') + 1
        self.save(update_fields=['document_count'])
        self.refresh_from_db()

    def decrement_document_count(self):
        """Decrement the document count."""
        if self.document_count > 0:
            self.document_count = models.F('document_count') - 1
            self.save(update_fields=['document_count'])
            self.refresh_from_db()

    def update_statistics(self):
        """Update knowledge base statistics based on current documents and chunks."""
        from apps.documents.models import Document, DocumentChunk

        # Update document count
        self.document_count = self.documents.filter(is_deleted=False).count()

        # Update chunk count and total tokens
        chunk_stats = DocumentChunk.objects.filter(
            document__knowledge_base=self,
            document__is_deleted=False
        ).aggregate(
            total_chunks=models.Count('id'),
            total_tokens=models.Sum('token_count') or 0
        )

        self.chunk_count = chunk_stats['total_chunks']
        self.total_tokens = chunk_stats['total_tokens']

        # Update average chunk quality
        quality_avg = DocumentChunk.objects.filter(
            document__knowledge_base=self,
            document__is_deleted=False,
            quality_score__isnull=False
        ).aggregate(
            avg_quality=models.Avg('quality_score')
        )

        self.avg_chunk_quality = quality_avg['avg_quality'] or 0.0

        self.save(update_fields=[
            'document_count', 'chunk_count', 'total_tokens', 'avg_chunk_quality'
        ])

    def get_embedding_config(self):
        """Get the embedding configuration for this knowledge base."""
        from django.conf import settings

        embedding_config = settings.EMBEDDING_CONFIG.copy()
        embedding_config['model'] = self.embedding_model
        embedding_config['dimension'] = self.embedding_dimension

        return embedding_config

    def get_vector_store_config(self):
        """Get the vector store configuration for this knowledge base."""
        from django.conf import settings

        config = settings.VECTOR_STORE_CONFIG[self.vector_store_type].copy()
        config['collection_name'] = f"kb_{self.id}"
        config['dimension'] = self.embedding_dimension

        return config


class KnowledgeBaseTag(models.Model):
    """
    Tags for categorizing knowledge bases.
    """
    name = models.CharField(
        _('Name'),
        max_length=50,
        unique=True
    )

    color = models.CharField(
        _('Color'),
        max_length=7,
        default='#007bff',
        help_text=_('Hex color code for the tag')
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Knowledge Base Tag')
        verbose_name_plural = _('Knowledge Base Tags')
        db_table = 'kb_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class KnowledgeBaseTagRelation(models.Model):
    """
    Many-to-many relationship between knowledge bases and tags.
    """
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='tag_relations'
    )

    tag = models.ForeignKey(
        KnowledgeBaseTag,
        on_delete=models.CASCADE,
        related_name='kb_relations'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Knowledge Base Tag Relation')
        verbose_name_plural = _('Knowledge Base Tag Relations')
        db_table = 'kb_tag_relation'
        unique_together = ['knowledge_base', 'tag']

    def __str__(self):
        return f"{self.knowledge_base.name} - {self.tag.name}"


class KnowledgeBaseAccess(models.Model):
    """
    Track access to knowledge bases for analytics.
    """
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='access_logs'
    )

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='kb_accesses'
    )

    access_type = models.CharField(
        _('Access type'),
        max_length=20,
        choices=[
            ('view', _('View')),
            ('search', _('Search')),
            ('query', _('Query')),
            ('edit', _('Edit')),
            ('delete', _('Delete')),
        ]
    )

    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True
    )

    user_agent = models.TextField(
        _('User agent'),
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Knowledge Base Access')
        verbose_name_plural = _('Knowledge Base Accesses')
        db_table = 'kb_access'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['knowledge_base', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]

    def __str__(self):
        return f"{self.user.display_name} - {self.access_type} - {self.knowledge_base.name}"


class KnowledgeBaseVersion(VersionedModel, MetadataModel):
    """
    Versioning for knowledge bases to track changes over time.
    """
    knowledge_base = models.ForeignKey(
        KnowledgeBase,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    name = models.CharField(
        _('Name'),
        max_length=200
    )

    description = models.TextField(
        _('Description'),
        blank=True
    )

    changes = models.TextField(
        _('Changes'),
        blank=True,
        help_text=_('Description of changes in this version')
    )

    document_count_snapshot = models.PositiveIntegerField(
        _('Document count snapshot'),
        default=0
    )

    chunk_count_snapshot = models.PositiveIntegerField(
        _('Chunk count snapshot'),
        default=0
    )

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='kb_versions_created'
    )

    class Meta:
        verbose_name = _('Knowledge Base Version')
        verbose_name_plural = _('Knowledge Base Versions')
        db_table = 'kb_version'
        ordering = ['-version', '-created_at']
        unique_together = ['knowledge_base', 'version']

    def __str__(self):
        return f"{self.knowledge_base.name} v{self.version}"