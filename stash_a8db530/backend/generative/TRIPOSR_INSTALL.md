# TripoSR Installation Instructions

## Quick Setup (Recommended)

Since TripoSR doesn't have a standard pip package, we need to clone and install manually:

```bash
# 1. Clone TripoSR repository
cd i:\QYNTARA AI\backend\generative
git clone https://github.com/VAST-AI-Research/TripoSR.git

# 2. Install dependencies
cd TripoSR
pip install -r requirements.txt

# 3. Test installation
python -c "from tsr.system import TSR; print('TripoSR installed successfully!')"
```

## Alternative: Use Mock Mode

The LRM generator includes a **mock mode** that creates simple test meshes without requiring TripoSR installation. This is useful for:
- Testing the integration
- Development without GPU
- CI/CD pipelines

Mock mode is automatically enabled when TripoSR is not found.

## Verification

After installation, test the LRM generator:

```bash
cd i:\QYNTARA AI
python backend/generative/lrm_generator.py test_image.png output.obj
```

Expected output:
- `[LRM] Model loaded in X.XXs` (real mode)
- OR `[LRM] Using mock generation` (mock mode)

## Next Steps

Once TripoSR is installed:
1. Run benchmark tests: `python tests/test_lrm_benchmark.py --image test.png`
2. Start backend: `python backend/main.py`
3. Test API: `curl -X POST http://localhost:8000/image-to-3d -F "file=@test.png" -F "quality=draft"`

## Troubleshooting

**Issue**: `ImportError: No module named 'tsr'`
**Solution**: Make sure TripoSR is cloned to `backend/generative/TripoSR`

**Issue**: `CUDA out of memory`
**Solution**: Reduce marching cubes resolution: `mc_resolution=128` instead of `256`

**Issue**: Model download is slow
**Solution**: Pre-download weights from Hugging Face: https://huggingface.co/stabilityai/TripoSR
