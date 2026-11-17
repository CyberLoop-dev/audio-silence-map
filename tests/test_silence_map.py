import tempfile,unittest,wave
from pathlib import Path
from silence_map import analyze_wav

class SilenceTests(unittest.TestCase):
    def test_detects_middle_silence(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"sample.wav"
            with wave.open(str(path),"wb") as wav:
                wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(1000)
                wav.writeframes(b"\xff\x3f"*1000+b"\x00\x00"*600+b"\xff\x3f"*1000)
            found=analyze_wav(path,-35,100,0.3)
            self.assertEqual(len(found),1)
            self.assertAlmostEqual(found[0]["duration"],0.6,places=2)

    def test_rejects_bad_window(self):
        with self.assertRaises(ValueError): analyze_wav(Path("unused"),-42,0,0.4)

if __name__=="__main__": unittest.main()
