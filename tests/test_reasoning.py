import unittest
from nova_core.reasoning import IndependentReasoner, Rule

class IndependentReasonerTests(unittest.TestCase):
    def test_transitive_inference(self):
        engine = IndependentReasoner()
        engine.add_fact(("parent", "Arun", "Maya"))
        engine.add_fact(("parent", "Maya", "Ravi"))
        engine.add_rule(Rule("grandparent", (
            ("parent", "?x", "?y"), ("parent", "?y", "?z")
        ), ("grandparent", "?x", "?z")))
        result = engine.infer()
        self.assertIn(("grandparent", "Arun", "Ravi"), result.derived)
        self.assertTrue(result.saturated)

    def test_recursive_multi_hop_inference(self):
        engine = IndependentReasoner()
        for fact in (("parent","A","B"),("parent","B","C"),("parent","C","D")):
            engine.add_fact(fact)
        engine.add_rule(Rule("ancestor_step", (("parent","?x","?y"),),
                             ("ancestor","?x","?y")))
        engine.add_rule(Rule("ancestor_recursive", (
            ("ancestor","?x","?y"),("parent","?y","?z")
        ), ("ancestor","?x","?z")))
        self.assertIn(("ancestor","A","D"), engine.infer().facts)

    def test_query_bindings(self):
        engine = IndependentReasoner()
        engine.add_fact(("likes","Meena","Tea"))
        self.assertEqual(engine.query(("likes","?person","?subject")),
                         ({"?person":"Meena","?subject":"Tea"},))

    def test_repeated_variable_must_match(self):
        engine = IndependentReasoner()
        engine.add_fact(("same","A","B"))
        engine.add_fact(("same","A","A"))
        self.assertEqual(engine.query(("same","?x","?x")), ({"?x":"A"},))

    def test_deterministic_results(self):
        def run():
            engine = IndependentReasoner()
            engine.add_fact(("edge","b","c"))
            engine.add_fact(("edge","a","b"))
            engine.add_rule(Rule("path", (
                ("edge","?x","?y"),("edge","?y","?z")
            ), ("path","?x","?z")))
            return engine.infer()
        self.assertEqual(run(), run())

    def test_proof_trace(self):
        engine = IndependentReasoner()
        engine.add_fact(("human","Arun"))
        engine.add_rule(Rule("mortality", (("human","?x"),), ("mortal","?x")))
        result = engine.infer()
        step = next(x for x in result.proof if x.fact == ("mortal","Arun"))
        self.assertEqual(step.rule_name, "mortality")
        self.assertEqual(step.premises, (("human","Arun"),))

    def test_multiword_string_is_opaque(self):
        engine = IndependentReasoner()
        engine.add_fact(("phrase","a whole English phrase"))
        self.assertEqual(engine.query(("phrase","?whole")),
                         ({"?whole":"a whole English phrase"},))

    def test_fact_limit(self):
        engine = IndependentReasoner(max_facts=1)
        engine.add_fact(("a","1"))
        with self.assertRaises(RuntimeError):
            engine.add_fact(("a","2"))

    def test_round_limit_is_reported(self):
        engine = IndependentReasoner(max_rounds=1)
        engine.add_fact(("parent","A","B"))
        engine.add_fact(("parent","B","C"))
        engine.add_rule(Rule("step", (("parent","?x","?y"),), ("ancestor","?x","?y")))
        engine.add_rule(Rule("recursive", (
            ("ancestor","?x","?y"),("parent","?y","?z")
        ), ("ancestor","?x","?z")))
        self.assertFalse(engine.infer().saturated)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Rule("bad", (), ("x","y"))
        with self.assertRaises(ValueError):
            IndependentReasoner().add_fact(("", "value"))

if __name__ == "__main__":
    unittest.main()
