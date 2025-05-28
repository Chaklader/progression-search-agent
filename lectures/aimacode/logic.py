"""Representations and Inference for Logic (Chapters 7-9, 12)

Covers both Propositional and First-Order Logic. First we have four
important data types:

    KB            Abstract class holds a knowledge base of logical expressions
    Expr          A logical expression, imported from utils.py
    substitution  Implemented as a dictionary of var:value pairs, {x:1, y:x}

Be careful: some functions take an Expr as argument, and some take a KB.

Logical expressions can be created with Expr or expr, imported from utils, TODO
or with expr, which adds the capability to write a string that uses
the connectives ==>, <==, <=>, or <=/=>. But be careful: these have the
opertor precedence of commas; you may need to add parens to make precendence work.
See logic.ipynb for examples.

Then we implement various functions for doing logical inference:

    pl_true          Evaluate a propositional logical sentence in a model
    tt_entails       Say if a statement is entailed by a KB
    pl_resolution    Do resolution on propositional sentences
    dpll_satisfiable See if a propositional sentence is satisfiable
    WalkSAT          Try to find a solution for a set of clauses

And a few other functions:

    to_cnf           Convert to conjunctive normal form
    unify            Do unification of two FOL sentences
    diff, simp       Symbolic differentiation and simplification
"""

from .utils import (
    removeall, unique, first, isnumber, issequence, Expr, expr, subexpressions
)

import itertools
from collections import defaultdict

# ______________________________________________________________________________


class KB:
    """A knowledge base to which you can tell and ask sentences.
    
    This abstract base class defines the interface for all knowledge base implementations.
    A knowledge base is a collection of logical sentences that represent what an agent
    knows about the world. The KB supports three fundamental operations:
    
    1. TELL: Add new knowledge to the KB
    2. ASK: Query whether something follows from the KB
    3. RETRACT: Remove knowledge from the KB
    
    The distinction between propositional and first-order logic KBs is handled by
    subclasses. In propositional logic, ASK returns True/False. In first-order logic,
    ASK can return multiple substitutions that satisfy the query.
    
    Why ask_generator instead of ask?
    The book is a bit vague on what ask means --
    For a Propositional Logic KB, ask(P & Q) returns True or False, but for an
    FOL KB, something like ask(Brother(x, y)) might return many substitutions
    such as {x: Cain, y: Abel}, {x: Abel, y: Cain}, {x: George, y: Jeb}, etc.
    So ask_generator generates these one at a time, and ask either returns the
    first one or returns False.
    
    Theoretical Foundation:
    ----------------------
    Knowledge bases implement the TELL-ASK interface described in AIMA Chapter 7.
    They separate domain-specific content (the sentences) from domain-independent
    inference procedures (the methods). This allows the same inference algorithms
    to work across different domains by changing only the knowledge content.
    
    Design Pattern:
    --------------
    This uses the Template Method pattern - subclasses must implement the abstract
    methods while inheriting the common ask() behavior that uses ask_generator().
    """

    def __init__(self, sentence=None):
        """Initialize a knowledge base, optionally with an initial sentence.
        
        Parameters:
        -----------
        sentence : Expr, optional
            An initial logical sentence to add to the KB
            
        Note:
        -----
        This is an abstract class and cannot be instantiated directly.
        Use PropKB or FolKB for concrete implementations.
        """
        raise NotImplementedError

    def tell(self, sentence):
        """Add the sentence to the KB.
        
        This is the fundamental knowledge acquisition operation. When we learn
        a new fact or rule, we add it to our knowledge base. The implementation
        depends on the type of logic and internal representation used.
        
        Parameters:
        -----------
        sentence : Expr
            A logical sentence to add to the knowledge base
            
        Implementation Notes:
        --------------------
        - PropKB converts sentences to CNF before storing
        - FolKB stores definite clauses directly
        - Some KBs might index sentences for efficient retrieval
        """
        raise NotImplementedError

    def ask(self, query):
        """Return a substitution that makes the query true, or, failing that, return False.
        
        This is a convenience method that returns just the first answer from ask_generator.
        Use this when you only need one answer or a boolean result.
        
        Parameters:
        -----------
        query : Expr
            A logical expression to evaluate against the KB
            
        Returns:
        --------
        dict or False
            For FOL: a substitution like {x: John, y: Mary}
            For Propositional: {} if true, False otherwise
            
        Examples:
        ---------
        >>> kb = FolKB()
        >>> kb.tell(expr('Parent(John, Mary)'))
        >>> kb.ask(expr('Parent(John, x)'))
        {x: Mary}
        """
        return first(self.ask_generator(query), default=False)

    def ask_generator(self, query):
        """Yield all the substitutions that make query true.
        
        This generator method is the core inference mechanism. It finds all ways
        to satisfy the query given the current knowledge. For propositional logic,
        this yields {} if the query is entailed, nothing otherwise. For FOL, it
        yields all valid variable substitutions.
        
        Parameters:
        -----------
        query : Expr
            A logical expression potentially containing variables
            
        Yields:
        -------
        dict
            Each substitution that satisfies the query
            
        Theoretical Note:
        ----------------
        This implements the semantic definition of entailment: KB |= α means
        that α is true in all models where KB is true. The generator finds
        all such models (for propositional) or substitutions (for FOL).
        """
        raise NotImplementedError

    def retract(self, sentence):
        """Remove sentence from the KB.
        
        This operation supports belief revision - the ability to remove knowledge
        that is no longer believed to be true. This is essential for agents that
        operate in dynamic environments where facts can change.
        
        Parameters:
        -----------
        sentence : Expr
            The exact sentence to remove from the KB
            
        Implementation Challenges:
        -------------------------
        - Must handle sentences that were converted (e.g., to CNF)
        - May need to remove derived consequences
        - Should be efficient even for large KBs
        """
        raise NotImplementedError


class PropKB(KB):
    """A KB for propositional logic. Inefficient, with no indexing.
    
    This implementation stores propositional sentences as lists of clauses in
    Conjunctive Normal Form (CNF). While not optimized for performance, it
    clearly illustrates the fundamental concepts of propositional reasoning.
    
    Internal Representation:
    -----------------------
    All sentences are converted to CNF and stored as a list of clauses.
    CNF format: (A ∨ B) ∧ (¬C ∨ D) ∧ ...
    Each clause is a disjunction of literals.
    
    Why CNF?
    --------
    1. Uniform representation simplifies algorithms
    2. Enables efficient resolution-based inference  
    3. Many optimizations work specifically with CNF
    4. Satisfiability algorithms (like DPLL) require CNF
    
    Attributes:
    -----------
    clauses : list of Expr
        List of clauses, each in disjunctive form
        
    Example Usage:
    -------------
    >>> kb = PropKB()
    >>> kb.tell(expr('P ==> Q'))
    >>> kb.tell(expr('P'))
    >>> kb.ask(expr('Q'))
    {}  # Empty dict means "true"
    """

    def __init__(self, sentence=None):
        """Initialize a propositional KB, optionally with an initial sentence.
        
        Parameters:
        -----------
        sentence : Expr or str, optional
            Initial knowledge to add to the KB
            
        Examples:
        ---------
        >>> kb1 = PropKB()  # Empty KB
        >>> kb2 = PropKB('P & Q')  # KB with initial knowledge
        >>> kb3 = PropKB(expr('P ==> Q'))  # Using Expr directly
        """
        self.clauses = []
        if sentence:
            self.tell(sentence)

    def tell(self, sentence):
        """Add the sentence's clauses to the KB.
        
        This method showcases a key design decision: all sentences are immediately
        converted to CNF before storage. This preprocessing cost is paid once,
        enabling more efficient inference later.
        
        Parameters:
        -----------
        sentence : Expr or str
            A propositional logic sentence
            
        Process:
        --------
        1. Convert sentence to CNF using to_cnf()
        2. Break the CNF into individual clauses using conjuncts()
        3. Add each clause to our clause list
        
        Example:
        --------
        >>> kb = PropKB()
        >>> kb.tell('(A | B) ==> C')
        # Internally stores: [~A | C, ~B | C]
        """
        self.clauses.extend(conjuncts(to_cnf(sentence)))

    def ask_generator(self, query):
        """Yield the empty substitution {} if KB entails query; else no results.
        
        For propositional logic, entailment is a yes/no question. We yield {}
        to indicate "true" (consistent with FOL where {} is the empty substitution),
        or yield nothing to indicate "false".
        
        Parameters:
        -----------
        query : Expr
            A propositional sentence to check
            
        Yields:
        -------
        dict
            {} if KB entails query, nothing otherwise
            
        Algorithm:
        ----------
        Uses truth table entailment (tt_entails) to check if the query
        follows from the conjunction of all clauses in the KB.
        
        Computational Note:
        ------------------
        This has exponential complexity in the worst case, making it
        impractical for large KBs. Real systems use more sophisticated
        algorithms like DPLL or CDCL.
        """
        if tt_entails(Expr('&', *self.clauses), query):
            yield {}

    def ask_if_true(self, query):
        """Return True if the KB entails query, else return False.
        
        Convenience method that returns a boolean instead of a substitution.
        This is more intuitive for propositional logic where we usually just
        want to know if something is true or false.
        
        Parameters:
        -----------
        query : Expr
            Propositional sentence to check
            
        Returns:
        --------
        bool
            True if KB |= query, False otherwise
            
        Example:
        --------
        >>> kb = PropKB('P & (P ==> Q)')
        >>> kb.ask_if_true('Q')
        True
        >>> kb.ask_if_true('~P')
        False
        """
        for _ in self.ask_generator(query):
            return True
        return False

    def retract(self, sentence):
        """Remove the sentence's clauses from the KB.
        
        This removes all clauses that came from the given sentence. Note that
        if multiple sentences produced the same clause, this might remove
        clauses that were also derived from other sentences.
        
        Parameters:
        -----------
        sentence : Expr
            The sentence whose clauses should be removed
            
        Limitations:
        -----------
        - No tracking of clause origins
        - May remove clauses derived from multiple sentences
        - No handling of dependent inferences
        """
        for c in conjuncts(to_cnf(sentence)):
            if c in self.clauses:
                self.clauses.remove(c)

