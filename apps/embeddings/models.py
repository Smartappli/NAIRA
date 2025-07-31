""" Embedding models for the RAG system. """
from django.db import models
# from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from apps.core.models import BaseModel, ProcessingStatusModel, MetadataModel


class EmbeddingModel(BaseModel, MetadataModel):
    """
    Configuration for embedding models available in the system.
    """
    name = models.CharField(
        _('Name'),
        max_length=100,
        unique=True,
        help_text=_('Name of the embedding model')
    )

    provider = models.CharField(
        _('Provider'),
        max_length=50,
        choices=[
            ('ollama', 'Ollama'),
            ('openai', 'OpenAI'),
            ('huggingface', 'Hugging Face'),
            ('sentence_transformers', 'Sentence Transformers'),
        ],
        help_text=_('Provider of the embedding model')
    )

    model_id = models.CharField(
        _('Model ID'),
        max_length=200,
        help_text=_('Identifier used by the provider')
    )

    dimension = models.PositiveIntegerField(
        _('Dimension'),
        help_text=_('Dimension of the embedding vectors')
    )

    max_tokens = models.PositiveIntegerField(
        _('Max tokens'),
        default=512,
        help_text=_('Maximum number of tokens the model can process')
    )

    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Description of the model and its capabilities')
    )

    is_active = models.BooleanField(
        _('Is active'),
        default=True,
        help_text=_('Whether this model is available for use')
    )

    # Performance Metrics
    avg_processing_time = models.FloatField(
        _('Average processing time'),
        default=0.0,
        help_text=_('Average processing time per token in milliseconds')
    )

    usage_count = models.PositiveBigIntegerField(
        _('Usage count'),
        default=0,
        help_text=_('Number of times this model has been used')
    )

    # Configuration
    config = models.JSONField(
        _('Configuration'),
        default=dict,
        blank=True,
        help_text=_('Model-specific configuration parameters')
    )

    class Meta:
        verbose_name = _('Embedding Model')
        verbose_name_plural = _('Embedding Models')
        db_table = 'embeddings_model'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.provider})"

    def increment_usage(self):
        """Increment the usage counter."""
        self.usage_count = models.F('usage_count') + 1
        self.save(update_fields=['usage_count'])

    def update_processing_time(self, new_time):
        """Update average processing time with a new measurement."""
        if self.usage_count == 0:
            self.avg_processing_time = new_time
        else:
            # Calculate rolling average
            total_time = self.avg_processing_time * self.usage_count
            self.avg_processing_time = (total_time + new_time) / (self.usage_count + 1)
        self.save(update_fields=['avg_processing_time'])


class DocumentEmbedding(BaseModel, ProcessingStatusModel):
    """
    Stores embeddings for document chunks.
    """
    document = models.ForeignKey(
        'documents.Document',
        on_delete=models.CASCADE,
        related_name='embeddings',
        verbose_name=_('Document')
    )

    chunk_index = models.PositiveIntegerField(
        _('Chunk index'),
        help_text=_('Index of the chunk within the document')
    )

    text_content = models.TextField(
        _('Text content'),
        help_text=_('The text content that was embedded')
    )

    embedding_model = models.ForeignKey(
        EmbeddingModel,
        on_delete=models.CASCADE,
        related_name='document_embeddings',
        verbose_name=_('Embedding Model')
    )

    embedding_vector = ArrayField(
        models.FloatField(),
        verbose_name=_('Embedding Vector'),
        help_text=_('The embedding vector for this text chunk')
    )

    # Metadata for the chunk
    chunk_metadata = models.JSONField(
        _('Chunk metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional metadata for this chunk')
    )

    # Processing metrics
    processing_time = models.FloatField(
        _('Processing time'),
        null=True,
        blank=True,
        help_text=_('Time taken to generate this embedding in milliseconds')
    )

    token_count = models.PositiveIntegerField(
        _('Token count'),
        null=True,
        blank=True,
        help_text=_('Number of tokens in the text content')
    )

    class Meta:
        verbose_name = _('Document Embedding')
        verbose_name_plural = _('Document Embeddings')
        db_table = 'embeddings_document_embedding'
        unique_together = ['document', 'chunk_index', 'embedding_model']
        indexes = [
            models.Index(fields=['document', 'embedding_model']),
            models.Index(fields=['chunk_index']),
        ]

    def __str__(self):
        return f"Embedding for {self.document.title} (chunk {self.chunk_index})"


