"""Linux CPU accounting regression: subsecond work must not look idle."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock
import os

SCRIPT=Path(__file__).resolve().parents[1]/'scripts/run_watched.py'
spec=importlib.util.spec_from_file_location('watched_linux',SCRIPT)
assert spec is not None and spec.loader is not None
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class LinuxCpuTests(unittest.TestCase):
    def test_proc_subsecond_cpu_and_descendant_are_summed(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as td:
            root=Path(td)
            # Linux /proc stat fields 3..: state, ppid ... utime(14), stime(15).
            def stat(pid,parent,user,system):
                path=root/str(pid);path.mkdir()
                fields=['S',str(parent)]+['0']*9+[str(user),str(system)]+['0']*8
                (path/'stat').write_text(str(pid)+' (worker name ) with parentheses) '+' '.join(fields))
            stat(10,1,18,2);stat(11,10,23,4);stat(12,1,500,0)
            with mock.patch.object(module.os,'sysconf',return_value=100):
                self.assertAlmostEqual(module.linux_tree_cpu(10,root),0.47)
                self.assertIsNone(module.linux_tree_cpu(999,root))
    def test_missing_proc_is_unavailable_not_zero_cpu(self):
        self.assertIsNone(module.linux_tree_cpu(1,Path('/nonexistent-pinshu-proc-fixture')))
    def test_linux_uses_high_resolution_instead_of_quantized_ps(self):
        with mock.patch.object(module.sys,'platform','linux'),mock.patch.object(module,'linux_tree_cpu',return_value=0.37),mock.patch.object(module.subprocess,'run',side_effect=AssertionError('quantized ps must not run')):
            self.assertAlmostEqual(module.tree_cpu(10),0.37)
    def test_unavailable_proc_keeps_portable_ps_fallback(self):
        with mock.patch.object(module.sys,'platform','linux'),mock.patch.object(module,'linux_tree_cpu',return_value=None),mock.patch.object(module.subprocess,'run',return_value=subprocess.CompletedProcess([],0,stdout='10 1 0:00.50\n11 10 0:00.25\n')):
            self.assertAlmostEqual(module.tree_cpu(10),0.75)

if __name__=='__main__':unittest.main()
