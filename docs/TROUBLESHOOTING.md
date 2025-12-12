# 🔧 Troubleshooting Guide

> **Last Updated:** 2025-12-08

## 🌐 HuggingFace API Issues

### "401 Unauthorized" Error
**Cause:** HF_TOKEN not set or invalid.
**Fix:**
```bash
# Check if token is set
echo $HF_TOKEN

# Set token
export HF_TOKEN="hf_your_token_here"
```

### "Model Loading" Takes Forever
**Cause:** First request to a model triggers warmup.
**Fix:** Wait 30-60 seconds for initial model load. Subsequent requests are faster.

### "Task not supported" Error (HTTP 500)
**Cause:** Attempting to use constrained models (Mistral/Qwen) on Free Tier for `text-generation`.
**Fix:** The app now enforces **Single-Model Architecture**. Please **Restart** your server to clear any stale processes trying to load old models.

### "Rate Limited" Error
**Cause:** Free tier has request limits (~300 requests/hour).
**Fix:** Wait 1 minute, or upgrade to HuggingFace Pro.

---

## 🖥️ Local Deployment Issues

### Port 7860 Already in Use
**Cause:** Another application using the port.
**Fix:** The app auto-finds next available port (7861, 7862, etc.). Check console output.

### Slow Response Times
**Cause:** Cold start or network latency.
**Fix:**
- Ensure stable internet connection
- First response may take longer due to model loading

### ImportError: No module named 'sentence_transformers'
**Fix:**
```bash
pip install sentence-transformers
```

### "Practice Mode requires full module installation"
**Cause:** Missing system library `libmagic` required for secure file type detection.
**Fix (Windows):** Run `pip install python-magic-bin`
**Fix (Linux/Mac):** Install `libmagic1` (Debian/Ubuntu) or `libmagic` (standard).

### "TypeError: argument of type 'bool' is not iterable"
**Cause:** Bug in Gradio 5.x schema parsing when using certain return types.
**Fix:** Downgrade to Gradio 4.44.0 (Recommended):
```bash
pip install "gradio==4.44.0"
```

---

## 🎯 Evaluation Issues

### Scores Seem Too Low
**Possible Causes:**
1. Answer is off-topic (semantic check triggered)
2. Missing structure (no bullet points, examples)
3. Too brief (< 50 words)

**Fix:** Provide comprehensive, structured answers with examples.

### "Answer does not appear to address the question"
**Cause:** Semantic similarity below 0.25 threshold.
**Fix:** Ensure your answer directly addresses the question asked.

---

## 📞 Getting Help

1. Check the [GitHub Issues](https://github.com/VIKAS9793/ai-interviewer-langchain/issues)
2. Verify HuggingFace API status: https://status.huggingface.co
3. Check `logs/` directory for detailed error messages
