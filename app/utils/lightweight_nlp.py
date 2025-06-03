"""
Lightweight NLP utilities to replace sklearn dependencies.
Pure Python implementations for TF-IDF and cosine similarity.
"""

import math
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Union


class SimpleTFIDF:
    """
    Pure Python TF-IDF implementation without sklearn dependencies.
    Provides basic text vectorization for semantic similarity.
    """

    def __init__(self, lowercase: bool = True, min_df: int = 1):
        """
        Initialize SimpleTFIDF vectorizer.

        Args:
            lowercase: Convert text to lowercase
            min_df: Minimum document frequency for a term to be included
        """
        self.lowercase = lowercase
        self.min_df = min_df
        self.vocabulary = {}
        self.idf_values = {}
        self.documents = []

    def tokenize(self, text: str) -> List[str]:
        """Simple word tokenization."""
        if self.lowercase:
            text = text.lower()
        # Basic tokenization - split on non-alphanumeric characters
        words = re.findall(r"\b\w+\b", text)
        return words

    def fit(self, documents: List[str]) -> "SimpleTFIDF":
        """
        Fit the TF-IDF model on documents.

        Args:
            documents: List of text documents

        Returns:
            Self for method chaining
        """
        self.documents = documents
        doc_count = len(documents)

        # Count document frequencies
        df_counts = defaultdict(int)
        all_terms = set()

        for doc in documents:
            terms = set(self.tokenize(doc))
            all_terms.update(terms)
            for term in terms:
                df_counts[term] += 1

        # Build vocabulary (only terms meeting min_df)
        vocab_index = 0
        for term in sorted(all_terms):
            if df_counts[term] >= self.min_df:
                self.vocabulary[term] = vocab_index
                # Calculate IDF: log(N / df) + 1 to avoid zero IDF
                # Adding 1 ensures even common terms have some weight
                self.idf_values[term] = math.log(doc_count / df_counts[term]) + 1
                vocab_index += 1

        return self

    def transform(self, documents: List[str]) -> List[List[float]]:
        """
        Transform documents to TF-IDF vectors.

        Args:
            documents: List of text documents

        Returns:
            List of dense vectors (lists)
        """
        vectors = []

        for doc in documents:
            # Calculate term frequencies
            terms = self.tokenize(doc)
            tf_counts = Counter(terms)
            doc_length = len(terms) if terms else 1

            # Create TF-IDF vector (dense)
            vector = [0.0] * len(self.vocabulary)
            for term, count in tf_counts.items():
                if term in self.vocabulary:
                    tf = count / doc_length  # Normalized term frequency
                    tfidf = tf * self.idf_values.get(term, 1.0)
                    vector[self.vocabulary[term]] = tfidf

            vectors.append(vector)

        return vectors

    def fit_transform(self, documents: List[str]) -> List[List[float]]:
        """Fit and transform in one step."""
        self.fit(documents)
        return self.transform(documents)


