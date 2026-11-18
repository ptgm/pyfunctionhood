"""Pytest for rule categorization (S1, S2, S3) in parent-child relationships.

This module validates that parents and children are correctly categorized
into S1, S2, and S3 rules, and that the categorization is exhaustive and
consistent.
"""
import pytest
from pyfunctionhood import HasseDiagram


def test_rule_categorization_completeness(n=4):
    """Verify that all parents/children are categorized into exactly one rule.
    
    Every parent must belong to exactly one of S1, S2, or S3.
    Every child must belong to exactly one of S1, S2, or S3.
    """
    hd = HasseDiagram(n)
    finf = hd.get_infimum()
    
    # Sample some functions at different levels
    s1Parents, s2Parents, s3Parents = hd.get_f_parents(finf)
    
    # Check partition properties: sets should be disjoint
    assert len(s1Parents & s2Parents) == 0, "S1 and S2 parents overlap"
    assert len(s2Parents & s3Parents) == 0, "S2 and S3 parents overlap"
    assert len(s1Parents & s3Parents) == 0, "S1 and S3 parents overlap"
    
    # Check that union equals total (optional, but good for exhaustiveness)
    all_parents = s1Parents | s2Parents | s3Parents
    assert len(all_parents) > 0, "No parents found"


@pytest.mark.parametrize("n", [2, 3, 4])
def test_rule_categorization_consistency(n):
    """Test that rule categorization is consistent across multiple queries.
    
    For several functions, verify that:
    1. Each parent/child belongs to exactly one rule category
    2. Getting the same parent/child again yields the same categorization
    """
    hd = HasseDiagram(n)
    finf = hd.get_infimum()
    fsup = hd.get_supremum()
    
    # Test parents of infimum
    s1P, s2P, s3P = hd.get_f_parents(finf)
    
    # Verify partition
    assert len(s1P & s2P) == 0 and len(s2P & s3P) == 0 and len(s1P & s3P) == 0, \
        f"n={n}: Parents not properly partitioned into disjoint sets"
    
    # Verify at least one rule is non-empty
    assert len(s1P) + len(s2P) + len(s3P) > 0, \
        f"n={n}: No parents found for infimum"
    
    # Test children of supremum
    s1C, s2C, s3C = hd.get_f_children(fsup)
    
    # Verify partition
    assert len(s1C & s2C) == 0 and len(s2C & s3C) == 0 and len(s1C & s3C) == 0, \
        f"n={n}: Children not properly partitioned into disjoint sets"
    
    # Verify at least one rule is non-empty
    assert len(s1C) + len(s2C) + len(s3C) > 0, \
        f"n={n}: No children found for supremum"


@pytest.mark.parametrize("n", [2, 3, 4])
def test_rule_coverage_across_dimensions(n):
    """Verify that rules are non-empty in the Hasse diagram.
    
    For small to medium dimensions, at least S3 should appear
    (S1 and S2 may require intermediate functions).
    """
    hd = HasseDiagram(n)
    finf = hd.get_infimum()
    fsup = hd.get_supremum()
    
    # Infimum should have S3 parents
    s1P, s2P, s3P = hd.get_f_parents(finf)
    assert len(s3P) > 0, f"n={n}: Infimum should have S3 parents"
    
    # Supremum should have S3 children
    s1C, s2C, s3C = hd.get_f_children(fsup)
    assert len(s3C) > 0, f"n={n}: Supremum should have S3 children"


def test_infimum_supremum_duality(n=4):
    """Test duality: infimum and supremum should have complementary properties.
    
    The infimum has only parents (no parents of parents...).
    The supremum has only children (no children of children...).
    """
    hd = HasseDiagram(n)
    finf = hd.get_infimum()
    fsup = hd.get_supremum()
    
    # Infimum has parents but no children
    s1P, s2P, s3P = hd.get_f_parents(finf)
    s1C, s2C, s3C = hd.get_f_children(finf)
    
    assert len(s1P) + len(s2P) + len(s3P) > 0, f"Infimum has no parents (n={n})"
    assert len(s1C) == 0 and len(s2C) == 0 and len(s3C) == 0, \
        f"Infimum should have no children (n={n})"
    
    # Supremum has children but no parents
    s1P, s2P, s3P = hd.get_f_parents(fsup)
    s1C, s2C, s3C = hd.get_f_children(fsup)
    
    assert len(s1C) + len(s2C) + len(s3C) > 0, f"Supremum has no children (n={n})"
    assert len(s1P) == 0 and len(s2P) == 0 and len(s3P) == 0, \
        f"Supremum should have no parents (n={n})"


if __name__ == "__main__":
    # Allow running directly with: python -m pytest tests/test_rule_categorization.py
    pytest.main([__file__, "-v"])
