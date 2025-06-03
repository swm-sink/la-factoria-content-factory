"""Unit tests for lightweight NLP utilities."""

import pytest

from app.utils.lightweight_nlp import (
    KeywordExtractor,
    LightweightSimilarity,
    SimpleTFIDF,
    TextSimilarityChecker,
)


class TestSimpleTFIDF:
    """Test SimpleTFIDF implementation."""

    def test_init(self):
        """Test TF-IDF initialization."""
        tfidf = SimpleTFIDF()
        assert tfidf.vocabulary == {}
        assert tfidf.idf_values == {}
        assert tfidf.documents == []

    def test_fit_single_document(self):
        """Test fitting with single document."""
        tfidf = SimpleTFIDF()
        documents = ["machine learning is great"]
        tfidf.fit(documents)

        assert len(tfidf.documents) == 1
        assert "machine" in tfidf.vocabulary
        assert "learning" in tfidf.vocabulary
        assert len(tfidf.idf_values) > 0

    def test_fit_multiple_documents(self):
        """Test fitting with multiple documents."""
        tfidf = SimpleTFIDF()
        documents = [
            "machine learning is great",
            "deep learning is better than machine learning",
            "artificial intelligence includes machine learning",
        ]
        tfidf.fit(documents)

        assert len(tfidf.documents) == 3
        assert "machine" in tfidf.vocabulary
        assert "learning" in tfidf.vocabulary
        assert "deep" in tfidf.vocabulary

        # Check IDF values - words appearing in all docs should have lower IDF
        assert tfidf.idf_values.get("machine", 0) < tfidf.idf_values.get("deep", 0)

    def test_transform_single_document(self):
        """Test transforming single document."""
        tfidf = SimpleTFIDF()
        documents = ["machine learning is great", "deep learning is amazing"]
        tfidf.fit(documents)

        vectors = tfidf.transform(["machine learning"])
        assert len(vectors) == 1
        assert len(vectors[0]) == len(tfidf.vocabulary)

        # Machine and learning should have non-zero values
        machine_idx = tfidf.vocabulary.get("machine")
        learning_idx = tfidf.vocabulary.get("learning")
        assert vectors[0][machine_idx] > 0
        assert vectors[0][learning_idx] > 0

    def test_fit_transform(self):
        """Test fit_transform convenience method."""
        tfidf = SimpleTFIDF()
        documents = ["machine learning", "deep learning"]
        vectors = tfidf.fit_transform(documents)

        assert len(vectors) == 2
        assert len(vectors[0]) == len(tfidf.vocabulary)
        assert len(vectors[1]) == len(tfidf.vocabulary)


