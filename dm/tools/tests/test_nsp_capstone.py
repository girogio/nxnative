"""Check the disassembler API before building or surveying a game."""
import importlib.util
from pathlib import Path
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location('nsp_capstone', Path(__file__).resolve().parents[3] / 'scripts/build_ipa_from_nsp.py')
assert spec is not None and spec.loader is not None
nsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nsp)


class CapstoneVersion(unittest.TestCase):
    def test_supported_api(self):
        with mock.patch('capstone.cs_version', return_value=(5, 0, 1280)):
            nsp.check_capstone()

    def test_unsupported_api_has_install_command(self):
        for major in (4, 6):
            with self.subTest(major=major), mock.patch('capstone.cs_version', return_value=(major, 0, major << 8)):
                with self.assertRaisesRegex(nsp.BuildError, 'pip install .*capstone>=5,<6'):
                    nsp.check_capstone()


if __name__ == '__main__':
    unittest.main()
