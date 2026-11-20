import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from pipeline_diagnostics import summarize,instrument


class PipelineTest(unittest.TestCase):
    def test_source_to_present_and_analysis_are_separate(self):
        result=summarize(['MAODIAG A sample=800 sequence=1 ns=1010000000 ms=4.0',
            'MAODIAG P sequence=1 ns=1020000000 ms=1.0'],{800:1000000000})
        self.assertEqual(result['source_to_present_ms']['max'],20)
        self.assertEqual(result['analysis_ms']['p99'],4)
        self.assertIsNone(result['physical_capture_latency_ms'])
        self.assertIsNone(result['audio_dropped_windows'])

    def test_first_presentation_wins_and_missing_frames_are_counted(self):
        result=summarize(['MAODIAG A sample=800 sequence=1 ns=1010000000 ms=4',
            'MAODIAG A sample=1600 sequence=2 ns=1060000000 ms=5',
            'MAODIAG P sequence=2 ns=1070000000 ms=1',
            'MAODIAG P sequence=2 ns=1080000000 ms=1'],{800:1000000000,1600:1050000000})
        self.assertEqual(result['source_to_present_ms']['max'],20)
        self.assertEqual(result['unpresented_analysis_frames'],1)

    def test_no_data_future_clocks_and_invalid_durations_fail(self):
        for lines in ([],['MAODIAG A sample=800 sequence=1 ns=900000000 ms=4'],
                ['MAODIAG A sample=800 sequence=1 ns=1010000000 ms=nan']):
            with self.assertRaises(ValueError): summarize(lines,{800:1000000000})

    def test_intentional_idle_skip_is_not_an_unaccounted_hop(self):
        result=summarize(['MAODIAG S sample=800','MAODIAG A sample=1600 sequence=1 ns=1060000000 ms=4',
            'MAODIAG P sequence=1 ns=1070000000 ms=1'],{800:1000000000,1600:1050000000})
        self.assertEqual(result['intentional_idle_hops'],1)
        self.assertEqual(result['controlled_stream_hop_gaps'],0)

    def test_workspace_idle_invalidation_is_preserved_by_probe(self):
        source='\t\tif (skip) {\n\t\t\tengine_.invalidate_audio_history();\n\t\t\treturn false;\n\t\t}\n'
        source+='\t\tsnapshot_ = engine_.analyze(window_.data(), window_samples_, settings_, source_name_.c_str(), 0);\n'
        source+='\t\tif (should_present) {\n\t\t\tpresent(&session, visualizer);\n'
        result=instrument(source)
        self.assertEqual(result.count('MAODIAG S'),1)
        self.assertIn('engine_.invalidate_audio_history();',result)


if __name__=='__main__': unittest.main()
