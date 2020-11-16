import unittest

from totalopenstation.formats import Feature, Point
from totalopenstation.output.tops_landxml import OutputFormat

class TestLandXMLOutput(unittest.TestCase):

    def setUp(self):
        self.data = [
            Feature(Point(12.8, 76.3, 56.2),
                    desc='PT',
                    point_name='TEST POINT',
                    id=1),
            Feature(Point(19.8, 26.3, 46.2),
                    desc='PT',
                    point_name='TEST POINT #2',
                    id=2),
            Feature(Point(7189.8, 5719.7, 972.6),
                    desc='ST',
                    id=3,
                    point_name='STATION',
                    ih=1.5),
            Feature(Point(6385.4, 4201.6, 943.1),
                    desc='PO',
                    id=4,
                    point_name='TEST POINT #3',
                    angle=0,
                    z_angle=90.585,
                    slope_dist=1718.28,
                    th=1.5,
                    station_name="STATION")
        ]

    def test_output(self):
        self.output = OutputFormat(self.data).process()
        self.assertEqual(self.output.splitlines()[9], b'\t\t\t<CgPoint name="TEST POINT">12.8 76.3 56.2</CgPoint>')
        self.assertEqual(self.output.splitlines()[10], b'\t\t\t<CgPoint name="TEST POINT #2">19.8 26.3 46.2</CgPoint>')
        self.assertEqual(self.output.splitlines()[12], b'\t\t<InstrumentSetup id="setup0" stationName="STATION" instrumentHeight="1.5">')
        self.assertEqual(self.output.splitlines()[16], b'\t\t\t<RawObservation targetHeight="1.5" horizAngle="0" zenithAngle="90.585" slopeDistance="1718.28">')
        self.assertEqual(self.output.splitlines()[17], b'\t\t\t\t<TargetPoint desc="TEST POINT #3">6385.4 4201.6 943.1</TargetPoint>')
