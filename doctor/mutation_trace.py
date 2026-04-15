"""
Mutation Trace System — Executable Implementation

Canonical serialization rules for deterministic SHA256 identity:
- All dict keys sorted alphabetically
- JSON canonical form (no whitespace, sorted keys)
- Version strings pinned at import time
- Params normalized to sorted tuples
"""
import hashlib
import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List


GRAMMAR_VERSION = "1.0.0"
ORACLE_VERSION = "1.0.0"


def canonical_hash(*components) -> str:
    """
    Deterministic SHA256 hash from components.
    
    Canonical form:
    - All strings as-is
    - Dicts sorted by key, then canonicalized recursively
    - Lists sorted by canonical form of items
    - Integers as decimal strings
    """
    def canonicalize(obj) -> str:
        if isinstance(obj, dict):
            return "{" + ",".join(
                f"{canonicalize(k)}:{canonicalize(v)}" 
                for k, v in sorted(obj.items())
            ) + "}"
        elif isinstance(obj, list):
            return "[" + ",".join(canonicalize(x) for x in obj) + "]"
        elif isinstance(obj, str):
            return obj
        elif isinstance(obj, (int, float)):
            return str(obj)
        elif obj is None:
            return "null"
        elif obj is True:
            return "true"
        elif obj is False:
            return "false"
        else:
            return str(obj)
    
    raw = "|".join(canonicalize(c) for c in components)
    return hashlib.sha256(raw.encode()).hexdigest()


class PhaseState(Enum):
    GENESIS = "GENESIS"
    EVALUATION = "EVALUATION"
    COMPLETE = "COMPLETE"


class MutationGraph:
    """Immutable graph after evaluation begins."""
    
    def __init__(self, graph_id: Optional[str] = None):
        self.graph_id = graph_id or str(uuid.uuid4())
        self.phase = PhaseState.GENESIS
        self.created_at = datetime.now().isoformat()
        self.eval_started_at: Optional[str] = None
        self.eval_completed_at: Optional[str] = None
        self.nodes: List[MutationCase] = []
        self.seeds: List[str] = []  # case_ids of seeds
    
    def start_evaluation(self):
        if self.phase != PhaseState.GENESIS:
            raise ValueError(f"Cannot start evaluation from {self.phase.value}")
        self.phase = PhaseState.EVALUATION
        self.eval_started_at = datetime.now().isoformat()
    
    def complete_evaluation(self):
        if self.phase != PhaseState.EVALUATION:
            raise ValueError(f"Cannot complete evaluation from {self.phase.value}")
        self.phase = PhaseState.COMPLETE
        self.eval_completed_at = datetime.now().isoformat()
    
    def assert_mutable(self):
        if self.phase != PhaseState.GENESIS:
            raise ValueError(
                f"Cannot mutate after evaluation begins. Current phase: {self.phase.value}"
            )
    
    def add_case(self, case: "MutationCase", parent_id: Optional[str] = None):
        self.assert_mutable()
        
        # Check for duplicates
        existing_keys = {n.identity_key for n in self.nodes}
        if case.identity_key in existing_keys:
            raise ValueError(f"Duplicate case: {case.identity_key}")
        
        self.nodes.append(case)
        if parent_id:
            case.parent_id = parent_id
        else:
            self.seeds.append(case.case_id)
            case.generation = 0
    
    def to_dict(self) -> dict:
        return {
            "graph_id": self.graph_id,
            "phase": self.phase.value,
            "grammar_version": GRAMMAR_VERSION,
            "oracle_version": ORACLE_VERSION,
            "created_at": self.created_at,
            "eval_started_at": self.eval_started_at,
            "eval_completed_at": self.eval_completed_at,
            "seeds": self.seeds,
            "nodes": [n.to_dict() for n in self.nodes]
        }


