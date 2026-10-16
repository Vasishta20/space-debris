import json, sys, unittest
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.orbit import is_candidate, parse_tle_text, utc_window

ROOT=Path(__file__).resolve().parents[1]
class OrbitTests(unittest.TestCase):
    def test_candidate_threshold_and_units(self):
        self.assertTrue(is_candidate(0.0,50.0)); self.assertTrue(is_candidate(50.0,50.0)); self.assertFalse(is_candidate(50.0001,50.0)); self.assertFalse(is_candidate(-1,50.0))
    def test_fixed_utc_window(self):
        start=datetime(2026,10,14,5,50,tzinfo=timezone.utc); epochs=utc_window(start,7,10)
        self.assertEqual(epochs[0].isoformat(),'2026-10-14T05:50:00+00:00'); self.assertEqual((epochs[-1]-epochs[0]).total_seconds(),3600)
    def test_candidate_identity_and_source_tles(self):
        result=json.loads((ROOT/'data'/'screening.json').read_text(encoding='utf-8'))
        self.assertEqual(result['reference_epoch_utc'],'2026-10-14T05:50:00Z'); self.assertEqual(result['step_minutes'],10); self.assertEqual(result['coordinate_frame'],'TEME')
        records=parse_tle_text((ROOT/'data'/'starlink.tle').read_text(encoding='utf-8'),60); by_id={r['norad_id']:r for r in records}
        for candidate in result['candidates']:
            self.assertIn(candidate['norad_a'],by_id); self.assertIn(candidate['norad_b'],by_id)
            self.assertEqual(candidate['tle_a_line1'],by_id[candidate['norad_a']]['line1']); self.assertEqual(candidate['tle_b_line2'],by_id[candidate['norad_b']]['line2'])
            self.assertGreaterEqual(candidate['distance_km'],0); self.assertLessEqual(candidate['distance_km'],result['threshold_km']); self.assertGreaterEqual(candidate['relative_velocity_km_s'],0)

if __name__ == '__main__': unittest.main()
