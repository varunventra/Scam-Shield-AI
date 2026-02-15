# PDF Storage - Quick Start Guide

## ✅ Implementation Complete

The forensic PDF reports are now stored permanently in MongoDB Atlas instead of locally.

---

## How It Works

### Automatic PDF Generation

PDFs are automatically generated when:
1. ✅ Scam is detected
2. ✅ Conversation has at least 3 messages
3. ✅ PDF doesn't already exist for that session

No manual intervention needed - happens automatically in the conversation pipeline.

---

## Testing the Implementation

### 1. Run the Test Script

```bash
python test_pdf_storage.py
```

This will:
- Test PDF generation as bytes
- Test storage in MongoDB GridFS
- Test retrieval mechanisms
- Test duplicate prevention
- Verify all components work together

### 2. Test via API (Manual)

**Step 1: Have a scam conversation (3+ messages)**
```bash
POST http://your-api/conversation
```

**Step 2: Download the PDF**
```bash
GET http://your-api/admin/report/{session_id}?admin_key=YOUR_ADMIN_KEY
```

The PDF will open directly in your browser.

---

## API Endpoint

### Download PDF Report

```
GET /admin/report/{session_id}
```

**Parameters:**
- `session_id` (path) - The session ID from the conversation
- `admin_key` (query) - Your admin API key

**Response:**
- **200 OK** - PDF file (opens in browser)
- **404 Not Found** - No PDF exists for that session
- **401 Unauthorized** - Invalid admin key
- **400 Bad Request** - Invalid session ID

**Example:**
```bash
curl -X GET "http://localhost:8000/admin/report/session_abc123?admin_key=your-admin-key" \
  --output report.pdf
```

---

## What Changed

### New Files
- `app/storage/pdf_storage.py` - GridFS storage functions

### Modified Files
- `app/services/forensic_reporter.py` - Added `generate_forensic_report_bytes()`
- `app/storage/mongodb.py` - Added PDF metadata fields to session storage
- `app/api/routes.py` - Added PDF generation + download endpoint

### No Breaking Changes
- All existing functionality works exactly the same
- PDF storage is an addition, not a replacement
- Graceful degradation if MongoDB unavailable

---

## MongoDB Schema

### Session Record (scam_sessions collection)

New fields added:
```json
{
  "pdfReportGenerated": true,
  "pdfReportFileId": "507f1f77bcf86cd799439011",
  "pdfReportGeneratedAt": "2025-02-15T10:30:00Z",
  "pdfReportCaseId": "HC-20250215-ABC123"
}
```

### GridFS Storage (forensic_pdfs bucket)

Files stored with metadata:
```json
{
  "filename": "CyberCrime_Report_HC-20250215-ABC123.pdf",
  "metadata": {
    "sessionId": "session_abc123",
    "caseId": "HC-20250215-ABC123",
    "uploadedAt": "2025-02-15T10:30:00Z",
    "contentType": "application/pdf",
    "size": 245632,
    "scamDetected": true,
    "totalMessages": 5,
    "scamType": "BANK_IMPERSONATION"
  }
}
```

---

## Verifying in MongoDB Atlas

### Check if PDF was generated for a session

```javascript
db.scam_sessions.findOne(
  { sessionId: "your-session-id" },
  {
    pdfReportGenerated: 1,
    pdfReportFileId: 1,
    pdfReportGeneratedAt: 1,
    pdfReportCaseId: 1
  }
)
```

### List all stored PDFs

```javascript
db.forensic_pdfs.files.find({}, {
  filename: 1,
  "metadata.sessionId": 1,
  "metadata.caseId": 1,
  uploadDate: 1,
  length: 1
}).limit(10)
```

### Count total PDFs

```javascript
db.forensic_pdfs.files.countDocuments()
```

---

## Deployment to Render

### No Special Configuration Needed

The implementation is **already Render-ready**:

✅ No local file storage
✅ No disk writes
✅ Pure MongoDB storage
✅ Stateless architecture
✅ Environment variable based (MONGODB_URI)

Just push to git and deploy - it will work immediately.

---

## Monitoring & Logs

### Success Logs

```
INFO - GridFS bucket initialized for PDF storage
INFO - Forensic report generated as bytes (Case: HC-20250215-ABC123, Size: 245632 bytes)
INFO - PDF stored in GridFS - Session: session_abc123, FileID: 507f..., Size: 245632 bytes
INFO - PDF retrieved from GridFS - FileID: 507f..., Size: 245632 bytes
```

### Prevention Logs

```
INFO - PDF already exists for session: session_abc123, skipping generation
```

### Warning Logs

```
WARNING - MONGODB_URI not set – PDF storage disabled
```

### Error Logs

```
ERROR - Failed to store PDF in GridFS - Session: session_abc123, Error: ...
ERROR - Forensic report generation/storage failed (non-blocking): ...
```

---

## Troubleshooting

### PDF not being generated

**Check:**
1. Is scam detected? (`scam_detected = True`)
2. Are there 3+ messages? (`message_count >= 3`)
3. Is MongoDB connected? (Check logs for GridFS initialization)
4. Does PDF already exist? (Check logs for "PDF already exists")

### PDF download returns 404

**Check:**
1. Was PDF actually generated? (Check session record in MongoDB)
2. Is the session ID correct?
3. Is admin key valid?

### MongoDB connection issues

**Check:**
1. Is `MONGODB_URI` set in environment?
2. Is MongoDB Atlas IP whitelist configured?
3. Are credentials correct?
4. Check logs for connection errors

---

## Example Workflow

### 1. Scammer Conversation

```
Scammer: "Your bank account is blocked"
Bot: "Oh no! What should I do?"
Scammer: "Send me OTP immediately"
Bot: "I'm checking my phone..."
```

### 2. Automatic PDF Generation (Behind the Scenes)

```
[System] Scam detected ✅
[System] Message count: 3 ✅
[System] Generating PDF...
[System] Storing in MongoDB GridFS...
[System] PDF stored with ID: 507f1f77bcf86cd799439011 ✅
```

### 3. Admin Downloads Report

```bash
GET /admin/report/session_abc123?admin_key=secret
```

**Browser opens PDF showing:**
- Executive Summary
- Suspect Contact Information
- Behavioral Markers
- Full Conversation Evidence Log
- Case ID: HC-20250215-ABC123

---

## Summary

### What You Get

✅ Automatic PDF generation when scam detected (3+ messages)
✅ Permanent storage in MongoDB Atlas (no local files)
✅ No duplicate PDFs (smart detection)
✅ Easy download via API endpoint
✅ Opens directly in browser
✅ Works on Render deployment
✅ Graceful degradation if MongoDB unavailable
✅ No breaking changes to existing code

### Files Changed

- 1 new file: `app/storage/pdf_storage.py`
- 3 modified files: `forensic_reporter.py`, `mongodb.py`, `routes.py`
- Total lines added: ~300 lines
- Breaking changes: 0

### Ready to Deploy

✅ All requirements met
✅ Test script included
✅ Documentation complete
✅ Backward compatible
✅ Production ready

---

**Need Help?**

- Check logs for error messages
- Run `python test_pdf_storage.py` to verify setup
- Review `PDF_STORAGE_IMPLEMENTATION.md` for detailed technical info
- Check MongoDB Atlas for stored PDFs

---

**Implementation Date:** 2026-02-15
**Status:** ✅ COMPLETE AND TESTED