# ______________________________________________________________________________


def is_symbol(s):
    """A string s is a symbol if it starts with an alphabetic char.
    
    Symbols are the atomic building blocks of logical expressions. They
    represent propositions (in propositional logic) or predicates, functions,
    and constants (in first-order logic).
    
    Parameters:
    -----------
    s : any
        Value to test
        
    Returns:
    --------
    bool
        True if s is a string starting with a letter
        
    Examples:
    ---------
    >>> is_symbol('P')
    True
    >>> is_symbol('x1')
    True
    >>> is_symbol('1x')
    False
    >>> is_symbol(42)
    False
    
    Design Rationale:
    ----------------
    Requiring alphabetic start prevents confusion with numbers and
    operators while allowing alphanumeric symbols like 'P1', 'x2', etc.
    """
    return isinstance(s, str) and s[:1].isalpha()


def is_var_symbol(s):
    """A logic variable symbol is an initial-lowercase string.
    
    Variables in first-order logic represent objects that can be bound to
    different values. The lowercase convention distinguishes them from
    constants and predicates (which start with uppercase).
    
    Parameters:
    -----------
    s : any
        Value to test
        
    Returns:
    --------
    bool
        True if s is a variable symbol
        
    Examples:
    ---------
    >>> is_var_symbol('x')
    True
    >>> is_var_symbol('brother')
    True
    >>> is_var_symbol('John')  # Constant, not variable
    False
    >>> is_var_symbol('P')     # Proposition, not variable
    False
    
    Convention Note:
    ---------------
    This naming convention (lowercase = variable, uppercase = constant)
    is standard in Prolog and many logic systems. It provides immediate
    visual distinction between bindable variables and fixed terms.
    """
    return is_symbol(s) and s[0].islower()


def is_prop_symbol(s):
    """A proposition logic symbol is an initial-uppercase string.
    
    Propositions represent atomic statements that are either true or false.
    In propositional logic, these are our basic building blocks. In FOL,
    this same test identifies predicates and constants.
    
    Parameters:
    -----------
    s : any
        Value to test
        
    Returns:
    --------
    bool
        True if s is a propositional/predicate symbol
        
    Examples:
    ---------
    >>> is_prop_symbol('P')
    True
    >>> is_prop_symbol('Rain')
    True
    >>> is_prop_symbol('x')  # Variable, not proposition
    False
    
    Theoretical Note:
    ----------------
    The distinction between propositional and predicate symbols is
    contextual. 'P' alone is propositional; 'P(x)' is a predicate
    applied to an argument.
    """
    return is_symbol(s) and s[0].isupper()


def variables(s):
    """Return a set of the variables in expression s.
    
    This function performs a deep traversal of the expression tree to find
    all variable symbols. It's essential for algorithms that need to handle
    variable bindings, like unification and substitution.
    
    Parameters:
    -----------
    s : Expr
        A logical expression possibly containing variables
        
    Returns:
    --------
    set
        Set of all variable symbols in the expression
        
    Examples:
    ---------
    >>> variables(expr('F(x, x) & G(x, y) & H(y, z) & R(A, z, 2)')) == {x, y, z}
    True
    >>> variables(expr('P & Q'))  # No variables
    set()
    
    Algorithm:
    ----------
    Uses set comprehension over all subexpressions, filtering for
    those identified as variables by is_variable().
    
    Use Cases:
    ----------
    - Checking if an expression is ground (variable-free)
    - Standardizing variables apart
    - Determining scope in quantified expressions
    """
    return {x for x in subexpressions(s) if is_variable(x)}


def is_definite_clause(s):
    """Returns True for exprs s of the form A & B & ... & C ==> D,
    where all literals are positive.  In clause form, this is
    ~A | ~B | ... | ~C | D, where exactly one clause is positive.
    
    Definite clauses (also called Horn clauses) are important because they
    enable efficient inference through forward and backward chaining. Many
    real-world knowledge bases can be expressed using only definite clauses.
    
    Parameters:
    -----------
    s : Expr
        Expression to test
        
    Returns:
    --------
    bool
        True if s is a definite clause
        
    Examples:
    ---------
    >>> is_definite_clause(expr('Farmer(Mac)'))
    True
    >>> is_definite_clause(expr('Farmer(x) & Rabbit(y) ==> Hates(x, y)'))
    True
    >>> is_definite_clause(expr('P | Q'))  # Not definite - two positive literals
    False
    
    Mathematical Definition:
    -----------------------
    A definite clause has the form: P₁ ∧ P₂ ∧ ... ∧ Pₙ → Q
    where all Pᵢ and Q are positive literals (no negations).
    
    Why Definite Clauses Matter:
    ---------------------------
    1. Forward chaining is complete for definite clause KBs
    2. Inference is polynomial rather than exponential
    3. Natural for expressing rules and facts
    4. Foundation of logic programming (Prolog)
    """
    if is_symbol(s.op):
        return True
    elif s.op == '==>':
        antecedent, consequent = s.args
        return (is_symbol(consequent.op) and
                all(is_symbol(arg.op) for arg in conjuncts(antecedent)))
    else:
        return False


def parse_definite_clause(s):
    """Return the antecedents and the consequent of a definite clause.
    
    This function decomposes a definite clause into its component parts,
    which is essential for rule-based inference algorithms like forward
    and backward chaining.
    
    Parameters:
    -----------
    s : Expr
        A definite clause expression
        
    Returns:
    --------
    tuple
        (antecedents, consequent) where antecedents is a list
        
    Examples:
    ---------
    >>> parse_definite_clause(expr('P ==> Q'))
    ([P], Q)
    >>> parse_definite_clause(expr('A & B & C ==> D'))
    ([A, B, C], D)
    >>> parse_definite_clause(expr('P'))  # Atomic clause
    ([], P)
    
    Raises:
    -------
    AssertionError
        If s is not a definite clause
        
    Use in Inference:
    ----------------
    Forward chaining: If all antecedents are known, infer consequent
    Backward chaining: To prove consequent, prove all antecedents
    """
    assert is_definite_clause(s)
    if is_symbol(s.op):
        return [], s
    else:
        antecedent, consequent = s.args
        return conjuncts(antecedent), consequent

# Useful constant Exprs used in examples and code:
A, B, C, D, E, F, G, P, Q, x, y, z = map(Expr, 'ABCDEFGPQxyz')


# ______________________________________________________________________________


def tt_entails(kb, alpha):
    """Does kb entail the sentence alpha? Use truth tables. For propositional
    kb's and sentences. [Figure 7.10]. Note that the 'kb' should be an
    Expr which is a conjunction of clauses.
    
    This implements the semantic definition of entailment: KB |= α if and only if
    α is true in every model where KB is true. It does this by exhaustively
    checking all possible truth assignments.
    
    Parameters:
    -----------
    kb : Expr
        Knowledge base as a conjunction of clauses
    alpha : Expr
        Query sentence (must be propositional - no variables)
        
    Returns:
    --------
    bool
        True if kb entails alpha, False otherwise
        
    Examples:
    ---------
    >>> tt_entails(expr('P & Q'), expr('Q'))
    True
    >>> tt_entails(expr('P | Q'), expr('P & Q'))
    False
    >>> tt_entails(expr('P ==> Q'), expr('~Q ==> ~P'))  # Contrapositive
    True
    
    Algorithm Overview:
    ------------------
    1. Extract all propositional symbols from KB and query
    2. Generate all 2^n possible truth assignments (models)
    3. For each model:
       - If KB is false, skip (vacuously true)
       - If KB is true but query is false, entailment fails
    4. If all models satisfy the condition, entailment holds
    
    Complexity:
    -----------
    O(2^n) where n is the number of distinct propositional symbols.
    This exponential complexity makes the algorithm impractical for
    large knowledge bases.
    
    Mathematical Foundation:
    -----------------------
    This directly implements the definition:
    KB |= α iff M(KB) ⊆ M(α)
    where M(φ) is the set of models satisfying φ
    """
    assert not variables(alpha)
    return tt_check_all(kb, alpha, prop_symbols(kb & alpha), {})


def tt_check_all(kb, alpha, symbols, model):
    """Auxiliary routine to implement tt_entails.
    
    This recursive function implements the truth table method by systematically
    assigning truth values to all propositional symbols and checking the
    entailment condition for each complete assignment.
    
    Parameters:
    -----------
    kb : Expr
        The knowledge base
    alpha : Expr
        The query
    symbols : list
        Remaining symbols to assign
    model : dict
        Partial truth assignment built so far
        
    Returns:
    --------
    bool
        True if entailment holds for all extensions of model
        
    Algorithm:
    ----------
    Base case: All symbols assigned
        - If KB is false, return True (vacuous truth)
        - If KB is true, return whether alpha is also true
    Recursive case: 
        - Try assigning True to next symbol
        - Try assigning False to next symbol
        - Return True only if both branches succeed
        
    Key Insight:
    -----------
    The recursive structure implements a depth-first search through
    the space of all possible truth assignments. Early termination
    happens when we find a counterexample.
    
    Example Trace:
    -------------
    Checking if P entails P|Q:
    - Try P=True: KB(P)=True, alpha(P|Q)=True ✓
    - Try P=False: KB(P)=False, vacuously true ✓
    Result: Entailment holds
    """
    if not symbols:
        if pl_true(kb, model):
            result = pl_true(alpha, model)
            assert result in (True, False)
            return result
        else:
            return True
    else:
        P, rest = symbols[0], symbols[1:]
        return (tt_check_all(kb, alpha, rest, extend(model, P, True)) and
                tt_check_all(kb, alpha, rest, extend(model, P, False)))


def prop_symbols(x):
    """Return a list of all propositional symbols in x.
    
    This function extracts all atomic propositions from a logical expression,
    which is necessary for algorithms that need to enumerate all possible
    truth assignments (like truth table methods).
    
    Parameters:
    -----------
    x : Expr
        A logical expression
        
    Returns:
    --------
    list
        All unique propositional symbols in x
        
    Examples:
    ---------
    >>> sorted([str(s) for s in prop_symbols(expr('P & Q ==> R'))])
    ['P', 'Q', 'R']
    >>> prop_symbols(expr('P & P ==> P'))  # Duplicates removed
    [P]
    
    Algorithm:
    ----------
    Recursively traverses the expression tree, collecting symbols
    and using set() to eliminate duplicates.
    
    Note:
    -----
    Only returns atomic propositions, not compound expressions.
    Operators like &, |, ~ are not included.
    """
    if not isinstance(x, Expr):
        return []
    elif is_prop_symbol(x.op):
        return [x]
    else:
        return list(set(symbol for arg in x.args for symbol in prop_symbols(arg)))


