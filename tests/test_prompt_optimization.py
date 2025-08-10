"""
Test suite for validating optimized prompts following Claude best practices.
Tests ensure prompts use XML tags, chain-of-thought, proper role setting, and other Anthropic guidelines.
"""

import pytest
import re
from pathlib import Path
from typing import Dict, List, Optional


class TestPromptOptimization:
    """Test suite for validating Claude-optimized prompts"""
    
    @pytest.fixture
    def prompt_dir(self):
        """Get the prompts directory"""
        return Path(__file__).parent.parent / "prompts"
    
    @pytest.fixture
    def optimized_prompts(self, prompt_dir):
        """Load optimized prompts with _v2 suffix"""
        prompts = {}
        for prompt_file in prompt_dir.glob("*_v2.md"):
            prompts[prompt_file.stem] = prompt_file.read_text()
        return prompts
    
    def test_prompts_use_xml_tags(self, optimized_prompts):
        """Test that optimized prompts use XML tags for structure"""
        required_tags = ['<role>', '<context>', '<instructions>', '<output_format>']
        
        for prompt_name, content in optimized_prompts.items():
            # Check for presence of XML tags
            for tag in required_tags:
                assert tag in content, f"{prompt_name} missing required XML tag: {tag}"
                # Check for closing tags
                closing_tag = tag.replace('<', '</')
                assert closing_tag in content, f"{prompt_name} missing closing tag: {closing_tag}"
    
    def test_prompts_have_thinking_steps(self, optimized_prompts):
        """Test that prompts include chain-of-thought prompting"""
        thinking_patterns = [
            r'<thinking>',
            r'step.?by.?step',
            r'think through',
            r'reason about'
        ]
        
        for prompt_name, content in optimized_prompts.items():
            has_thinking = any(
                re.search(pattern, content, re.IGNORECASE) 
                for pattern in thinking_patterns
            )
            assert has_thinking, f"{prompt_name} lacks chain-of-thought prompting"
    
    def test_prompts_have_clear_roles(self, optimized_prompts):
        """Test that prompts define clear expert roles"""
        for prompt_name, content in optimized_prompts.items():
            assert '<role>' in content, f"{prompt_name} missing role definition"
            
            # Extract role content
            role_match = re.search(r'<role>(.*?)</role>', content, re.DOTALL)
            assert role_match, f"{prompt_name} has malformed role tags"
            
            role_content = role_match.group(1)
            # Check for expert/specialist keywords
            expert_keywords = ['expert', 'specialist', 'professional', 'experienced']
            has_expertise = any(keyword in role_content.lower() for keyword in expert_keywords)
            assert has_expertise, f"{prompt_name} role doesn't establish expertise"
    
    def test_prompts_use_examples_properly(self, optimized_prompts):
        """Test that prompts use <example> tags for demonstrations"""
        for prompt_name, content in optimized_prompts.items():
            if '<example>' in content:
                # Verify proper example structure
                assert '</example>' in content, f"{prompt_name} has unclosed example tag"
                
                # Examples should be within appropriate sections
                example_count = content.count('<example>')
                closing_count = content.count('</example>')
                assert example_count == closing_count, f"{prompt_name} has mismatched example tags"
    
    def test_prompts_avoid_negative_instructions(self, optimized_prompts):
        """Test that prompts minimize negative instructions (don't do X)"""
        negative_patterns = [
            r"don't\s+",
            r"do\s+not\s+",
            r"never\s+",
            r"avoid\s+",
            r"must\s+not\s+"
        ]
        
        for prompt_name, content in optimized_prompts.items():
            negative_count = 0
            for pattern in negative_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                negative_count += len(matches)
            
            # Allow some negative instructions but not excessive
            assert negative_count < 5, f"{prompt_name} has too many negative instructions ({negative_count})"
    
    def test_prompts_have_clear_structure(self, optimized_prompts):
        """Test that prompts have clear hierarchical structure"""
        structure_tags = [
            '<role>',
            '<context>',
            '<instructions>',
            '<output_format>'
        ]
        
        for prompt_name, content in optimized_prompts.items():
            # Check order of tags
            positions = {}
            for tag in structure_tags:
                pos = content.find(tag)
                if pos != -1:
                    positions[tag] = pos
            
            # Verify logical order (role -> context -> instructions -> output)
            if len(positions) > 1:
                sorted_tags = sorted(positions.items(), key=lambda x: x[1])
                tag_order = [tag for tag, _ in sorted_tags]
                
                # Role should come before instructions
                if '<role>' in tag_order and '<instructions>' in tag_order:
                    role_idx = tag_order.index('<role>')
                    inst_idx = tag_order.index('<instructions>')
                    assert role_idx < inst_idx, f"{prompt_name} has illogical tag order"
    
    def test_prompts_use_cdata_for_complex_content(self, optimized_prompts):
        """Test that prompts use CDATA sections for complex content when needed"""
        for prompt_name, content in optimized_prompts.items():
            # If prompt contains JSON examples or code, should use CDATA
            if '```json' in content or '```python' in content:
                assert '<![CDATA[' in content, f"{prompt_name} should use CDATA for code/JSON blocks"
                assert ']]>' in content, f"{prompt_name} has unclosed CDATA section"
    
    def test_prompts_have_quality_criteria(self, optimized_prompts):
        """Test that prompts include success criteria"""
        for prompt_name, content in optimized_prompts.items():
            quality_indicators = [
                '<success_criteria>',
                '<quality_checks>',
                '<validation>',
                'high-quality',
                'ensure quality'
            ]
            
            has_quality = any(
                indicator in content.lower() 
                for indicator in quality_indicators
            )
            assert has_quality, f"{prompt_name} lacks quality criteria definition"
    
    def test_prompts_are_concise(self, optimized_prompts):
        """Test that prompts are concise and not overly verbose"""
        for prompt_name, content in optimized_prompts.items():
            # Check total length (should be reasonable)
            assert len(content) < 10000, f"{prompt_name} is too verbose ({len(content)} chars)"
            
            # Check for redundant instructions
            lines = content.split('\n')
            unique_lines = set(line.strip() for line in lines if line.strip())
            redundancy_ratio = 1 - (len(unique_lines) / len(lines)) if lines else 0
            assert redundancy_ratio < 0.2, f"{prompt_name} has high redundancy"
    
    def test_prompts_support_versioning(self, prompt_dir):
        """Test that prompt versioning system is in place"""
        # Check for version 2 prompts
        v2_prompts = list(prompt_dir.glob("*_v2.md"))
        assert len(v2_prompts) > 0, "No version 2 prompts found"
        
        # Each v2 should have a corresponding original
        for v2_prompt in v2_prompts:
            original_name = v2_prompt.stem.replace('_v2', '') + '.md'
            original_path = prompt_dir / original_name
            assert original_path.exists(), f"Missing original for {v2_prompt.name}"
    
    def test_prompt_loader_supports_versions(self):
        """Test that prompt loader can handle versioned prompts"""
        from src.services.prompt_loader import PromptLoader
        
        # This will fail initially, driving the implementation
        loader = PromptLoader()
        
        # Should be able to load specific versions
        assert hasattr(loader, 'load_prompt_version'), "PromptLoader lacks version support"
        
        # Should track available versions
        assert hasattr(loader, 'get_prompt_versions'), "PromptLoader can't list versions"
    
    def test_prompts_have_metadata(self, optimized_prompts):
        """Test that prompts include metadata for tracking"""
        metadata_patterns = [
            r'<!--\s*version:',
            r'<!--\s*updated:',
            r'<!--\s*author:',
            r'<!--\s*description:'
        ]
        
        for prompt_name, content in optimized_prompts.items():
            has_metadata = any(
                re.search(pattern, content, re.IGNORECASE)
                for pattern in metadata_patterns
            )
            assert has_metadata, f"{prompt_name} lacks metadata comments"


