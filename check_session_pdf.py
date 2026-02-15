"""
Check if a specific session has a PDF generated.
"""
import asyncio
from app.storage.mongodb import get_session_doc
from app.storage.pdf_storage import check_pdf_exists, retrieve_pdf_by_session

async def check_session(session_id: str):
    print(f"Checking session: {session_id}\n")
    print("=" * 70)

    # Check if session exists in MongoDB
    print("\n[1] Checking if session exists in MongoDB...")
    doc = await get_session_doc(session_id)

    if doc is None:
        print("[X] Session NOT FOUND in MongoDB")
        print("\nPossible reasons:")
        print("  - Session ID is incorrect")
        print("  - Session not yet saved to MongoDB")
        print("  - MongoDB connection issue")
        return

    print("[OK] Session found in MongoDB")

    # Check PDF metadata in session
    print("\n[2] Checking PDF metadata in session record...")
    pdf_generated = doc.get("pdfReportGenerated", False)
    pdf_file_id = doc.get("pdfReportFileId", None)
    pdf_case_id = doc.get("pdfReportCaseId", None)
    pdf_timestamp = doc.get("pdfReportGeneratedAt", None)

    print(f"  - pdfReportGenerated: {pdf_generated}")
    print(f"  - pdfReportFileId: {pdf_file_id}")
    print(f"  - pdfReportCaseId: {pdf_case_id}")
    print(f"  - pdfReportGeneratedAt: {pdf_timestamp}")

    if not pdf_generated:
        print("\n[X] PDF was NOT generated for this session")
        print("\nReasons why PDF might not be generated:")

        scam_detected = doc.get("scamDetected", False)
        total_messages = doc.get("totalMessagesExchanged", 0)

        print(f"  - Scam detected: {scam_detected} (needs to be True)")
        print(f"  - Total messages: {total_messages} (needs to be >= 3)")

        if not scam_detected:
            print("\n[!]  PDF not generated because scam was NOT detected")
        elif total_messages < 3:
            print(f"\n[!]  PDF not generated because only {total_messages} messages (need 3+)")
        else:
            print("\n[!]  PDF should have been generated but failed - check logs")
        return

    print("\n[OK] PDF metadata indicates PDF was generated")

    # Check if PDF exists in GridFS
    print("\n[3] Checking if PDF exists in GridFS...")
    exists = await check_pdf_exists(session_id)

    if not exists:
        print("[X] PDF NOT FOUND in GridFS")
        print("\nPossible issue:")
        print("  - PDF metadata saved but file upload failed")
        print("  - GridFS storage issue")
        print(f"  - File ID {pdf_file_id} may be invalid")
        return

    print("[OK] PDF exists in GridFS")

    # Try to retrieve PDF
    print("\n[4] Attempting to retrieve PDF...")
    result = await retrieve_pdf_by_session(session_id)

    if result is None:
        print("[X] Failed to retrieve PDF from GridFS")
        return

    pdf_bytes, metadata = result
    print(f"[OK] PDF retrieved successfully")
    print(f"\n  Metadata:")
    print(f"    - Filename: {metadata['filename']}")
    print(f"    - Size: {metadata['length']} bytes")
    print(f"    - Upload Date: {metadata['uploadDate']}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("[OK] Session exists: YES")
    print(f"[OK] PDF generated: {pdf_generated}")
    print(f"[OK] PDF in GridFS: YES")
    print(f"[OK] PDF retrievable: YES")
    print(f"\nPDF Size: {metadata['length']} bytes")
    print(f"Case ID: {pdf_case_id}")
    print(f"\n[OK] The PDF download endpoint SHOULD work for this session!")
    print("\nDownload URL:")
    print(f"https://scambot-honeypot.onrender.com/api/v1/admin/report/{session_id}?admin_key=honeypot123")
    print("=" * 70)


if __name__ == "__main__":
    # The session ID you tried
    session_id = "1f1fba65-ee05-4ad6-9a9b-44bdafb41fe5"

    print("\nPDF Session Checker")
    print("=" * 70)

    try:
        asyncio.run(check_session(session_id))
    except Exception as e:
        print(f"\n[X] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