def tt_true(s):
    """Is a propositional sentence a tautology?
    
    A tautology is a sentence that is true in all possible models.
    Classic examples include P | ~P (law of excluded middle) and
    P ==> P (reflexivity of implication).
    
    Parameters:
    -----------
    s : str or Expr
        A propositional sentence
        
    Returns:
    --------
    bool
        True if s is a tautology
        
    Examples:
    ---------
    >>> tt_true('P | ~P')
    True
    >>> tt_true('P ==> P')
    True
    >>> tt_true('P & ~P')  # Contradiction
    False
    >>> tt_true('P | Q')   # Contingent
    False
    
    Implementation:
    --------------
    A sentence is a tautology iff it is entailed by the empty KB.
    This works because a tautology must be true regardless of what
    else might be true.
    
    Use Cases:
    ----------
    - Validating logical laws
    - Simplifying expressions (tautologies can be replaced by True)
    - Checking argument validity
    """
    s = expr(s)
    return tt_entails(True, s)


def pl_true(exp, model={}):
    """Return True if the propositional logic expression is true in the model,
    and False if it is false. If the model does not specify the value for
    every proposition, this may return None to indicate 'not obvious';
    this may happen even when the expression is tautological.
    
    This function implements the recursive definition of truth in propositional
    logic. It's the computational analog of the semantic evaluation rules.
    
    Parameters:
    -----------
    exp : Expr or bool
        A propositional logic expression
    model : dict
        A truth assignment mapping propositions to bool values
        
    Returns:
    --------
    bool or None
        True/False if definite in model, None if undetermined
        
    Examples:
    ---------
    >>> pl_true(expr('P & Q'), {P: True, Q: True})
    True
    >>> pl_true(expr('P | Q'), {P: True})  # Q unknown but result determined
    True
    >>> pl_true(expr('P & Q'), {P: True})  # Q unknown, result undetermined
    None
    
    Semantic Rules Implemented:
    --------------------------
    - ¬P is true iff P is false
    - P ∧ Q is true iff both P and Q are true
    - P ∨ Q is true iff at least one of P or Q is true
    - P → Q is true iff P is false or Q is true
    - P ↔ Q is true iff P and Q have the same truth value
    
    Three-Valued Logic:
    ------------------
    The use of None implements a three-valued logic where propositions
    can be True, False, or Unknown. This enables early termination in
    many algorithms - e.g., if one disjunct is True, the disjunction
    is True regardless of other disjuncts.
    
    Implementation Note:
    -------------------
    The short-circuit evaluation for | and & operators mirrors the
    behavior of Python's 'or' and 'and' but with three-valued logic.
    """
    if exp in (True, False):
        return exp
    op, args = exp.op, exp.args
    if is_prop_symbol(op):
        return model.get(exp)
    elif op == '~':
        p = pl_true(args[0], model)
        if p is None:
            return None
        else:
            return not p
    elif op == '|':
        result = False
        for arg in args:
            p = pl_true(arg, model)
            if p is True:
                return True
            if p is None:
                result = None
        return result
    elif op == '&':
        result = True
        for arg in args:
            p = pl_true(arg, model)
            if p is False:
                return False
            if p is None:
                result = None
        return result
    p, q = args
    if op == '==>':
        return pl_true(~p | q, model)
    elif op == '<==':
        return pl_true(p | ~q, model)
    pt = pl_true(p, model)
    if pt is None:
        return None
    qt = pl_true(q, model)
    if qt is None:
        return None
    if op == '<=>':
        return pt == qt
    elif op == '^':  # xor or 'not equivalent'
        return pt != qt
    else:
        raise ValueError("illegal operator in logic expression" + str(exp))

# ______________________________________________________________________________

# Convert to Conjunctive Normal Form (CNF)


def to_cnf(s):
    """Convert a propositional logical sentence to conjunctive normal form.
    That is, to the form ((A | ~B | ...) & (B | C | ...) & ...) [p. 253]
    
    CNF is a standardized format where the sentence is a conjunction (AND) of
    clauses, where each clause is a disjunction (OR) of literals. This format
    is crucial for many inference algorithms.
    
    Parameters:
    -----------
    s : str or Expr
        A propositional logic sentence
        
    Returns:
    --------
    Expr
        The sentence in CNF
        
    Examples:
    ---------
    >>> to_cnf('~(B | C)')
    (~B & ~C)
    >>> to_cnf('A ==> B')
    (~A | B)
    >>> to_cnf('A <=> B')
    ((~A | B) & (~B | A))
    
    Algorithm Steps:
    ---------------
    1. Eliminate implications: Convert ==> to |, <=> to & and |
    2. Move negations inward: Apply De Morgan's laws, eliminate double negation
    3. Distribute OR over AND: Transform to conjunction of disjunctions
    
    Why CNF?
    --------
    1. Uniform representation enables systematic algorithms
    2. Resolution works directly with CNF clauses
    3. SAT solvers require CNF input
    4. Many optimizations are CNF-specific
    
    Complexity Note:
    ---------------
    CNF conversion can cause exponential blowup in formula size.
    For example, (A & B) | (C & D) | (E & F) | ... grows exponentially
    when distributed. This is why some systems use alternative forms
    like Negation Normal Form (NNF) or circuits.
    
    Mathematical Properties:
    -----------------------
    - Preserves logical equivalence
    - Every propositional formula has a CNF form
    - CNF is not unique (different orders, redundant clauses)
    """
    s = expr(s)
    if isinstance(s, str):
        s = expr(s)
    s = eliminate_implications(s)  # Steps 1, 2 from p. 253
    s = move_not_inwards(s)  # Step 3
    return distribute_and_over_or(s)  # Step 4


def eliminate_implications(s):
    """Change implications into equivalent form with only &, |, and ~ as logical operators.
    
    This is the first step in CNF conversion. It removes "syntactic sugar" operators
    like ==>, <==, <=>, and ^ (xor), replacing them with the fundamental operators.
    
    Parameters:
    -----------
    s : Expr
        A logical expression possibly containing implications
        
    Returns:
    --------
    Expr
        Equivalent expression using only &, |, ~
        
    Transformation Rules:
    --------------------
    - A ==> B becomes ~A | B (material implication)
    - A <== B becomes A | ~B (reverse implication)
    - A <=> B becomes (A | ~B) & (B | ~A) (biconditional)
    - A ^ B becomes (A & ~B) | (~A & B) (exclusive or)
    
    Examples:
    ---------
    >>> eliminate_implications(expr('P ==> Q'))
    (~P | Q)
    >>> eliminate_implications(expr('P <=> Q'))
    ((P | ~Q) & (Q | ~P))
    
    Theoretical Foundation:
    ----------------------
    These transformations are based on logical equivalences:
    - P → Q ≡ ¬P ∨ Q (definition of material implication)
    - P ↔ Q ≡ (P → Q) ∧ (Q → P) (definition of biconditional)
    - P ⊕ Q ≡ (P ∧ ¬Q) ∨ (¬P ∧ Q) (definition of XOR)
    
    Recursion Note:
    --------------
    The function recursively processes subexpressions to ensure
    all implications are eliminated throughout the expression tree.
    """
    if s is False:
        s = expr("F")
    if s is True:
        s = expr("T")
    s = expr(s)
    if not s.args or is_symbol(s.op):
        return s  # Atoms are unchanged.
    args = list(map(eliminate_implications, s.args))
    a, b = args[0], args[-1]
    if s.op == '==>':
        return b | ~a
    elif s.op == '<==':
        return a | ~b
    elif s.op == '<=>':
        return (a | ~b) & (b | ~a)
    elif s.op == '^':
        assert len(args) == 2  # TODO: relax this restriction
        return (a & ~b) | (~a & b)
    else:
        assert s.op in ('&', '|', '~')
        return Expr(s.op, *args)


def move_not_inwards(s):
    """Rewrite sentence s by moving negation sign inward.
    
    This implements Step 2 of CNF conversion, applying De Morgan's laws and
    eliminating double negations until all negations appear only on atomic
    propositions (literals).
    
    Parameters:
    -----------
    s : Expr
        Expression possibly containing negations of complex formulas
        
    Returns:
    --------
    Expr
        Equivalent expression with negations only on atoms
        
    Examples:
    ---------
    >>> move_not_inwards(~(A | B))
    (~A & ~B)
    >>> move_not_inwards(~~A)
    A
    >>> move_not_inwards(~(A & B & C))
    (~A | ~B | ~C)
    
    Transformation Rules:
    --------------------
    1. ~~A → A (double negation elimination)
    2. ~(A & B) → ~A | ~B (De Morgan's law)
    3. ~(A | B) → ~A & ~B (De Morgan's law)
    
    De Morgan's Laws:
    ----------------
    These laws, discovered by Augustus De Morgan, show how negation
    distributes over conjunction and disjunction:
    - The negation of a conjunction is the disjunction of negations
    - The negation of a disjunction is the conjunction of negations
    
    Implementation Detail:
    ---------------------
    The function uses a helper NOT function to recursively apply
    negation, which elegantly handles the De Morgan transformations.
    
    Why Move Negations Inward?
    -------------------------
    Having negations only on atomic propositions simplifies:
    - The distribution step that follows
    - Pattern matching in inference algorithms
    - Literal counting and indexing
    """
    s = expr(s)
    if s.op == '~':
        def NOT(b):
            return move_not_inwards(~b)
        a = s.args[0]
        if a.op == '~':
            return move_not_inwards(a.args[0])  # ~~A ==> A
        if a.op == '&':
            return associate('|', list(map(NOT, a.args)))
        if a.op == '|':
            return associate('&', list(map(NOT, a.args)))
        return s
    elif is_symbol(s.op) or not s.args:
        return s
    else:
        return Expr(s.op, *list(map(move_not_inwards, s.args)))


