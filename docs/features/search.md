# Search and Filtering System

## Overview

The La Factoria search system provides comprehensive content discovery capabilities with advanced filtering, faceted search, search suggestions, and analytics. The system is designed to scale from simple in-memory searches to full Elasticsearch deployments.

## Features

### Core Search Capabilities

1. **Full-Text Search**
   - Search across all content fields (title, overview, descriptions, key points)
   - Relevance scoring with field boosting (titles weighted higher)
   - Search result highlighting with context

2. **Advanced Filtering**
   - Content type (study guides, flashcards, FAQs, etc.)
   - Difficulty level (beginner, intermediate, advanced)
   - Target audience (elementary, high school, university, etc.)
   - Date ranges (created/modified dates)
   - Quality score ranges
   - Duration ranges
   - Tags and categories
   - Status (draft, published, archived)

3. **Faceted Search**
   - Aggregated counts for each filter option
   - Dynamic facet navigation
   - Missing value handling
   - Configurable facet sizes

4. **Search Suggestions**
   - Auto-complete from popular searches
   - Content title suggestions
   - Tag and category suggestions
   - Spelling corrections
   - Personalized suggestions based on user history

5. **Saved Searches**
   - Save frequently used search configurations
   - Private and public saved searches
   - Tag organization
   - Quick access to complex queries

6. **Search Analytics**
   - Popular searches tracking
   - Trending searches identification
   - Failed searches monitoring
   - User search history
   - Search performance metrics
   - Click-through rate tracking

## API Endpoints

### Basic Search

```
GET /api/search?q=machine+learning&page=1&size=20
```

Parameters:

- `q` - Search query (required)
- `content_type` - Filter by content type
- `page` - Page number (default: 1)
- `size` - Results per page (default: 20, max: 100)
- `sort` - Sort field (prefix with - for descending)

### Advanced Search

```
POST /api/search/advanced
```

Request body:

```json
{
  "query": "machine learning",
  "filters": {
    "content_type": ["study_guide", "flashcards"],
    "difficulty": ["intermediate", "advanced"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "quality_score_min": 0.7,
    "target_audience": ["university"]
  },
  "sort": [
    {"field": "relevance", "order": "desc"},
    {"field": "created_at", "order": "desc"}
  ],
  "facets": ["content_type", "difficulty"],
  "page": 1,
  "size": 20,
  "highlight": true
}
```

### Search Suggestions

```
GET /api/search/suggestions?q=mach&limit=10
```

Parameters:

- `q` - Partial query (required, min 1 char)
- `limit` - Maximum suggestions (default: 10, max: 50)
- `types` - Suggestion types to include (query, content, tag, correction)

### Saved Searches

Save a search:

```
POST /api/search/saved
```

Get saved searches:

```
GET /api/search/saved?include_public=true
```

Delete a saved search:

```
DELETE /api/search/saved/{search_id}
```

### Search Analytics

Popular searches:

```
GET /api/search/analytics/popular?period=7d&limit=20
```

Trending searches:

```
GET /api/search/analytics/trending?current_period=1d&comparison_period=7d
```

Failed searches:

```
GET /api/search/analytics/failed?period=7d
```

User search history:

```
GET /api/search/analytics/user/{user_id}?days=30
```

## Architecture

### Backend Support

The system supports multiple search backends through a common interface:

1. **SimpleSearchBackend** (Default)
   - Uses Firestore for storage
   - In-memory text matching and filtering
   - Suitable for smaller datasets (<10k documents)
   - No additional infrastructure required

2. **ElasticsearchBackend** (Future)
   - Full Elasticsearch integration
   - Advanced text analysis and tokenization
   - Scalable to millions of documents
   - Requires Elasticsearch cluster

### Query Builder Pattern

The system uses a flexible query builder for constructing complex searches:

```python
query = (QueryBuilder()
    .match("title", "machine learning")
    .filter_term("content_type", "study_guide")
    .filter_range("quality_score", gte=0.7)
    .sort_by("created_at", "desc")
    .facet("difficulty")
    .paginate(page=2, size=20)
    .build())
```

### Search Indexing

Content is automatically indexed when:

- New content is generated
- Existing content is updated
- Manual reindexing is triggered

Background tasks handle:

- Initial content indexing
- Incremental updates
- Index optimization
- Orphaned entry cleanup

## Performance Considerations

### Caching

- Search results cached for 60 seconds
- Suggestions cached for 5 minutes
- Analytics metrics cached for 5-10 minutes
- Popular searches precomputed periodically

### Optimization Strategies

1. **Query Optimization**
   - Limit searchable fields for better performance
   - Use filters instead of text search when possible
   - Implement query result pagination

2. **Index Optimization**
   - Regular index refreshing
   - Batch indexing for bulk operations
   - Asynchronous index updates

3. **Scaling Considerations**
   - SimpleSearch suitable for <10k documents
   - Consider Elasticsearch for >10k documents
   - Implement read replicas for high traffic
   - Use dedicated search infrastructure

## Search Relevance

### Scoring Factors

1. **Text Relevance**
   - Title matches: 2.0x boost
   - Content matches: 0.5x per occurrence
   - Exact phrase matches weighted higher

2. **Field Boosting**
   - Title: Highest weight
   - Overview: Medium weight
   - Section content: Lower weight

3. **Quality Signals**
   - Quality score consideration
   - User engagement metrics
   - Click-through rates

### Improving Search Quality

1. **Content Enrichment**
   - Add descriptive titles
   - Include comprehensive overviews
   - Use relevant tags and categories

2. **Analytics Monitoring**
   - Review failed searches regularly
   - Analyze popular search patterns
   - Optimize content based on search behavior

3. **User Feedback**
   - Track click-through rates
   - Monitor search abandonment
   - Collect explicit feedback

## Security and Privacy

### Access Control

- Users can only search their own content
- Admins can search all content
- Public saved searches visible to all
- Search history private by default

### Data Protection

- Search queries logged anonymously
- User associations stored securely
- Analytics data aggregated for privacy
- PII excluded from search indices

## Future Enhancements

1. **Advanced Features**
   - Semantic search with embeddings
   - Multi-language support
   - Voice search integration
   - Search result personalization

2. **Machine Learning**
   - Query understanding
   - Intent detection
   - Automatic query expansion
   - Learning-to-rank models

3. **Analytics Improvements**
   - Real-time search metrics
   - A/B testing framework
   - Conversion tracking
   - Advanced visualization

## Configuration

Search system configuration in `app/services/search/base.py`:

```python
SearchConfig(
    backend_type="simple",  # or "elasticsearch"
    index_name="content",
    max_results=10000,
    default_page_size=20,
    max_page_size=100,
    enable_analytics=True,
    enable_suggestions=True,
    enable_highlighting=True,
    suggestion_min_length=2,
    cache_ttl=300,
    elasticsearch_url=None  # For ES backend
)
```

## Troubleshooting

### Common Issues

1. **No Search Results**
   - Verify content is indexed
   - Check search query syntax
   - Review filter combinations
   - Ensure proper permissions

2. **Slow Search Performance**
   - Check index size and stats
   - Review query complexity
   - Monitor cache hit rates
   - Consider backend upgrade

3. **Indexing Problems**
   - Check background task logs
   - Verify Firestore connectivity
   - Review content structure
   - Manual reindex if needed

### Monitoring

Key metrics to track:

- Search response times
- Query success rates
- Index document count
- Cache hit ratios
- Popular search terms
- Failed search patterns