class TestPromptPerformance:
    """Test prompt performance and effectiveness"""
    
    @pytest.mark.slow
    async def test_optimized_prompts_generate_valid_json(self):
        """Test that optimized prompts consistently generate valid JSON"""
        # This would test actual AI generation with the new prompts
        # Marked as slow since it requires AI API calls
        pass
    
    @pytest.mark.slow  
    async def test_optimized_prompts_improve_quality_scores(self):
        """Test that optimized prompts produce higher quality content"""
        # Compare quality scores between v1 and v2 prompts
        pass
    
    def test_prompts_reduce_token_usage(self):
        """Test that optimized prompts are more token-efficient"""
        try:
            import tiktoken
        except ImportError:
            pytest.skip("tiktoken not installed")
            
        # Get the prompts directory
        prompt_dir = Path(__file__).parent.parent / "prompts"
        optimized_prompts = {}
        for prompt_file in prompt_dir.glob("*_v2.md"):
            optimized_prompts[prompt_file.stem] = prompt_file.read_text()
            
        if not optimized_prompts:
            pytest.skip("No optimized prompts found")
        
        # Get tokenizer for Claude (approximate with cl100k_base)
        enc = tiktoken.get_encoding("cl100k_base")
        
        for prompt_name, content in optimized_prompts.items():
            tokens = len(enc.encode(content))
            # Optimized prompts should be reasonably sized
            assert tokens < 2000, f"{prompt_name} uses too many tokens ({tokens})"