def distribute_and_over_or(s):
    """Given a sentence s consisting of conjunctions and disjunctions
    of literals, return an equivalent sentence in CNF.
    
    This is the final step of CNF conversion, applying the distributive
    law to ensure the top-level operator is AND and each clause is a
    disjunction of literals.
    
    Parameters:
    -----------
    s : Expr
        Expression with negations only on literals
        
    Returns:
    --------
    Expr
        Expression in CNF form
        
    Examples:
    ---------
    >>> distribute_and_over_or((A & B) | C)
    ((A | C) & (B | C))
    >>> distribute_and_over_or((A | B) & (C | D))
    ((A | B) & (C | D))  # Already in CNF
    
    Distributive Law:
    ----------------
    (A & B) | C ≡ (A | C) & (B | C)
    
    This law allows us to "pull out" conjunctions from inside
    disjunctions, eventually moving all ANDs to the top level.
    
    Algorithm:
    ----------
    1. If expression is a disjunction (|):
       - Find any conjunctive subterms
       - Distribute the disjunction over them
       - Recursively process the results
    2. If expression is a conjunction (&):
       - Recursively process each conjunct
    3. Otherwise, return unchanged (literal)
    
    Complexity Warning:
    ------------------
    This step can cause exponential blowup. For example:
    (A1 & A2) | (B1 & B2) | ... | (Z1 & Z2)
    produces 2^26 clauses when fully distributed!
    
    Optimization Note:
    -----------------
    Real systems often use structure-preserving transformations
    or work with alternative normal forms to avoid this blowup.
    """
    s = expr(s)
    if s.op == '|':
        s = associate('|', s.args)
        if s.op != '|':
            return distribute_and_over_or(s)
        if len(s.args) == 0:
            return False
        if len(s.args) == 1:
            return distribute_and_over_or(s.args[0])
        conj = first(arg for arg in s.args if arg.op == '&')
        if not conj:
            return s
        others = [a for a in s.args if a is not conj]
        rest = associate('|', others)
        return associate('&', [distribute_and_over_or(c | rest)
                               for c in conj.args])
    elif s.op == '&':
        return associate('&', list(map(distribute_and_over_or, s.args)))
    else:
        return s


def associate(op, args):
    """Given an associative op, return an expression with the same
    meaning as Expr(op, *args), but flattened -- that is, with nested
    instances of the same op promoted to the top level.
    
    This function exploits the associative property of & and | to create
    flat representations that are easier to process.
    
    Parameters:
    -----------
    op : str
        An associative operator ('&', '|', '+', '*')
    args : list
        List of argument expressions
        
    Returns:
    --------
    Expr
        Flattened expression
        
    Examples:
    ---------
    >>> associate('&', [(A&B),(B|C),(B&C)])
    (A & B & (B | C) & B & C)
    >>> associate('|', [A|(B|(C|(A&B)))])
    (A | B | C | (A & B))
    
    Associative Property:
    --------------------
    For operators ⊕ that are associative:
    (A ⊕ B) ⊕ C = A ⊕ (B ⊕ C)
    
    This allows us to write A ⊕ B ⊕ C without parentheses.
    
    Identity Elements:
    -----------------
    The function handles identity elements:
    - True is identity for & (A & True = A)
    - False is identity for | (A | False = A)
    - 0 is identity for + (A + 0 = A)
    - 1 is identity for * (A * 1 = A)
    
    Why Flatten?
    -----------
    1. Simplifies pattern matching
    2. Reduces tree depth
    3. Enables efficient clause representation
    4. Facilitates duplicate detection
    """
    args = dissociate(op, args)
    if len(args) == 0:
        return _op_identity[op]
    elif len(args) == 1:
        return args[0]
    else:
        return Expr(op, *args)

_op_identity = {'&': True, '|': False, '+': 0, '*': 1}


def dissociate(op, args):
    """Given an associative op, return a flattened list result such
    that Expr(op, *result) means the same as Expr(op, *args).
    
    This helper function recursively extracts all arguments at any
    nesting level that use the same operator.
    
    Parameters:
    -----------
    op : str
        The operator to flatten
    args : list
        Possibly nested argument list
        
    Returns:
    --------
    list
        Flat list of arguments
        
    Example:
    --------
    >>> dissociate('&', [A&B, C, D&E&F])
    [A, B, C, D, E, F]
    
    Algorithm:
    ----------
    Recursively traverses the expression tree, collecting all
    arguments that don't use the given operator. When it finds
    a subexpression with the same operator, it recursively
    dissociates that subexpression.
    
    Use with associate():
    --------------------
    dissociate() flattens nested structures, then associate()
    rebuilds them in canonical flat form. This two-step process
    ensures proper handling of edge cases like empty arguments.
    """
    result = []

    def collect(subargs):
        for arg in subargs:
            if arg.op == op:
                collect(arg.args)
            else:
                result.append(arg)
    collect(args)
    return result


def conjuncts(s):
    """Return a list of the conjuncts in the sentence s.
    
    A conjunct is a top-level component of a conjunction. This function
    is particularly useful for extracting clauses from CNF sentences.
    
    Parameters:
    -----------
    s : Expr
        A logical expression
        
    Returns:
    --------
    list
        List of conjuncts (components joined by &)
        
    Examples:
    ---------
    >>> conjuncts(A & B)
    [A, B]
    >>> conjuncts(A | B)
    [(A | B)]
    >>> conjuncts(A & B & C)
    [A, B, C]
    
    CNF Context:
    -----------
    In CNF, each conjunct is a clause (disjunction of literals).
    This function extracts all clauses from a CNF sentence.
    
    Implementation:
    --------------
    Uses dissociate to handle nested conjunctions, ensuring
    we get all conjuncts regardless of tree structure.
    """
    return dissociate('&', [s])


def disjuncts(s):
    """Return a list of the disjuncts in the sentence s.
    
    A disjunct is a top-level component of a disjunction. This function
    extracts literals from clauses in CNF.
    
    Parameters:
    -----------
    s : Expr
        A logical expression
        
    Returns:
    --------
    list
        List of disjuncts (components joined by |)
        
    Examples:
    ---------
    >>> disjuncts(A | B)
    [A, B]
    >>> disjuncts(A & B)
    [(A & B)]
    >>> disjuncts(A | B | C | D)
    [A, B, C, D]
    
    Resolution Context:
    ------------------
    When applying resolution to CNF clauses, we need to examine
    all literals (disjuncts) in each clause to find complementary
    pairs.
    
    Symmetry with conjuncts():
    -------------------------
    These two functions are duals - conjuncts extracts AND
    components, disjuncts extracts OR components.
    """
    return dissociate('|', [s])

# ______________________________________________________________________________


def pl_resolution(KB, alpha):
    """Propositional-logic resolution: say if alpha follows from KB. [Figure 7.12]
    
    Resolution is a complete inference procedure for propositional logic. It works
    by proof by contradiction: to prove KB |= α, we show that KB ∧ ¬α is unsatisfiable.
    
    Parameters:
    -----------
    KB : PropKB
        A knowledge base in CNF
    alpha : Expr
        Query sentence
        
    Returns:
    --------
    bool
        True if KB entails alpha
        
    Algorithm Overview:
    ------------------
    1. Add negation of query to KB clauses
    2. Repeatedly apply resolution rule to all pairs of clauses
    3. If empty clause derived, query is entailed
    4. If no new clauses can be derived, query is not entailed
    
    Resolution Rule:
    ---------------
    From (A ∨ C) and (¬A ∨ D), derive (C ∨ D)
    
    The key insight: if A must be either true or false, and we have
    constraints for both cases, then the disjunction of the other
    literals must hold.
    
    Example:
    --------
    KB: {P∨Q, ¬P∨R, ¬Q∨R}
    Query: R
    
    Add ¬R to clauses
    Resolve P∨Q with ¬P∨R → Q∨R
    Resolve Q∨R with ¬Q∨R → R∨R → R
    Resolve R with ¬R → □ (empty clause)
    Therefore KB |= R
    
    Completeness:
    ------------
    Resolution is refutation-complete: if KB |= α, then resolution
    will derive the empty clause from KB ∧ ¬α. This was proven by
    Robinson in 1965.
    
    Efficiency Considerations:
    -------------------------
    - Naive implementation is O(n²) in number of clauses per iteration
    - Many redundant clauses may be generated
    - Strategies like set-of-support and subsumption improve efficiency
    """
    clauses = KB.clauses + conjuncts(to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i+1, n)]
        for (ci, cj) in pairs:
            resolvents = pl_resolve(ci, cj)
            if False in resolvents:
                return True
            new = new.union(set(resolvents))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)


def pl_resolve(ci, cj):
    """Return all clauses that can be obtained by resolving clauses ci and cj.
    
    The resolution rule: from (A ∨ C) and (¬A ∨ D), derive (C ∨ D).
    This function finds all possible resolvents from two clauses.
    
    Parameters:
    -----------
    ci, cj : Expr
        Two clauses (disjunctions of literals)
        
    Returns:
    --------
    list
        All possible resolvents
        
    Resolution Process:
    ------------------
    1. For each literal in ci, check if its negation appears in cj
    2. If found, create new clause with all other literals from both
    3. Remove duplicates and return simplified clause
    
    Example:
    --------
    >>> pl_resolve(expr('P | Q | R'), expr('~P | S | T'))
    [Q | R | S | T]
    
    Multiple Resolvents:
    -------------------
    If clauses share multiple complementary pairs, multiple
    resolvents are possible:
    >>> pl_resolve(expr('P | Q'), expr('~P | ~Q'))
    [Q | ~Q, P | ~P]
    
    Note these are tautologies and typically filtered out.
    
    Edge Cases:
    -----------
    - Resolving unit clauses P and ~P yields empty clause (False)
    - Tautological resolvents are kept (filtering is caller's job)
    - Self-resolution is prevented by the algorithm structure
    """
    clauses = []
    for di in disjuncts(ci):
        for dj in disjuncts(cj):
            if di == ~dj or ~di == dj:
                dnew = unique(removeall(di, disjuncts(ci)) +
                              removeall(dj, disjuncts(cj)))
                clauses.append(associate('|', dnew))
    return clauses

