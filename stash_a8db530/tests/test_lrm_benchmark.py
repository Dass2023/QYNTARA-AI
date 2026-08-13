"""
LRM Benchmark Test Suite
Compares TripoSR (LRM) vs Trellis performance and quality.

Metrics:
- Generation speed (seconds)
- Face count (triangles)
- Memory usage (VRAM)
- Quality assessment (subjective 1-10 scale)
"""

import os
import time
import sys
import psutil
import torch
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.generative.lrm_generator import LRMGenerator
from backend.generative.image_to_3d import ImageTo3DGenerator


class BenchmarkRunner:
    """Runs performance benchmarks for LRM vs Trellis"""
    
    def __init__(self):
        self.results = []
        
    def get_gpu_memory(self) -> float:
        """Get current GPU memory usage in GB"""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**3
        return 0.0
    
    def benchmark_lrm(self, image_path: str, output_path: str) -> Dict:
        """Benchmark TripoSR generation"""
        print("\n=== Benchmarking TripoSR (LRM) ===")
        
        generator = LRMGenerator()
        
        # Measure memory before
        mem_before = self.get_gpu_memory()
        
        # Run generation
        start = time.time()
        result = generator.generate(image_path, output_path, mc_resolution=256)
        elapsed = time.time() - start
        
        # Measure memory after
        mem_after = self.get_gpu_memory()
        mem_used = mem_after - mem_before
        
        if result["status"] == "success":
            metrics = result["metrics"]
            return {
                "method": "TripoSR (LRM)",
                "time_seconds": elapsed,
                "face_count": metrics.get("face_count", 0),
                "vertex_count": metrics.get("vertex_count", 0),
                "memory_gb": mem_used,
                "is_watertight": metrics.get("is_watertight", False),
                "status": "success"
            }
        else:
            return {
                "method": "TripoSR (LRM)",
                "status": "failed",
                "error": result.get("error", "Unknown error")
            }
    
    def benchmark_trellis(self, image_path: str, output_path: str) -> Dict:
        """Benchmark Trellis generation"""
        print("\n=== Benchmarking Trellis (High Quality) ===")
        
        try:
            generator = ImageTo3DGenerator()
            
            # Measure memory before
            mem_before = self.get_gpu_memory()
            
            # Run generation
            start = time.time()
            result = generator.generate(image_path, output_path)
            elapsed = time.time() - start
            
            # Measure memory after
            mem_after = self.get_gpu_memory()
            mem_used = mem_after - mem_before
            
            if result.get("status") == "success":
                # Load mesh to get metrics
                import trimesh
                mesh = trimesh.load(output_path)
                
                return {
                    "method": "Trellis (High Quality)",
                    "time_seconds": elapsed,
                    "face_count": len(mesh.faces),
                    "vertex_count": len(mesh.vertices),
                    "memory_gb": mem_used,
                    "is_watertight": mesh.is_watertight,
                    "status": "success"
                }
            else:
                return {
                    "method": "Trellis (High Quality)",
                    "status": "failed",
                    "error": result.get("error", "Unknown error")
                }
        except Exception as e:
            return {
                "method": "Trellis (High Quality)",
                "status": "failed",
                "error": str(e)
            }
    
    def run_comparison(self, image_path: str):
        """Run full comparison benchmark"""
        print(f"\n{'='*60}")
        print(f"BENCHMARK: {os.path.basename(image_path)}")
        print(f"{'='*60}")
        
        # Create output directory
        os.makedirs("tests/benchmark_results", exist_ok=True)
        
        # Benchmark LRM
        lrm_output = f"tests/benchmark_results/lrm_{os.path.basename(image_path).replace('.png', '.obj')}"
        lrm_result = self.benchmark_lrm(image_path, lrm_output)
        self.results.append(lrm_result)
        
        # Benchmark Trellis
        trellis_output = f"tests/benchmark_results/trellis_{os.path.basename(image_path).replace('.png', '.obj')}"
        trellis_result = self.benchmark_trellis(image_path, trellis_output)
        self.results.append(trellis_result)
        
        # Print comparison
        self.print_comparison(lrm_result, trellis_result)
    
    def print_comparison(self, lrm: Dict, trellis: Dict):
        """Print side-by-side comparison"""
        print(f"\n{'='*60}")
        print("COMPARISON RESULTS")
        print(f"{'='*60}")
        
        if lrm["status"] == "success" and trellis["status"] == "success":
            speedup = trellis["time_seconds"] / lrm["time_seconds"]
            
            print(f"\n{'Metric':<25} {'TripoSR (LRM)':<20} {'Trellis (High)':<20} {'Winner':<15}")
            print(f"{'-'*80}")
            print(f"{'Generation Time':<25} {lrm['time_seconds']:<20.2f}s {trellis['time_seconds']:<20.2f}s {'LRM (' + str(round(speedup, 1)) + 'x)':<15}")
            print(f"{'Face Count':<25} {lrm['face_count']:<20,} {trellis['face_count']:<20,} {'Trellis':<15}")
            print(f"{'Vertex Count':<25} {lrm['vertex_count']:<20,} {trellis['vertex_count']:<20,} {'Trellis':<15}")
            print(f"{'Memory Usage':<25} {lrm['memory_gb']:<20.2f}GB {trellis['memory_gb']:<20.2f}GB {'LRM' if lrm['memory_gb'] < trellis['memory_gb'] else 'Trellis':<15}")
            print(f"{'Watertight':<25} {str(lrm['is_watertight']):<20} {str(trellis['is_watertight']):<20} {'-':<15}")
            
            print(f"\n{'='*60}")
            print(f"SPEEDUP: {speedup:.1f}x faster with LRM")
            print(f"QUALITY TRADEOFF: {trellis['face_count'] / lrm['face_count']:.1f}x more detail with Trellis")
            print(f"{'='*60}")
        else:
            print("\n⚠ One or both methods failed:")
            if lrm["status"] != "success":
                print(f"  LRM: {lrm.get('error', 'Unknown error')}")
            if trellis["status"] != "success":
                print(f"  Trellis: {trellis.get('error', 'Unknown error')}")
    
    def generate_report(self, output_file: str = "tests/benchmark_report.md"):
        """Generate markdown report"""
        print(f"\nGenerating report: {output_file}")
        
        with open(output_file, 'w') as f:
            f.write("# LRM Benchmark Report\n\n")
            f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Summary\n\n")
            
            # Calculate averages
            lrm_results = [r for r in self.results if r["method"] == "TripoSR (LRM)" and r["status"] == "success"]
            trellis_results = [r for r in self.results if r["method"] == "Trellis (High Quality)" and r["status"] == "success"]
            
            if lrm_results and trellis_results:
                avg_lrm_time = sum(r["time_seconds"] for r in lrm_results) / len(lrm_results)
                avg_trellis_time = sum(r["time_seconds"] for r in trellis_results) / len(trellis_results)
                avg_speedup = avg_trellis_time / avg_lrm_time
                
                f.write(f"- **Average LRM Time**: {avg_lrm_time:.2f}s\n")
                f.write(f"- **Average Trellis Time**: {avg_trellis_time:.2f}s\n")
                f.write(f"- **Average Speedup**: {avg_speedup:.1f}x\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Method | Time (s) | Faces | Vertices | Memory (GB) | Watertight | Status |\n")
            f.write("|--------|----------|-------|----------|-------------|------------|--------|\n")
            
            for result in self.results:
                if result["status"] == "success":
                    f.write(f"| {result['method']} | {result['time_seconds']:.2f} | {result['face_count']:,} | {result['vertex_count']:,} | {result['memory_gb']:.2f} | {result['is_watertight']} | ✅ |\n")
                else:
                    f.write(f"| {result['method']} | - | - | - | - | - | ❌ {result.get('error', 'Failed')} |\n")
            
            f.write("\n## Conclusion\n\n")
            
            if lrm_results and trellis_results:
                f.write(f"TripoSR (LRM) achieves **{avg_speedup:.1f}x speedup** over Trellis, making it suitable for:\n")
                f.write("- Real-time generation workflows\n")
                f.write("- Background assets and rapid prototyping\n")
                f.write("- Runtime generation in Unity/Unreal\n\n")
                f.write("Trellis remains the better choice for:\n")
                f.write("- Hero assets requiring maximum detail\n")
                f.write("- Final production-quality models\n")
                f.write("- Cases where generation time is not critical\n")
        
        print(f"✅ Report saved to: {output_file}")


def main():
    """Main benchmark entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark LRM vs Trellis")
    parser.add_argument("--image", type=str, help="Path to test image")
    parser.add_argument("--batch", action="store_true", help="Run batch test on multiple images")
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    
    if args.batch:
        # Batch mode: test multiple images
        test_images = [
            "backend/data/test_chair.png",
            "backend/data/test_character.png",
            "backend/data/test_prop.png"
        ]
        
        for img in test_images:
            if os.path.exists(img):
                runner.run_comparison(img)
            else:
                print(f"⚠ Image not found: {img}")
    
    elif args.image:
        # Single image mode
        if os.path.exists(args.image):
            runner.run_comparison(args.image)
        else:
            print(f"❌ Image not found: {args.image}")
            return
    else:
        print("Usage:")
        print("  python test_lrm_benchmark.py --image path/to/image.png")
        print("  python test_lrm_benchmark.py --batch")
        return
    
    # Generate report
    runner.generate_report()


if __name__ == "__main__":
    main()