class LightweightSimilarity:
    """
    Pure Python similarity implementations.
    Works with both sparse and dense vectors.
    """

    @staticmethod
    def cosine_similarity(
        vec1: Union[List[float], Dict[int, float]],
        vec2: Union[List[float], Dict[int, float]],
    ) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector (list or dict)
            vec2: Second vector (list or dict)

        Returns:
            Cosine similarity score between 0 and 1
        """
        # Handle list (dense) vectors
        if isinstance(vec1, list) and isinstance(vec2, list):
            if len(vec1) != len(vec2):
                raise ValueError("Vectors must have the same length")

            dot_product = sum(v1 * v2 for v1, v2 in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(v * v for v in vec1))
            magnitude2 = math.sqrt(sum(v * v for v in vec2))

            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            return dot_product / (magnitude1 * magnitude2)

        # Handle dict (sparse) vectors
        elif isinstance(vec1, dict) and isinstance(vec2, dict):
            # Get all indices
            all_indices = set(vec1.keys()) | set(vec2.keys())

            # Calculate dot product and magnitudes
            dot_product = 0.0
            magnitude1 = 0.0
            magnitude2 = 0.0

            for idx in all_indices:
                val1 = vec1.get(idx, 0.0)
                val2 = vec2.get(idx, 0.0)

                dot_product += val1 * val2
                magnitude1 += val1 * val1
                magnitude2 += val2 * val2

            # Avoid division by zero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0

            # Calculate cosine similarity
            return dot_product / (math.sqrt(magnitude1) * math.sqrt(magnitude2))

        else:
            raise TypeError("Vectors must be both lists or both dicts")

    @staticmethod
    def jaccard_similarity(set1: Set, set2: Set) -> float:
        """
        Calculate Jaccard similarity between two sets.

        Args:
            set1: First set
            set2: Second set

        Returns:
            Jaccard similarity score between 0 and 1
        """
        if not set1 and not set2:
            return 0.0

        intersection = set1 & set2
        union = set1 | set2

        if not union:
            return 0.0

        return len(intersection) / len(union)

    @staticmethod
    def cosine_similarity_matrix(
        vectors: List[Union[List[float], Dict[int, float]]]
    ) -> List[List[float]]:
        """
        Calculate pairwise cosine similarities.

        Args:
            vectors: List of vectors

        Returns:
            2D list of similarity scores
        """
        n = len(vectors)
        similarity_matrix = [[0.0] * n for _ in range(n)]

        for i in range(n):
            for j in range(i, n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    sim = LightweightSimilarity.cosine_similarity(
                        vectors[i], vectors[j]
                    )
                    similarity_matrix[i][j] = sim
                    similarity_matrix[j][i] = sim

        return similarity_matrix


class KeywordExtractor:
    """
    Simple keyword extraction based on term frequency and importance.
    """

    # Common stopwords to filter out
    STOPWORDS = {
        "the",
        "is",
        "at",
        "which",
        "on",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "with",
        "to",
        "for",
        "of",
        "as",
        "by",
        "that",
        "this",
        "it",
        "from",
        "be",
        "are",
        "was",
        "were",
        "been",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "shall",
        "can",
        "need",
        "ought",
        "dare",
        "if",
        "then",
        "else",
        "when",
        "where",
        "why",
        "how",
        "all",
        "each",
        "every",
        "some",
        "any",
        "many",
        "much",
        "most",
        "several",
        "few",
        "both",
        "either",
        "neither",
        "only",
        "just",
        "not",
        "no",
        "nor",
        "so",
        "than",
        "too",
        "very",
        "about",
        "after",
        "before",
        "under",
        "over",
        "between",
        "through",
        "during",
        "against",
        "among",
        "into",
        "onto",
        "upon",
        "out",
        "up",
        "down",
        "off",
        "away",
        "back",
    }

    @classmethod
    def extract_keywords(
        cls, text: str, top_k: int = 10, reference_corpus: List[str] = None
    ) -> List[Tuple[str, int]]:
        """
        Extract keywords from text based on frequency.

        Args:
            text: Input text
            top_k: Number of top keywords to extract
            reference_corpus: Optional reference corpus for IDF calculation

        Returns:
            List of (keyword, frequency) tuples
        """
        if not text:
            return []

        # Tokenize and lowercase text
        words = re.findall(r"\b\w+\b", text.lower())

        # Filter out stopwords and short words
        words = [w for w in words if w not in cls.STOPWORDS and len(w) > 2]

        # Count word frequencies
        word_freq = Counter(words)

        # Return top keywords by frequency
        return word_freq.most_common(top_k)

    @classmethod
    def get_text_keywords(cls, text: str, top_k: int = 10) -> List[str]:
        """
        Get just the keywords without frequencies.

        Args:
            text: Input text
            top_k: Number of keywords to extract

        Returns:
            List of keywords
        """
        keyword_tuples = cls.extract_keywords(text, top_k)
        return [word for word, _ in keyword_tuples]


class TextSimilarityChecker:
    """High-level text similarity checking using lightweight methods."""

    @staticmethod
    def check_similarity(
        text1: str, text2: str, threshold: float = 0.5
    ) -> Tuple[bool, float]:
        """
        Check if two texts are similar based on TF-IDF cosine similarity.

        Args:
            text1: First text to compare
            text2: Second text to compare
            threshold: Similarity threshold (0-1)

        Returns:
            Tuple of (is_similar, similarity_score)
        """
        if not text1 or not text2:
            return False, 0.0

        # Handle identical texts
        if text1.strip() == text2.strip():
            return True, 1.0

        # Use TF-IDF to get vector representations
        tfidf = SimpleTFIDF()
        # Fit on both texts to ensure vocabulary includes all terms
        vectors = tfidf.fit_transform([text1, text2])

        if len(vectors) < 2:
            return False, 0.0

        # Calculate cosine similarity
        similarity = LightweightSimilarity.cosine_similarity(vectors[0], vectors[1])

        return similarity >= threshold, similarity

    @staticmethod
    def check_keyword_overlap(
        text1: str, text2: str, top_k: int = 10, threshold: float = 0.3
    ) -> Tuple[bool, float]:
        """
        Check keyword overlap between two texts.

        Args:
            text1: First text
            text2: Second text
            top_k: Number of top keywords to extract
            threshold: Overlap threshold

        Returns:
            Tuple of (has_significant_overlap, overlap_score)
        """
        # Extract keywords from both texts
        keywords1 = set(KeywordExtractor.get_text_keywords(text1, top_k))
        keywords2 = set(KeywordExtractor.get_text_keywords(text2, top_k))

        if not keywords1 or not keywords2:
            return False, 0.0

        # Calculate Jaccard similarity of keywords
        overlap_score = LightweightSimilarity.jaccard_similarity(keywords1, keywords2)

        return overlap_score >= threshold, overlap_score


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Simple function to calculate similarity between two texts.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score between 0 and 1
    """
    # Handle empty or identical texts
    if not text1 or not text2:
        return 0.0
    if text1.strip() == text2.strip():
        return 1.0

    # Use TF-IDF and cosine similarity
    tfidf = SimpleTFIDF()
    vectors = tfidf.fit_transform([text1, text2])

    if len(vectors) < 2:
        return 0.0

    similarity = LightweightSimilarity.cosine_similarity(vectors[0], vectors[1])
    return similarity


def extract_key_terms(texts: List[str], top_n: int = 20) -> List[str]:
    """
    Extract key terms from a collection of texts.

    Args:
        texts: List of text documents
        top_n: Number of top terms to extract

    Returns:
        List of key terms
    """
    # Combine all texts
    combined_text = " ".join(texts)

    # Extract keywords using the class method
    return KeywordExtractor.get_text_keywords(combined_text, top_n)