class TestLightweightSimilarity:
    """Test LightweightSimilarity implementation."""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity for identical vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0, 3.0]

        similarity = LightweightSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.0001  # Should be 1.0

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors."""
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]

        similarity = LightweightSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity) < 0.0001  # Should be 0.0

    def test_cosine_similarity_proportional(self):
        """Test cosine similarity for proportional vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [2.0, 4.0, 6.0]  # 2x vec1

        similarity = LightweightSimilarity.cosine_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 0.0001  # Should be 1.0

    def test_cosine_similarity_zero_vectors(self):
        """Test cosine similarity with zero vectors."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]

        similarity = LightweightSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_jaccard_similarity_identical(self):
        """Test Jaccard similarity for identical sets."""
        set1 = {"machine", "learning", "ai"}
        set2 = {"machine", "learning", "ai"}

        similarity = LightweightSimilarity.jaccard_similarity(set1, set2)
        assert similarity == 1.0

    def test_jaccard_similarity_disjoint(self):
        """Test Jaccard similarity for disjoint sets."""
        set1 = {"machine", "learning"}
        set2 = {"deep", "neural"}

        similarity = LightweightSimilarity.jaccard_similarity(set1, set2)
        assert similarity == 0.0

    def test_jaccard_similarity_partial_overlap(self):
        """Test Jaccard similarity for partial overlap."""
        set1 = {"machine", "learning", "ai"}
        set2 = {"machine", "learning", "deep"}

        similarity = LightweightSimilarity.jaccard_similarity(set1, set2)
        # 2 common / 4 total = 0.5
        assert abs(similarity - 0.5) < 0.0001

    def test_jaccard_similarity_empty_sets(self):
        """Test Jaccard similarity with empty sets."""
        set1 = set()
        set2 = {"machine", "learning"}

        similarity = LightweightSimilarity.jaccard_similarity(set1, set2)
        assert similarity == 0.0

        # Both empty
        similarity = LightweightSimilarity.jaccard_similarity(set(), set())
        assert similarity == 0.0


class TestKeywordExtractor:
    """Test KeywordExtractor implementation."""

    def test_extract_keywords_simple(self):
        """Test keyword extraction from simple text."""
        text = "Machine learning is great. Machine learning is powerful."
        keywords = KeywordExtractor.extract_keywords(text, top_k=3)

        assert len(keywords) <= 3
        assert isinstance(keywords, list)

        # Machine and learning should be top keywords (appear twice)
        keyword_words = [kw[0] for kw in keywords]
        assert "machine" in keyword_words
        assert "learning" in keyword_words

    def test_extract_keywords_with_stopwords(self):
        """Test keyword extraction filters common words."""
        text = "The machine learning is the best approach for the problem"
        keywords = KeywordExtractor.extract_keywords(text, top_k=5)

        # Common words like 'the', 'is', 'for' should be filtered
        keyword_words = [kw[0] for kw in keywords]
        assert "the" not in keyword_words
        assert "is" not in keyword_words
        assert "for" not in keyword_words

        # Content words should remain
        assert "machine" in keyword_words
        assert "learning" in keyword_words

    def test_extract_keywords_frequency_ordering(self):
        """Test keywords are ordered by frequency."""
        text = "Deep learning deep learning deep neural networks learning"
        keywords = KeywordExtractor.extract_keywords(text, top_k=3)

        # Check frequencies are in descending order
        frequencies = [kw[1] for kw in keywords]
        assert frequencies == sorted(frequencies, reverse=True)

        # 'deep' and 'learning' should be most frequent
        assert keywords[0][0] in ["deep", "learning"]
        assert keywords[0][1] == 3  # Both appear 3 times

    def test_extract_keywords_empty_text(self):
        """Test keyword extraction from empty text."""
        keywords = KeywordExtractor.extract_keywords("", top_k=5)
        assert keywords == []

    def test_extract_keywords_top_k_limit(self):
        """Test top_k parameter limits results."""
        text = "one two three four five six seven eight nine ten"
        keywords = KeywordExtractor.extract_keywords(text, top_k=3)

        assert len(keywords) == 3

    def test_get_text_keywords_convenience(self):
        """Test convenience method returns just words."""
        text = "Machine learning and deep learning are important"
        keywords = KeywordExtractor.get_text_keywords(text, top_k=3)

        assert isinstance(keywords, list)
        assert all(isinstance(kw, str) for kw in keywords)
        assert len(keywords) <= 3


class TestTextSimilarityChecker:
    """Test TextSimilarityChecker implementation."""

    def test_check_similarity_identical(self):
        """Test similarity check for identical texts."""
        text1 = "Machine learning is a subset of artificial intelligence"
        text2 = "Machine learning is a subset of artificial intelligence"

        is_similar, score = TextSimilarityChecker.check_similarity(text1, text2)
        assert is_similar is True
        assert score > 0.9

    def test_check_similarity_different(self):
        """Test similarity check for different texts."""
        text1 = "Machine learning is great"
        text2 = "The weather is nice today"

        is_similar, score = TextSimilarityChecker.check_similarity(text1, text2)
        assert is_similar is False
        assert score < 0.3

    def test_check_similarity_partial(self):
        """Test similarity check for partially similar texts."""
        text1 = "Machine learning uses neural networks"
        text2 = "Deep learning uses neural networks extensively"

        is_similar, score = TextSimilarityChecker.check_similarity(text1, text2)
        # Should have moderate similarity due to shared terms
        assert 0.3 < score < 0.8

    def test_check_similarity_empty_texts(self):
        """Test similarity check with empty texts."""
        is_similar, score = TextSimilarityChecker.check_similarity("", "")
        assert is_similar is False
        assert score == 0.0

        is_similar, score = TextSimilarityChecker.check_similarity("text", "")
        assert is_similar is False
        assert score == 0.0

    def test_check_similarity_custom_threshold(self):
        """Test similarity check with custom threshold."""
        text1 = "Machine learning is powerful"
        text2 = "Machine learning is amazing"

        # With low threshold
        is_similar, score = TextSimilarityChecker.check_similarity(
            text1, text2, threshold=0.3
        )
        assert is_similar is True

        # With high threshold
        is_similar, score = TextSimilarityChecker.check_similarity(
            text1, text2, threshold=0.9
        )
        assert is_similar is False

    def test_check_keyword_overlap(self):
        """Test keyword overlap checking."""
        text1 = "Machine learning and artificial intelligence are related fields"
        text2 = "AI and machine learning revolutionize technology"

        # Use a lower threshold since overlap is ~0.25
        has_overlap, score = TextSimilarityChecker.check_keyword_overlap(
            text1, text2, threshold=0.2
        )
        assert has_overlap is True
        assert score > 0.2  # Some overlap expected

        # Check with non-overlapping texts
        text3 = "The weather is nice today"
        has_overlap, score = TextSimilarityChecker.check_keyword_overlap(text1, text3)
        assert score < 0.3  # Low overlap


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
