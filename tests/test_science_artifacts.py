import csv, json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sgp4.api import Satrec, jday

ROOT=Path(__file__).resolve().parents[1]
class ScienceArtifactTests(unittest.TestCase):
    def test_ingested_catalog_schema_and_count(self):
        with open(r'D:\Projects\space-debris-collision-risk\data\raw\satcat_clean.csv', newline='', encoding='utf-8') as f:
            reader=csv.DictReader(f); self.assertTrue({'NORAD_CAT_ID','OBJECT_TYPE','APOGEE','PERIGEE'}.issubset(reader.fieldnames or [])); self.assertEqual(sum(1 for _ in reader),68129)
    def test_tle_propagates_without_error(self):
        lines=(ROOT/'data'/'starlink.tle').read_text(encoding='utf-8').splitlines(); self.assertGreaterEqual(len(lines),3)
        sat=Satrec.twoline2rv(lines[1],lines[2]); jd,fr=jday(2026,10,13,0,0,0); error,position,velocity=sat.sgp4(jd,fr)
        self.assertEqual(error,0); self.assertEqual(len(position),3); self.assertEqual(len(velocity),3)
    def test_screening_evidence_is_not_a_collision_label(self):
        result=json.loads((ROOT/'data'/'screening.json').read_text(encoding='utf-8'))
        self.assertEqual(result['objects'],60); self.assertEqual(result['samples'],7); self.assertIn('threshold_km',result)

if __name__ == '__main__': unittest.main()
