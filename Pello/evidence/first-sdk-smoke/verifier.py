import importlib.util, pathlib, sys, unittest
spec = importlib.util.spec_from_file_location('pello_probe', pathlib.Path(sys.argv[1]))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class ProbeTests(unittest.TestCase):
    def test_positive(self): self.assertEqual(module.add(2, 3), 5)
    def test_negative(self): self.assertEqual(module.add(-8, 3), -5)
    def test_zero(self): self.assertEqual(module.add(0, 0), 0)
    def test_float(self): self.assertAlmostEqual(module.add(0.1, 0.2), 0.3)
    def test_large(self): self.assertEqual(module.add(10**40, 1), 10**40 + 1)
    def test_unchanged_arguments(self):
        values = [1]; self.assertEqual(module.add(values, [2]), [1, 2]); self.assertEqual(values, [1])
unittest.main(argv=['probe'], verbosity=2)
