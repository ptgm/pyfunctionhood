"""Pytest for consistency of parent-child relationships in Hasse diagrams.

This module contains tests that verify parent-child relationships are
consistent by performing random walks on the Hasse diagram, both from
infimum to supremum and from supremum to infimum.
"""
import pytest
import random
from pyfunctionhood import HasseDiagram


def random_walk_infimum_to_supremum(hd, num_walks=10):
    """Perform random walks from infimum to supremum.
    
    For each walk, verify that at every step, the previous function
    is indeed a child of the randomly chosen parent.
    
    Args:
        hd: HasseDiagram instance
        num_walks: number of independent random walks to perform
        
    Returns:
        Tuple of (failed, total_steps) where failed is True if any walk failed
    """
    finf = hd.get_infimum()
    fsup = hd.get_supremum()
    
    for walk in range(num_walks):
        f = finf
        while f != fsup:
            s1Parents, s2Parents, s3Parents = hd.get_f_parents(f)
            lParents = list(s1Parents) + list(s2Parents) + list(s3Parents)
            
            # Randomly choose a parent
            parent = lParents[random.randint(0, len(lParents) - 1)]
            
            # Verify that f is indeed a child of parent
            s1Children, s2Children, s3Children = hd.get_f_children(parent)
            if not (f in s1Children or f in s2Children or f in s3Children):
                return True, walk, f, parent  # Failed
            
            f = parent
    
    return False, num_walks, None, None  # Success


def random_walk_supremum_to_infimum(hd, num_walks=10):
    """Perform random walks from supremum to infimum.
    
    For each walk, verify that at every step, the previous function
    is indeed a parent of the randomly chosen child.
    
    Args:
        hd: HasseDiagram instance
        num_walks: number of independent random walks to perform
        
    Returns:
        Tuple of (failed, total_steps) where failed is True if any walk failed
    """
    finf = hd.get_infimum()
    fsup = hd.get_supremum()
    
    for walk in range(num_walks):
        f = fsup
        while f != finf:
            s1Children, s2Children, s3Children = hd.get_f_children(f)
            lChildren = list(s1Children) + list(s2Children) + list(s3Children)
            
            # Randomly choose a child
            child = lChildren[random.randint(0, len(lChildren) - 1)]
            
            # Verify that f is indeed a parent of child
            s1Parents, s2Parents, s3Parents = hd.get_f_parents(child)
            if not (f in s1Parents or f in s2Parents or f in s3Parents):
                return True, walk, f, child  # Failed
            
            f = child
    
    return False, num_walks, None, None  # Success


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_hasse_diagram_rules_infimum_to_supremum(n):
    """Test parent-child consistency with random walks from infimum to supremum.
    
    Performs 10 independent random walks from the infimum (0) to supremum (1)
    on the Hasse diagram, verifying that at each step, the previous function
    is indeed a child of the randomly chosen parent.
    """
    hd = HasseDiagram(n)
    failed, walk, f, parent = random_walk_infimum_to_supremum(hd, num_walks=10)
    assert not failed, f"Walk failed at walk {walk} for n={n}: f={f} is not a child of parent={parent}"


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6])
def test_hasse_diagram_rules_supremum_to_infimum(n):
    """Test parent-child consistency with random walks from supremum to infimum.
    
    Performs 10 independent random walks from the supremum (1) to infimum (0)
    on the Hasse diagram, verifying that at each step, the previous function
    is indeed a parent of the randomly chosen child.
    """
    hd = HasseDiagram(n)
    failed, walk, f, child = random_walk_supremum_to_infimum(hd, num_walks=10)
    assert not failed, f"Walk failed at walk {walk} for n={n}: f={f} is not a parent of child={child}"


if __name__ == "__main__":
    # Allow running directly with: python -m pytest tests/test_check_rules.py
    pytest.main([__file__, "-v"])
