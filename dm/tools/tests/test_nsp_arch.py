"""Reject AArch32 before the packing script reads ELF64 symbols or rewrites code."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

REPO = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('nsp_arch', REPO / 'scripts/build_ipa_from_nsp.py')
nsp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nsp)


class Architecture(unittest.TestCase):
    def test_npdm_execution_bit_is_independent_of_address_space(self):
        with tempfile.TemporaryDirectory() as tmp:
            exefs = Path(tmp)
            for flags in (0, 2, 4, 6, 1, 3, 5, 7):
                with self.subTest(flags=flags):
                    header = bytearray(0x80)
                    header[:4] = b'META'
                    header[0xc] = flags
                    (exefs / 'main.npdm').write_bytes(header)
                    if flags & 1:
                        nsp.require_aarch64(exefs)
                    else:
                        with self.assertRaisesRegex(nsp.BuildError, '32-bit ARM'):
                            nsp.require_aarch64(exefs)

    def test_missing_and_invalid_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            exefs = Path(tmp)
            nsp.require_aarch64(exefs)
            for data in (b'META', bytes(0x80)):
                (exefs / 'main.npdm').write_bytes(data)
                with self.assertRaisesRegex(nsp.BuildError, 'invalid NPDM'):
                    nsp.require_aarch64(exefs)

    def test_cli_reports_unsupported_architecture_without_traceback(self):
        with mock.patch.object(nsp, 'main', side_effect=nsp.BuildError('32-bit ARM')), \
             mock.patch.object(nsp, 'PROG') as progress:
            self.assertEqual(nsp.cli([]), 1)
            progress.say.assert_called_with('[RED] 32-bit ARM')


if __name__ == '__main__':
    unittest.main()