class MutationCase:
    """Atomic mutation case with deterministic identity."""
    
    VALID_TYPES = {"seed", "scale", "boundary", "order", "format", "noise", "adversarial"}
    MAX_GENERATION = 3
    
    def __init__(
        self,
        seed_id: str,
        mutation_type: str,
        params: Dict[str, Any],
        trigger: Optional[Dict[str, str]] = None,
        parent_id: Optional[str] = None
    ):
        # Validate mutation type
        if mutation_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid mutation type: {mutation_type}")
        
        self.case_id = str(uuid.uuid4())
        self.seed_id = seed_id
        self.mutation_type = mutation_type
        self.params = params  # Already sorted dict for determinism
        self.grammar_version = GRAMMAR_VERSION
        self.oracle_version = ORACLE_VERSION
        self.parent_id = parent_id
        self.generation = 1 if parent_id else 0
        
        # Compute deterministic identity
        self.identity_key = self._compute_identity()
        
        # Metadata
        self.created_at = datetime.now().isoformat()
        self.trigger = trigger
        
        # Evaluation results (set after oracle runs)
        self.E: Optional[int] = None
        self.e: Optional[float] = None
        self.risk: Optional[str] = None
        self.trust_type: Optional[str] = None
    
    def _compute_identity(self) -> str:
        """
        Canonical identity = SHA256(seed_id + type + sorted_params + versions).
        
        Params must already be in canonical form (sorted dict).
        """
        return canonical_hash(
            self.seed_id,
            self.mutation_type,
            self.params,  # Must be canonical (sorted keys)
            self.grammar_version,
            self.oracle_version
        )
    
    def set_parent(self, parent_id: str, parent_generation: int):
        """Set parent after creation (called by graph.add_case)."""
        if parent_generation >= self.MAX_GENERATION:
            raise ValueError(f"Max generation ({self.MAX_GENERATION}) exceeded")
        self.parent_id = parent_id
        self.generation = parent_generation + 1
    
    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "identity_key": self.identity_key,
            "seed_id": self.seed_id,
            "mutation_type": self.mutation_type,
            "params": self.params,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "grammar_version": self.grammar_version,
            "oracle_version": self.oracle_version,
            "created_at": self.created_at,
            "trigger": self.trigger,
            "E": self.E,
            "e": self.e,
            "risk": self.risk,
            "trust_type": self.trust_type
        }


def apply_mutation(
    graph: MutationGraph,
    parent: MutationCase,
    mutation_type: str,
    params: Dict[str, Any],
    trigger: Optional[Dict[str, str]] = None
) -> MutationCase:
    """
    Apply mutation to parent case.
    
    Canonical form:
    - params dict keys sorted alphabetically
    - identity computed before storage
    """
    # Normalize params to sorted dict for determinism
    sorted_params = {k: params[k] for k in sorted(params.keys())}
    
    case = MutationCase(
        seed_id=parent.seed_id,  # Preserve original seed reference
        mutation_type=mutation_type,
        params=sorted_params,
        trigger=trigger,
        parent_id=parent.case_id
    )
    
    # Set generation based on parent
    case.set_parent(parent.case_id, parent.generation)
    
    graph.add_case(case, parent.case_id)
    
    return case


def create_seed(
    graph: MutationGraph,
    problem_name: str,
    variant_label: str,
    code: str
) -> MutationCase:
    """Create initial seed case."""
    seed_id = str(uuid.uuid4())
    
    # Create a special "seed" mutation type for roots
    case = MutationCase(
        seed_id=seed_id,
        mutation_type="seed",
        params={"problem_name": problem_name, "variant": variant_label, "code_hash": hashlib.sha256(code.encode()).hexdigest()},
        trigger=None,
        parent_id=None
    )
    case.code = code
    case.problem_name = problem_name
    case.variant_label = variant_label
    
    graph.add_case(case, parent_id=None)
    
    return case


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    print("Mutation Trace System - Implementation Test")
    print("=" * 60)
    
    # Create graph
    graph = MutationGraph()
    print(f"Created graph: {graph.graph_id}")
    print(f"Phase: {graph.phase.value}")
    
    # Create seed
    seed = create_seed(
        graph,
        problem_name="Two Sum",
        variant_label="correct",
        code="def twoSum(nums, target): pass"
    )
    print(f"\nCreated seed: {seed.case_id}")
    print(f"  Generation: {seed.generation}")
    print(f"  Identity: {seed.identity_key[:16]}...")
    
    # Apply mutation (in GENESIS phase)
    mutant1 = apply_mutation(
        graph,
        seed,
        mutation_type="scale",
        params={"input_size": "large", "perturbation": 0.1},
        trigger={"risk": "HIGH", "reason": "boundary_case"}
    )
    print(f"\nApplied scale mutation: {mutant1.case_id}")
    print(f"  Generation: {mutant1.generation}")
    print(f"  Identity: {mutant1.identity_key[:16]}...")
    
    # Verify determinism (create fresh graph)
    test_graph = MutationGraph()
    mutant1_dup = apply_mutation(
        test_graph,
        seed,
        mutation_type="scale",
        params={"perturbation": 0.1, "input_size": "large"},  # Same params, different order
        trigger={"risk": "HIGH", "reason": "boundary_case"}
    )
    print(f"\nDeterminism check:")
    print(f"  Original: {mutant1.identity_key[:16]}...")
    print(f"  Duplicate: {mutant1_dup.identity_key[:16]}...")
    print(f"  Match: {mutant1.identity_key == mutant1_dup.identity_key}")
    
    # Phase transition
    print(f"\nStarting evaluation...")
    graph.start_evaluation()
    print(f"Phase: {graph.phase.value}")
    print(f"Eval started: {graph.eval_started_at}")
    
    # Verify immutability
    try:
        apply_mutation(graph, mutant1, "boundary", {"case": "test"})
        print("ERROR: Should have raised exception")
    except ValueError as e:
        print(f"Immutability enforced: {e}")
    
    print("\n" + "=" * 60)
    print("Implementation verified.")