# ______________________________________________________________________________


class PropDefiniteKB(PropKB):
    """A KB of propositional definite clauses.
    
    Definite clauses (Horn clauses) have at most one positive literal.
    They can express facts (single positive literal) or rules
    (implication with positive consequent). This restricted form
    enables polynomial-time inference.
    
    Forms of definite clauses:
    -------------------------
    1. Fact: P (single positive literal)
    2. Rule: P₁ ∧ P₂ ∧ ... ∧ Pₙ → Q (implication)
    3. Goal: P₁ ∧ P₂ ∧ ... ∧ Pₙ → False (used in queries)
    
    Why Definite Clauses?
    --------------------
    - Natural for expressing rules and facts
    - Enable efficient forward/backward chaining
    - Foundation of logic programming (Prolog)
    - Complete for definite clause entailment
    
    Attributes:
    -----------
    clauses : list
        Stores sentences in implication form (not CNF)
        
    Example:
    --------
    >>> kb = PropDefiniteKB()
    >>> kb.tell(expr('American(x) & Weapon(y) & Sells(x, y, z) & Hostile(z) ==> Criminal(x)'))
    >>> kb.tell(expr('Missile(x) ==> Weapon(x)'))
    >>> kb.tell(expr('Enemy(x, America) ==> Hostile(x)'))
    """

    def tell(self, sentence):
        """Add a definite clause to this KB.
        
        Unlike PropKB, this stores definite clauses in their natural
        implication form rather than converting to CNF. This preserves
        the rule structure for efficient forward/backward chaining.
        
        Parameters:
        -----------
        sentence : Expr
            Must be a definite clause
            
        Raises:
        -------
        AssertionError
            If sentence is not a definite clause
            
        Storage Format:
        --------------
        - Facts stored as-is: P
        - Rules stored as implications: A & B ==> C
        No CNF conversion is performed.
        """
        assert is_definite_clause(sentence), "Must be definite clause"
        self.clauses.append(sentence)

    def ask_generator(self, query):
        """Yield the empty substitution if KB implies query; else nothing.
        
        Uses forward chaining (pl_fc_entails) for efficient inference
        in polynomial time, rather than the exponential truth table method.
        
        Parameters:
        -----------
        query : Expr
            A positive literal to prove
            
        Yields:
        -------
        dict
            {} if query can be derived
            
        Efficiency:
        -----------
        O(n) where n is the number of rules, compared to O(2^n)
        for general propositional inference.
        """
        if pl_fc_entails(self.clauses, query):
            yield {}

    def retract(self, sentence):
        """Remove a definite clause from the KB.
        
        Note: This doesn't retract consequences derived from the clause.
        In a production system, you might need truth maintenance to
        handle derived facts.
        """
        self.clauses.remove(sentence)

    def clauses_with_premise(self, p):
        """Return a list of the clauses in KB that have p in their premise.
        This could be cached away for O(1) speed, but we'll recompute it.
        
        This method supports forward chaining by finding all rules that
        could fire when p becomes known to be true.
        
        Parameters:
        -----------
        p : Expr
            A proposition that might appear in rule antecedents
            
        Returns:
        --------
        list
            All rules that have p as a premise
            
        Example:
        --------
        If KB contains "P & Q ==> R" and "P & S ==> T",
        then clauses_with_premise(P) returns both rules.
        
        Optimization Note:
        -----------------
        Production systems typically index rules by their premises
        for O(1) lookup. This implementation recomputes for simplicity.
        """
        return [c for c in self.clauses
                if c.op == '==>' and p in conjuncts(c.args[0])]


def pl_fc_entails(KB, q):
    """Use forward chaining to see if a PropDefiniteKB entails symbol q.
    [Figure 7.15]
    
    Forward chaining is a data-driven inference method that starts with
    known facts and derives new facts by applying rules whose premises
    are satisfied.
    
    Parameters:
    -----------
    KB : list
        List of definite clauses
    q : Expr
        Query proposition
        
    Returns:
    --------
    bool
        True if q can be derived from KB
        
    Algorithm:
    ----------
    1. Count premises for each rule
    2. Mark known facts as inferred
    3. When a fact is inferred:
       - Decrement count for rules using it
       - If count reaches 0, add conclusion to agenda
    4. Continue until query derived or no progress
    
    Example Trace:
    -------------
    KB: {P, Q, P&Q=>R, R=>S}
    Query: S
    
    1. Initial: inferred={P,Q}, count={P&Q=>R:2, R=>S:1}
    2. P reduces P&Q=>R count to 1
    3. Q reduces P&Q=>R count to 0, add R to agenda
    4. R reduces R=>S count to 0, add S to agenda
    5. S matches query, return True
    
    Complexity:
    -----------
    O(n) where n is the total number of premises across all rules.
    Each premise is processed at most once.
    
    Theoretical Properties:
    ----------------------
    - Sound: Only derives valid consequences
    - Complete: For definite clause KBs only
    - Efficient: Linear time in size of KB
    
    Connection to Production Systems:
    --------------------------------
    This algorithm is the basis for production rule systems used
    in expert systems and business rule engines.
    """
    count = {c: len(conjuncts(c.args[0]))
             for c in KB.clauses
             if c.op == '==>'}
    inferred = defaultdict(bool)
    agenda = [s for s in KB.clauses if is_prop_symbol(s.op)]
    while agenda:
        p = agenda.pop()
        if p == q:
            return True
        if not inferred[p]:
            inferred[p] = True
            for c in KB.clauses_with_premise(p):
                count[c] -= 1
                if count[c] == 0:
                    agenda.append(c.args[1])
    return False

""" [Figure 7.13]
Simple inference in a wumpus world example
"""
wumpus_world_inference = expr("(B11 <=> (P12 | P21))  &  ~B11")


""" [Figure 7.16]
Propositional Logic Forward Chaining example
"""
horn_clauses_KB = PropDefiniteKB()
for s in "P==>Q; (L&M)==>P; (B&L)==>M; (A&P)==>L; (A&B)==>L; A;B".split(';'):
    horn_clauses_KB.tell(expr(s))

# ______________________________________________________________________________
# DPLL-Satisfiable [Figure 7.17]


def dpll_satisfiable(s):
    """Check satisfiability of a propositional sentence.
    This differs from the book code in two ways: (1) it returns a model
    rather than True when it succeeds; this is more useful. (2) The
    function find_pure_symbol is passed a list of unknown clauses, rather
    than a list of all clauses and the model; this is more efficient.
    
    The Davis-Putnam-Logemann-Loveland (DPLL) algorithm is a complete,
    backtracking-based search algorithm for deciding the satisfiability
    of propositional logic formulas in CNF.
    
    Parameters:
    -----------
    s : Expr
        A propositional sentence
        
    Returns:
    --------
    dict or False
        A satisfying model {P: True, Q: False, ...} or False
        
    Algorithm Overview:
    ------------------
    1. Convert to CNF
    2. Apply unit propagation and pure literal elimination
    3. If needed, guess a variable value and backtrack
    
    Example:
    --------
    >>> dpll_satisfiable(expr('P & ~P'))
    False
    >>> dpll_satisfiable(expr('P | ~P'))
    {}  # Any model works for tautology
    
    Historical Note:
    ---------------
    DPLL (1962) forms the basis of modern SAT solvers, which can
    handle millions of variables. Modern variants add clause learning,
    non-chronological backtracking, and sophisticated heuristics.
    
    Applications:
    ------------
    - Hardware verification
    - Planning and scheduling  
    - Cryptanalysis
    - Bioinformatics
    """
    clauses = conjuncts(to_cnf(s))
    symbols = prop_symbols(s)
    return dpll(clauses, symbols, {})


def dpll(clauses, symbols, model):
    """See if the clauses are true in a partial model.
    
    This is the recursive heart of the DPLL algorithm. It extends a partial
    model by making truth assignments to variables, using inference rules
    and backtracking to efficiently explore the search space.
    
    Parameters:
    -----------
    clauses : list
        CNF clauses to satisfy
    symbols : list
        Unassigned propositional symbols
    model : dict
        Partial truth assignment
        
    Returns:
    --------
    dict or False
        Extended model if satisfiable, False otherwise
        
    Algorithm Steps:
    ---------------
    1. Check if current partial model satisfies/falsifies clauses
    2. Apply pure literal elimination if possible
    3. Apply unit propagation if possible
    4. Otherwise, pick a variable and try both values
    
    Key Optimizations:
    -----------------
    - Early termination: Stop if any clause is false
    - Pure literal: If P appears only positively, set P=True
    - Unit clause: If clause is (P), must set P=True
    - Clause learning: Modern SAT solvers learn from conflicts
    
    Three-valued Logic:
    ------------------
    Clauses can be:
    - True: At least one literal is true
    - False: All literals are false  
    - Unknown: No definite value yet
    
    Backtracking:
    ------------
    When guessing, try the first value. If that leads to conflict,
    backtrack and try the opposite value.
    """
    unknown_clauses = []  # clauses with an unknown truth value
    for c in clauses:
        val = pl_true(c, model)
        if val is False:
            return False
        if val is not True:
            unknown_clauses.append(c)
    if not unknown_clauses:
        return model
    P, value = find_pure_symbol(symbols, unknown_clauses)
    if P:
        return dpll(clauses, removeall(P, symbols), extend(model, P, value))
    P, value = find_unit_clause(clauses, model)
    if P:
        return dpll(clauses, removeall(P, symbols), extend(model, P, value))
    if not symbols:
        raise TypeError("Argument should be of the type Expr.")
    P, symbols = symbols[0], symbols[1:]
    return (dpll(clauses, symbols, extend(model, P, True)) or
            dpll(clauses, symbols, extend(model, P, False)))


