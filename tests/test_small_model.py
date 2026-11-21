import unittest
import torch

from small_model.model import NovaTiny
from small_model.data import split_data


class NovaTinyTests(unittest.TestCase):
    def test_forward_shape(self):
        model = NovaTiny()
        x = torch.randint(0, 256, (2, 16))
        logits, hidden = model(x)
        self.assertEqual(tuple(logits.shape), (2, 16, 256))
        self.assertEqual(tuple(hidden.shape), (4, 2, 128))

    def test_parameter_count_is_small(self):
        model = NovaTiny()
        self.assertLess(model.parameter_count(), 1_000_000)
        self.assertGreater(model.parameter_count(), 100_000)

    def test_train_validation_split(self):
        data = torch.arange(100)
        train, val = split_data(data, 0.8)
        self.assertEqual(len(train), 80)
        self.assertEqual(len(val), 20)
        self.assertEqual(train[-1].item(), 79)
        self.assertEqual(val[0].item(), 80)


if __name__ == "__main__":
    unittest.main()
