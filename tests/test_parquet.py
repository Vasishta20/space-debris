import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ParquetTests(unittest.TestCase):
    def test_bounded_roundtrip_evidence(self):
        result=json.loads((ROOT/'data'/'satcat_clean.json').read_text(encoding='utf-8'))
        self.assertEqual(result['rows_written'],68129); self.assertEqual(result['rows_read'],68129); self.assertTrue(result['schema_valid']); self.assertEqual(result['format'],'parquet')
        self.assertTrue((ROOT/'data'/'satcat_clean.parquet').exists())