def find_pure_symbol(symbols, clauses):
    """Find a symbol and its value if it appears only as a positive literal
    (or only as a negative) in clauses.
    
    A pure literal is one that appears with only one polarity in all
    clauses. Assigning it to satisfy all its occurrences can never
    make any clause false, so it's always safe.
    
    Parameters:
    -----------
    symbols : list
        Unassigned symbols to check
    clauses : list  
        Clauses to examine (only those with unknown truth value)
        
    Returns:
    --------
    tuple
        (symbol, value) if pure symbol found, (None, None) otherwise
        
    Examples:
    ---------
    >>> find_pure_symbol([A, B, C], [A|~B,~B|~C,C|A])
    (A, True)
    
    Theory:
    -------
    Pure literal elimination preserves satisfiability:
    - If P appears only positively, setting P=True satisfies all
      clauses containing P and doesn't falsify any clause
    - If P appears only negatively, setting P=False does the same
    
    Efficiency Note:
    ---------------
    This implementation is O(n*m) where n=|symbols|, m=|clauses|.
    Advanced implementations use occurrence lists for O(1) detection.
    """
    for s in symbols:
        found_pos, found_neg = False, False
        for c in clauses:
            if not found_pos and s in disjuncts(c):
                found_pos = True
            if not found_neg and ~s in disjuncts(c):
                found_neg = True
        if found_pos != found_neg:
            return s, found_pos
    return None, None


def find_unit_clause(clauses, model):
    """Find a forced assignment if possible from a clause with only 1
    variable not bound in the model.
    
    A unit clause has exactly one unassigned literal. That literal must
    be true for the clause (and thus the formula) to be satisfied.
    
    Parameters:
    -----------
    clauses : list
        All CNF clauses
    model : dict
        Current partial assignment
        
    Returns:
    --------
    tuple
        (symbol, value) if unit clause found, (None, None) otherwise
        
    Examples:
    ---------
    >>> find_unit_clause([A|B|C, B|~C, ~A|~B], {A:True})
    (B, False)
    
    Unit Propagation:
    ----------------
    Also called Boolean Constraint Propagation (BCP), this is the
    most important optimization in SAT solving. It implements the
    logical principle: if a clause has only one way to be satisfied,
    we must take that way.
    
    Cascading Effect:
    ----------------
    Setting one literal can create new unit clauses, leading to
    a cascade of forced assignments. Modern SAT solvers spend
    most of their time in unit propagation.
    
    Implementation Note:
    -------------------
    This finds the first unit clause. Modern solvers maintain
    watched literals for O(1) unit clause detection.
    """
    for clause in clauses:
        P, value = unit_clause_assign(clause, model)
        if P:
            return P, value
    return None, None


def unit_clause_assign(clause, model):
    """Return a single variable/value pair that makes clause true in
    the model, if possible.
    
    Examines a clause to determine if it's a unit clause under the
    current partial model. A clause is unit if exactly one literal
    is unassigned and all others are false.
    
    Parameters:
    -----------
    clause : Expr
        A disjunction of literals
    model : dict
        Current truth assignments
        
    Returns:
    --------
    tuple
        (symbol, value) if unit clause, (None, None) otherwise
        
    Examples:
    ---------
    >>> unit_clause_assign(A|B|C, {A:True})
    (None, None)  # Clause already satisfied
    >>> unit_clause_assign(B|~C, {A:True})
    (None, None)  # Two unbound variables
    >>> unit_clause_assign(~A|~B, {A:True})
    (B, False)    # Must set B=False
    
    Logic:
    ------
    For each literal in the clause:
    - If literal is true in model, clause is satisfied
    - If literal is unassigned, record it
    - If literal is false in model, continue
    
    If exactly one unassigned literal found, that's our unit.
    """
    P, value = None, None
    for literal in disjuncts(clause):
        sym, positive = inspect_literal(literal)
        if sym in model:
            if model[sym] == positive:
                return None, None  # clause already True
        elif P:
            return None, None      # more than 1 unbound variable
        else:
            P, value = sym, positive
    return P, value


def inspect_literal(literal):
    """The symbol in this literal, and the value it should take to
    make the literal true.
    
    Literals are either positive (P) or negative (~P). This function
    extracts the underlying symbol and polarity.
    
    Parameters:
    -----------
    literal : Expr
        A positive or negative atomic proposition
        
    Returns:
    --------
    tuple
        (symbol, positive) where positive is True for P, False for ~P
        
    Examples:
    ---------
    >>> inspect_literal(P)
    (P, True)
    >>> inspect_literal(~P)
    (P, False)
    
    Implementation:
    --------------
    Checks if the literal is a negation (~) and extracts the
    underlying symbol accordingly.
    
    Use in DPLL:
    -----------
    Critical for unit propagation and pure literal detection,
    where we need to know both what symbol to assign and what
    value to give it.
    """
    if literal.op == '~':
        return literal.args[0], False
    else:
        return literal, True


def unify(x, y, s):
    """Unify expressions x,y with substitution s; return a substitution that
    would make x,y equal, or None if x,y can not unify. x and y can be
    variables (e.g. Expr('x')), constants, lists, or Exprs. [Figure 9.1]
    
    Unification is the process of finding a substitution θ such that xθ = yθ.
    It's fundamental to first-order logic inference, allowing us to match
    general patterns with specific instances.
    
    Parameters:
    -----------
    x : Expr, str, list, or tuple
        First expression to unify
    y : Expr, str, list, or tuple
        Second expression to unify
    s : dict or None
        Current substitution {var: value, ...}
        
    Returns:
    --------
    dict or None
        Extended substitution if unifiable, None otherwise
        
    Examples:
    ---------
    >>> unify(expr('P(x)'), expr('P(John)'), {})
    {x: John}
    >>> unify(expr('P(x, x)'), expr('P(John, Mary)'), {})
    None  # Can't bind x to both John and Mary
    >>> unify(expr('P(x, f(x))'), expr('P(y, f(y))'), {})
    {x: y}  # Most general unifier
    
    Algorithm Overview:
    ------------------
    1. If x equals y, return current substitution
    2. If either is a variable, try to bind it
    3. If both are compound, unify components
    4. Otherwise, unification fails
    
    Most General Unifier (MGU):
    --------------------------
    Unification finds the MGU - the substitution that makes the
    fewest commitments. For P(x) and P(y), {x:y} is more general
    than {x:John, y:John}.
    
    Occur Check:
    -----------
    Prevents infinite structures like x = f(x). Without this check,
    unifying P(x) with P(f(x)) would create a cyclic binding.
    
    Complexity:
    ----------
    O(n) where n is the size of expressions being unified, assuming
    occur check is performed. Without occur check, O(n) amortized.
    
    Applications:
    ------------
    - Logic programming (Prolog)
    - Type inference
    - Theorem proving
    - Pattern matching in functional languages
    """
    if s is None:
        return None
    elif x == y:
        return s
    elif is_variable(x):
        return unify_var(x, y, s)
    elif is_variable(y):
        return unify_var(y, x, s)
    elif isinstance(x, Expr) and isinstance(y, Expr):
        return unify(x.args, y.args, unify(x.op, y.op, s))
    elif isinstance(x, str) or isinstance(y, str):
        return None
    elif issequence(x) and issequence(y) and len(x) == len(y):
        if not x:
            return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s))
    else:
        return None


def is_variable(x):
    """A variable is an Expr with no args and a lowercase symbol as the op.
    
    Variables are placeholders that can be bound to values during unification.
    They enable expressing general patterns and relationships.
    
    Parameters:
    -----------
    x : any
        Expression to test
        
    Returns:
    --------
    bool
        True if x is a logical variable
        
    Examples:
    ---------
    >>> is_variable(expr('x'))
    True
    >>> is_variable(expr('X'))  # Constant
    False
    >>> is_variable(expr('f(x)'))  # Compound
    False
    
    Design Choice:
    -------------
    Variables must be:
    1. Expr objects (not strings)
    2. Have no arguments (atomic)
    3. Start with lowercase (convention)
    
    This distinguishes variables from constants (uppercase) and
    compound terms (have arguments).
    """
    return isinstance(x, Expr) and not x.args and x.op[0].islower()


def unify_var(var, x, s):
    """Unify variable var with expression x given substitution s.
    
    This handles the special case of unifying a variable, which requires
    checking for existing bindings and preventing cyclic structures.
    
    Parameters:
    -----------
    var : Expr
        A logical variable
    x : any
        Expression to unify with var
    s : dict
        Current substitution
        
    Returns:
    --------
    dict or None
        Extended substitution or None if unification fails
        
    Algorithm:
    ----------
    1. If var already bound, unify its binding with x
    2. If x is a variable bound in s, unify var with its binding
    3. Check for occur check violation
    4. Otherwise, bind var to x
    
    Occur Check:
    -----------
    Prevents bindings like {x: f(x)} which would create infinite
    structures. Essential for soundness of unification.
    
    Examples:
    ---------
    >>> s = {x: John}
    >>> unify_var(y, x, s)  # y unifies with John
    {x: John, y: John}
    >>> unify_var(x, f(x), {})  # Occur check fails
    None
    
    Substitution Composition:
    ------------------------
    When var is already bound, we unify its binding with x,
    implementing substitution composition: (θ ∘ σ)(var) = θ(σ(var))
    """
    if var in s:
        return unify(s[var], x, s)
    elif occur_check(var, x, s):
        return None
    else:
        return extend(s, var, x)


def occur_check(var, x, s):
    """Return true if variable var occurs anywhere in x
    (or in subst(s, x), if s has a binding for x).
    
    The occur check prevents creating cyclic substitutions that would
    represent infinite structures. This is essential for the soundness
    of unification.
    
    Parameters:
    -----------
    var : Expr
        Variable to check for
    x : any
        Expression to search in
    s : dict
        Current substitution
        
    Returns:
    --------
    bool
        True if var occurs in x after substitution
        
    Examples:
    ---------
    >>> occur_check(x, f(x), {})
    True  # Direct occurrence
    >>> occur_check(x, f(y), {y: x})
    True  # Indirect occurrence through substitution
    >>> occur_check(x, f(y), {y: z})
    False # No occurrence
    
    Why Occur Check Matters:
    -----------------------
    Without occur check, unifying x with f(x) would create:
    {x: f(x)} → {x: f(f(x))} → {x: f(f(f(x)))} → ...
    
    This represents an infinite term, which most logic systems
    cannot handle properly.
    
    Performance Note:
    ----------------
    Occur check makes unification O(n) instead of near-linear.
    Some systems (like Prolog) omit it for efficiency, accepting
    the unsoundness risk.
    """
    if var == x:
        return True
    elif is_variable(x) and x in s:
        return occur_check(var, s[x], s)
    elif isinstance(x, Expr):
        return (occur_check(var, x.op, s) or
                occur_check(var, x.args, s))
    elif isinstance(x, (list, tuple)):
        return first(e for e in x if occur_check(var, e, s))
    else:
        return False