class QueryEmbedding(BaseModel):
    """
    Stores embeddings for user queries for caching purposes.
    """
    query_text = models.TextField(
        _('Query text'),
        help_text=_('The original query text')
    )

    query_hash = models.CharField(
        _('Query hash'),
        max_length=64,
        unique=True,
        help_text=_('Hash of the query text for quick lookups')
    )

    embedding_model = models.ForeignKey(
        EmbeddingModel,
        on_delete=models.CASCADE,
        related_name='query_embeddings',
        verbose_name=_('Embedding Model')
    )

    embedding_vector = ArrayField(
        models.FloatField(),
        verbose_name=_('Embedding Vector'),
        help_text=_('The embedding vector for this query')
    )

    # Usage tracking
    hit_count = models.PositiveIntegerField(
        _('Hit count'),
        default=1,
        help_text=_('Number of times this cached embedding was used')
    )

    last_used = models.DateTimeField(
        _('Last used'),
        auto_now=True,
        help_text=_('When this cached embedding was last used')
    )

    class Meta:
        verbose_name = _('Query Embedding')
        verbose_name_plural = _('Query Embeddings')
        db_table = 'embeddings_query_embedding'
        indexes = [
            models.Index(fields=['query_hash']),
            models.Index(fields=['embedding_model', 'last_used']),
        ]

    def __str__(self):
        return f"Query embedding: {self.query_text[:50]}..."

    def increment_hit_count(self):
        """Increment the hit counter for cache usage tracking."""
        self.hit_count = models.F('hit_count') + 1
        self.save(update_fields=['hit_count', 'last_used'])


class EmbeddingJob(BaseModel, ProcessingStatusModel):
    """
    Tracks embedding generation jobs for batch processing.
    """
    JOB_TYPES = [
        ('document', _('Document Embedding')),
        ('query', _('Query Embedding')),
        ('reindex', _('Reindexing')),
    ]

    job_type = models.CharField(
        _('Job type'),
        max_length=20,
        choices=JOB_TYPES,
        help_text=_('Type of embedding job')
    )

    embedding_model = models.ForeignKey(
        EmbeddingModel,
        on_delete=models.CASCADE,
        related_name='embedding_jobs',
        verbose_name=_('Embedding Model')
    )

    # Job parameters
    parameters = models.JSONField(
        _('Parameters'),
        default=dict,
        blank=True,
        help_text=_('Job-specific parameters')
    )

    # Progress tracking
    total_items = models.PositiveIntegerField(
        _('Total items'),
        default=0,
        help_text=_('Total number of items to process')
    )

    processed_items = models.PositiveIntegerField(
        _('Processed items'),
        default=0,
        help_text=_('Number of items processed')
    )

    failed_items = models.PositiveIntegerField(
        _('Failed items'),
        default=0,
        help_text=_('Number of items that failed processing')
    )

    # Timing
    started_at = models.DateTimeField(
        _('Started at'),
        null=True,
        blank=True,
        help_text=_('When the job started processing')
    )

    completed_at = models.DateTimeField(
        _('Completed at'),
        null=True,
        blank=True,
        help_text=_('When the job finished processing')
    )

    # Results
    result_data = models.JSONField(
        _('Result data'),
        default=dict,
        blank=True,
        help_text=_('Job results and statistics')
    )

    class Meta:
        verbose_name = _('Embedding Job')
        verbose_name_plural = _('Embedding Jobs')
        db_table = 'embeddings_job'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_job_type_display()} job ({self.get_status_display()})"

    @property
    def progress_percentage(self):
        """Calculate job progress as a percentage."""
        if self.total_items == 0:
            return 0
        return (self.processed_items / self.total_items) * 100

    def mark_item_processed(self):
        """Mark one item as processed."""
        self.processed_items = models.F('processed_items') + 1
        self.save(update_fields=['processed_items'])

    def mark_item_failed(self):
        """Mark one item as failed."""
        self.failed_items = models.F('failed_items') + 1
        self.save(update_fields=['failed_items'])