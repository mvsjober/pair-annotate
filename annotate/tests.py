from django.test import TestCase

from annotate.pmatrix import PMatrix
import numpy as np

class AnnotateTests(TestCase):
    def test_pmatrix_bad_input(self):
        s = 2
        pm = PMatrix(s)

        with self.assertRaises(AssertionError):
            ids = [42, 92, 20]
            pm.init_randomly(ids)

        with self.assertRaises(AssertionError):
            ids = [42, 92, 92, 1]
            pm.init_randomly(ids)

        with self.assertRaises(AssertionError):
            ids = [42, 92, 92, 1]
            pm.init_spiral([0.1, 0.2, 0.3, 0.4], ids)

    def test_pmatrix_random(self):
        s = 4
        pm = PMatrix(s)

        ids = [  1,  3,  5,  7,  
                 9, 11, 13, 15, 
                17, 19, 21, 23, 
                25, 27, 29, 31]

        pm.init_randomly(ids)

        self.assertEqual(pm.p.shape, (s, s))

        for row in pm.p:
            for x in row:
                self.assertTrue(x in ids)

        for x in ids:
            self.assertTrue(x in pm.p)
        
        # not strictly true test :-)
        self.assertFalse((pm.p == np.sort(pm.p)).all(), 'P not "random"')

        pairs = pm.generate_pairs()
        self.assert_pairs_ok(pairs, ids)

    def test_pmatrix_spiral(self):
        for s in range(1,10):
            pm = PMatrix(s)

            ids = np.arange(1,s*s+1)

            np.random.shuffle(ids)
            p = ids*0.42

            pm.init_spiral(p, ids)

            self.assertEquals(pm.p.shape, (s,s))

            for row in pm.p:
                for x in row:
                    self.assertTrue(x in ids)

            for x in ids:
                self.assertTrue(x in pm.p)

            print('P (spiral) = \n', pm, '\n')

            pairs = pm.generate_pairs()
            self.assert_pairs_ok(pairs, ids)

    def assert_pairs_ok(self, pairs, ids):
        t = len(ids)
        s = int(np.sqrt(t))
        self.assertEquals(t*(s-1), len(pairs))

        for i in ids:
            count = len([p for p in pairs if i in p])
            
            self.assertEquals(count, (s-1)*2)