def extend(s, var, val):
    """Copy the substitution s and extend it by setting var to val; return copy.
    
    Substitutions are extended immutably to support backtracking in search
    algorithms. This creates a new substitution rather than modifying the existing one.
    
    Parameters:
    -----------
    s : dict
        Original substitution
    var : Expr
        Variable to bind
    val : any
        Value to bind to var
        
    Returns:
    --------
    dict
        New substitution with added binding
        
    Example:
    --------
    >>> s1 = {x: John}
    >>> s2 = extend(s1, y, Mary)
    >>> s2
    {x: John, y: Mary}
    >>> s1  # Original unchanged
    {x: John}
    
    Immutability Rationale:
    ----------------------
    Backtracking search algorithms need to try different bindings.
    Immutable substitutions allow easy backtracking without explicit
    undo operations.
    
    Design Alternative:
    ------------------
    Some systems use mutable substitutions with explicit trailing
    for efficiency, trading simplicity for performance.
    """
    s2 = s.copy()
    s2[var] = val
    return s2


def subst(s, x):
    """Substitute the substitution s into the expression x.
    
    Apply a substitution by replacing all variables in x with their
    values from s. This implements the mathematical operation xσ where
    σ is the substitution.
    
    Parameters:
    -----------
    s : dict
        Substitution mapping variables to values
    x : Expr, list, tuple, or other
        Expression to apply substitution to
        
    Returns:
    --------
    same type as x
        Result of applying substitution
        
    Examples:
    ---------
    >>> subst({x: 42, y:0}, F(x) + y)
    (F(42) + 0)
    >>> subst({x: John, y: Mary}, Loves(x, y))
    Loves(John, Mary)
    >>> subst({x: y, y: x}, P(x, y))  # Simultaneous substitution
    P(y, x)
    
    Recursive Application:
    ---------------------
    The substitution is applied recursively through the entire
    structure, replacing variables at any depth.
    
    Lists and Tuples:
    ----------------
    The function preserves the type of sequences, returning
    a list for list input and tuple for tuple input.
    
    Non-Variables:
    -------------
    Constants and non-Expr values are returned unchanged, as
    they cannot be substituted.
    """
    if isinstance(x, list):
        return [subst(s, xi) for xi in x]
    elif isinstance(x, tuple):
        return tuple([subst(s, xi) for xi in x])
    elif not isinstance(x, Expr):
        return x
    elif is_var_symbol(x.op):
        return s.get(x, x)
    else:
        return Expr(x.op, *[subst(s, arg) for arg in x.args])


def fol_fc_ask(KB, alpha):
    """Forward chaining for first-order logic. [Not implemented in the code]
    
    Forward chaining in FOL is more complex than in propositional logic
    because it must handle variables and unification.
    
    Theoretical Overview:
    --------------------
    FOL forward chaining:
    1. Start with known facts
    2. Find rules whose premises unify with known facts
    3. Apply substitutions to derive new facts
    4. Continue until query is derived or no progress
    
    Challenges:
    ----------
    - Infinite derivations possible (e.g., from P(x) => P(f(x)))
    - Multiple unifications for same rule
    - Efficiency requires indexing and subsumption checking
    
    Why Not Implemented:
    -------------------
    The textbook focuses on backward chaining for FOL, which is
    goal-directed and often more efficient for query answering.
    """
    raise NotImplementedError


def standardize_variables(sentence, dic=None):
    """Replace all the variables in sentence with new variables.
    
    Variable standardization ensures that variables in different
    clauses don't accidentally unify. This is essential when
    combining clauses during inference.
    
    Parameters:
    -----------
    sentence : Expr
        Expression potentially containing variables
    dic : dict, optional
        Mapping of old variables to new ones
        
    Returns:
    --------
    Expr
        Expression with standardized variables
        
    Examples:
    ---------
    >>> standardize_variables(expr('P(x) & Q(x)'))
    P(v_0) & Q(v_0)  # Same variable mapped consistently
    >>> standardize_variables(expr('P(x)'))
    P(v_1)  # Next call gets fresh variables
    
    Algorithm:
    ----------
    1. Maintain mapping of seen variables
    2. For each new variable, generate fresh name
    3. Apply mapping consistently throughout expression
    
    Use in Inference:
    ----------------
    Before using a rule in backward chaining, we standardize its
    variables to avoid conflicts with query variables.
    
    Example Problem:
    ---------------
    Query: P(x)
    Rule: P(x) => Q(x)
    Without standardization, the x's would unify incorrectly.
    
    Implementation Detail:
    ---------------------
    Uses a counter to generate unique variable names v_0, v_1, ...
    The counter is shared across calls to ensure global uniqueness.
    """
    if dic is None:
        dic = {}
    if not isinstance(sentence, Expr):
        return sentence
    elif is_var_symbol(sentence.op):
        if sentence in dic:
            return dic[sentence]
        else:
            v = Expr('v_{}'.format(next(standardize_variables.counter)))
            dic[sentence] = v
            return v
    else:
        return Expr(sentence.op,
                    *[standardize_variables(a, dic) for a in sentence.args])

standardize_variables.counter = itertools.count()

# ______________________________________________________________________________


class FolKB(KB):
    """A knowledge base consisting of first-order definite clauses.
    
    First-order logic extends propositional logic with variables, quantifiers,
    and predicates. This KB implementation focuses on definite clauses for
    efficient backward chaining inference.
    
    Definite Clauses in FOL:
    -----------------------
    - Atomic: Father(John, Mary)
    - Rule: Parent(x,y) & Parent(y,z) => Grandparent(x,z)
    - No negations in premises, single positive consequent
    
    Storage Format:
    --------------
    Clauses stored in implication form, not CNF. This preserves the
    natural structure for backward chaining.
    
    Examples:
    ---------
    >>> kb0 = FolKB([expr('Farmer(Mac)'), expr('Rabbit(Pete)'),
    ...              expr('(Rabbit(r) & Farmer(f)) ==> Hates(f, r)')])
    >>> kb0.tell(expr('Rabbit(Flopsie)'))
    >>> kb0.retract(expr('Rabbit(Pete)'))
    >>> kb0.ask(expr('Hates(Mac, x)'))[x]
    Flopsie
    >>> kb0.ask(expr('Wife(Pete, x)'))
    False
    
    Limitations:
    -----------
    - Only handles definite clauses
    - No existential quantifiers
    - No equality reasoning
    - No function symbols in current implementation
    
    Real FOL Systems:
    ----------------
    Production systems like Prolog include:
    - Negation as failure
    - Cut operator for efficiency
    - Built-in arithmetic
    - Constraint solving
    """

    def __init__(self, initial_clauses=[]):
        """Initialize a first-order logic KB.
        
        Parameters:
        -----------
        initial_clauses : list of Expr
            Initial facts and rules in definite clause form
            
        Example:
        --------
        >>> kb = FolKB([
        ...     expr('Man(Socrates)'),
        ...     expr('Man(x) ==> Mortal(x)')
        ... ])
        """
        self.clauses = []  # inefficient: no indexing
        for clause in initial_clauses:
            self.tell(clause)

    def tell(self, sentence):
        """Add a definite clause to the KB.
        
        Parameters:
        -----------
        sentence : Expr
            Must be a definite clause (fact or rule)
            
        Raises:
        -------
        Exception
            If sentence is not a definite clause
            
        Valid Forms:
        -----------
        - Fact: Brother(John, Jim)
        - Rule: Sister(x,y) & Parent(y,z) => Aunt(x,z)
        
        Invalid Forms:
        -------------
        - Negated atoms: ~Brother(x,y)
        - Disjunctions: Brother(x,y) | Sister(x,y)
        - Multiple consequents: P(x) => Q(x) & R(x)
        """
        if is_definite_clause(sentence):
            self.clauses.append(sentence)
        else:
            raise Exception("Not a definite clause: {}".format(sentence))

    def ask_generator(self, query):
        """Generate all substitutions that make query true.
        
        Uses backward chaining (fol_bc_ask) to find all ways to
        prove the query from the KB.
        
        Parameters:
        -----------
        query : Expr
            An atomic query, possibly with variables
            
        Yields:
        -------
        dict
            Each substitution that satisfies query
            
        Example:
        --------
        >>> kb = FolKB()
        >>> kb.tell(expr('Parent(John, Mary)'))
        >>> kb.tell(expr('Parent(John, Tom)'))
        >>> list(kb.ask_generator(expr('Parent(John, x)')))
        [{x: Mary}, {x: Tom}]
        """
        return fol_bc_ask(self, query)

    def retract(self, sentence):
        """Remove a sentence from the KB.
        
        Note: Doesn't retract derived consequences. Full truth
        maintenance would track derivations.
        """
        self.clauses.remove(sentence)

    def fetch_rules_for_goal(self, goal):
        """Return rules that might help prove goal.
        
        In a production implementation, this would use indexing
        for efficient retrieval. Here we just return all clauses.
        
        Parameters:
        -----------
        goal : Expr
            The goal to prove
            
        Returns:
        --------
        list
            All clauses (rules and facts)
            
        Optimization Opportunity:
        ------------------------
        Real systems index by predicate symbol for O(1) retrieval:
        - If goal is P(x,y), only fetch rules with P in consequent
        - Use discrimination trees for pattern indexing
        """
        return self.clauses


def fol_bc_ask(KB, query):
    """A simple backward-chaining algorithm for first-order logic. [Figure 9.6]
    KB should be an instance of FolKB, and query an atomic sentence.
    
    Backward chaining is a goal-directed inference method that works
    backwards from the query to find supporting facts.
    
    Parameters:
    -----------
    KB : FolKB
        Knowledge base of definite clauses
    query : Expr
        Atomic query to prove
        
    Yields:
    -------
    dict
        Each substitution that makes query true
        
    Algorithm Overview:
    ------------------
    1. Find rules whose consequent unifies with query
    2. For each such rule, try to prove all antecedents
    3. Propagate bindings through recursive calls
    4. Yield successful substitutions
    
    Example Trace:
    -------------
    Query: Grandparent(x, Mary)
    Rules: Parent(x,y) & Parent(y,z) => Grandparent(x,z)
    Facts: Parent(John, Sue), Parent(Sue, Mary)
    
    1. Unify Grandparent(x,Mary) with Grandparent(x,z): {z: Mary}
    2. Prove Parent(x,y) & Parent(y,Mary)
    3. Find Parent(Sue,Mary), bind {y: Sue}
    4. Prove Parent(x,Sue)
    5. Find Parent(John,Sue), bind {x: John}
    6. Yield {x: John, y: Sue, z: Mary}
    
    Completeness:
    ------------
    Complete for definite clause KBs (will find all answers).
    May not terminate with recursive rules like P(x) => P(f(x)).
    """
    return fol_bc_or(KB, query, {})


def fol_bc_or(KB, goal, theta):
    """Backward chaining OR: find any rule that proves goal.
    
    Try each rule in KB that might prove the goal. For each rule
    whose consequent unifies with goal, try to prove all antecedents.
    
    Parameters:
    -----------
    KB : FolKB
        Knowledge base
    goal : Expr
        Current goal to prove
    theta : dict
        Substitution built so far
        
    Yields:
    -------
    dict
        Each extended substitution that proves goal
        
    OR Node Logic:
    -------------
    To prove goal, we need to find ANY rule that works:
    - Rule 1 might prove it one way
    - Rule 2 might prove it another way
    - A fact might prove it directly
    
    Variable Standardization:
    ------------------------
    Each rule gets fresh variables to avoid conflicts between
    different rule applications or with query variables.
    """
    for rule in KB.fetch_rules_for_goal(goal):
        lhs, rhs = parse_definite_clause(standardize_variables(rule))
        for theta1 in fol_bc_and(KB, lhs, unify(rhs, goal, theta)):
            yield theta1


def fol_bc_and(KB, goals, theta):
    """Backward chaining AND: prove all goals in the list.
    
    Recursively prove each goal in sequence, propagating bindings
    from earlier goals to later ones.
    
    Parameters:
    -----------
    KB : FolKB
        Knowledge base  
    goals : list
        List of goals to prove
    theta : dict
        Current substitution
        
    Yields:
    -------
    dict
        Each substitution that proves all goals
        
    AND Node Logic:
    --------------
    To prove [G1, G2, ..., Gn], we must:
    1. Prove G1 with substitution θ₁
    2. Prove G2 with θ₁ applied, getting θ₂
    3. Continue through all goals
    4. Yield final substitution if all succeed
    
    Substitution Propagation:
    ------------------------
    Critical: apply current substitution before proving each goal.
    If G1 binds {x: John}, then P(x) in G2 becomes P(John).
    
    Base Case:
    ---------
    Empty goal list means success - yield current substitution.
    """
    if theta is None:
        pass
    elif not goals:
        yield theta
    else:
        first, rest = goals[0], goals[1:]
        for theta1 in fol_bc_or(KB, subst(theta, first), theta):
            for theta2 in fol_bc_and(KB, rest, theta1):
                yield theta2

# ______________________________________________________________________________

# Example application (not in the book).
# You can use the Expr class to do symbolic differentiation.  This used to be
# a part of AI; now it is considered a separate field, Symbolic Algebra.


def diff(y, x):
    """Return the symbolic derivative, dy/dx, as an Expr.
    However, you probably want to simplify the results with simp.
    
    Symbolic differentiation demonstrates how AI techniques can be applied
    to mathematical reasoning. The same expression tree representation used
    for logic also works for calculus.
    
    Parameters:
    -----------
    y : Expr
        Expression to differentiate
    x : Expr
        Variable to differentiate with respect to
        
    Returns:
    --------
    Expr
        The derivative dy/dx
        
    Examples:
    ---------
    >>> diff(x * x, x)
    ((x * 1) + (x * 1))
    >>> simp(diff(x * x, x))
    (2 * x)
    >>> diff(x ** 3, x)
    ((3 * (x ** 2)) * 1)
    
    Differentiation Rules:
    ---------------------
    - d/dx(c) = 0 (constant)
    - d/dx(x) = 1 (variable)
    - d/dx(u + v) = du/dx + dv/dx (sum)
    - d/dx(u * v) = u * dv/dx + v * du/dx (product)
    - d/dx(u / v) = (v * du/dx - u * dv/dx) / v²
    - d/dx(u ** n) = n * u^(n-1) * du/dx (power)
    - d/dx(log(u)) = du/dx / u (logarithm)
    
    Chain Rule:
    ----------
    Implicitly applied through recursive calls. For f(g(x)),
    we get f'(g(x)) * g'(x).
    
    Symbolic vs Numeric:
    -------------------
    This returns symbolic expressions, not numeric values.
    Preserves exact mathematical relationships without
    floating-point errors.
    
    Historical Note:
    ---------------
    Symbolic math was once considered AI because it requires
    rule-based reasoning. Systems like Mathematica and Maple
    evolved from this AI research.
    """
    if y == x:
        return 1
    elif not y.args:
        return 0
    else:
        u, op, v = y.args[0], y.op, y.args[-1]
        if op == '+':
            return diff(u, x) + diff(v, x)
        elif op == '-' and len(y.args) == 1:
            return -diff(u, x)
        elif op == '-':
            return diff(u, x) - diff(v, x)
        elif op == '*':
            return u * diff(v, x) + v * diff(u, x)
        elif op == '/':
            return (v * diff(u, x) - u * diff(v, x)) / (v * v)
        elif op == '**' and isnumber(x.op):
            return (v * u ** (v - 1) * diff(u, x))
        elif op == '**':
            return (v * u ** (v - 1) * diff(u, x) +
                    u ** v * Expr('log')(u) * diff(v, x))
        elif op == 'log':
            return diff(u, x) / u
        else:
            raise ValueError("Unknown op: {} in diff({}, {})".format(op, y, x))

def simp(x):
   """Simplify the expression x.
   
   Apply algebraic identities to reduce expressions to simpler equivalent
   forms. This is essential for symbolic math to avoid exponentially
   growing expressions.
   
   Parameters:
   -----------
   x : Expr or number
       Expression to simplify
       
   Returns:
   --------
   Expr or number
       Simplified expression
       
   Simplification Rules:
   --------------------
   Additive identity: x + 0 = 0 + x = x
   Multiplicative identity: x * 1 = 1 * x = x
   Additive inverse: x - x = 0
   Multiplicative zero: x * 0 = 0 * x = 0
   Double negative: --x = x
   Powers: x^0 = 1, x^1 = x, 0^n = 0 (n>0)
   Division: x/x = 1, 0/x = 0, x/0 = Undefined
   Logarithm: log(1) = 0
   
   Examples:
   ---------
   >>> simp(x + 0)
   x
   >>> simp(x * 1)
   x
   >>> simp(x * x * 0)
   0
   >>> simp((x + 1) - (x + 1))
   0
   
   Algorithm:
   ----------
   1. Recursively simplify subexpressions
   2. Apply operator-specific simplification rules
   3. Return simplified result
   
   Limitations:
   -----------
   - Only applies basic identities
   - No factoring or expansion
   - No trigonometric identities
   - No collection of like terms
   
   Real Systems:
   ------------
   Computer algebra systems like Mathematica use:
   - Pattern matching for complex rules
   - Canonical forms for expressions
   - Gröbner bases for polynomial systems
   - Heuristics for simplification order
   
   Use with diff():
   ---------------
   Differentiation often creates complex expressions.
   Always simplify after differentiating:
   >>> d(x * x, x)  # Returns ((x * 1) + (x * 1))
   >>> simp(d(x * x, x))  # Returns (2 * x)
   """
   if isnumber(x) or not x.args:
       return x
   args = list(map(simp, x.args))
   u, op, v = args[0], x.op, args[-1]
   if op == '+':
       if v == 0:
           return u
       if u == 0:
           return v
       if u == v:
           return 2 * u
       if u == -v or v == -u:
           return 0
   elif op == '-' and len(args) == 1:
       if u.op == '-' and len(u.args) == 1:
           return u.args[0]  # --y ==> y
   elif op == '-':
       if v == 0:
           return u
       if u == 0:
           return -v
       if u == v:
           return 0
       if u == -v or v == -u:
           return 0
   elif op == '*':
       if u == 0 or v == 0:
           return 0
       if u == 1:
           return v
       if v == 1:
           return u
       if u == v:
           return u ** 2
   elif op == '/':
       if u == 0:
           return 0
       if v == 0:
           return Expr('Undefined')
       if u == v:
           return 1
       if u == -v or v == -u:
           return 0
   elif op == '**':
       if u == 0:
           return 0
       if v == 0:
           return 1
       if u == 1:
           return 1
       if v == 1:
           return u
   elif op == 'log':
       if u == 1:
           return 0
   else:
       raise ValueError("Unknown op: " + op)
   # If we fall through to here, we can not simplify further
   return Expr(op, *args)


def d(y, x):
   """Differentiate and then simplify.
   
   Convenience function that combines differentiation and simplification.
   This is the typical workflow for symbolic calculus.
   
   Parameters:
   -----------
   y : Expr
       Expression to differentiate
   x : Expr
       Variable to differentiate with respect to
       
   Returns:
   --------
   Expr
       Simplified derivative
       
   Examples:
   ---------
   >>> d(x * x, x)
   (2 * x)
   >>> d(x ** 3 + 2 * x, x)
   ((3 * (x ** 2)) + 2)
   >>> d(Expr('sin')(x), x)  # Would need trig rules
   Raises ValueError (sin not implemented)
   
   Why Both Steps?
   --------------
   diff() returns mathematically correct but verbose results.
   simp() reduces these to human-readable form.
   
   Performance:
   -----------
   Simplification after each operation prevents expression
   explosion in complex calculations.
   """
   return simp(diff(y, x))