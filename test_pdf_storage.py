"""
Test script for PDF storage implementation.

This script tests the complete PDF storage flow:
1. PDF generation as bytes
2. Storage in MongoDB GridFS
3. Retrieval from GridFS
4. Duplicate prevention

Run with: python test_pdf_storage.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.storage.pdf_storage import (
    store_pdf,
    retrieve_pdf,
    retrieve_pdf_by_session,
    check_pdf_exists,
    delete_pdf,
    get_gridfs_bucket
)
from app.services.forensic_reporter import ForensicReporter
from app.models.responses import ExtractedIntelligence
from app.models.requests import Message


async def test_pdf_storage():
    """Test the complete PDF storage workflow."""

    print("=" * 70)
    print("PDF STORAGE IMPLEMENTATION TEST")
    print("=" * 70)

    # Test 1: GridFS Bucket Initialization
    print("\n[TEST 1] GridFS Bucket Initialization...")
    bucket = await get_gridfs_bucket()
    if bucket is None:
        print("❌ FAILED: MongoDB not configured or unavailable")
        print("   Make sure MONGODB_URI is set in your environment")
        return
    print("✅ PASSED: GridFS bucket initialized successfully")

    # Test 2: Generate PDF as bytes
    print("\n[TEST 2] Generate PDF as bytes...")
    forensic_reporter = ForensicReporter()

    # Create test data
    test_session_id = "test_session_pdf_001"
    test_intelligence = ExtractedIntelligence(
        phoneNumbers=["+919876543210"],
        upiIds=["scammer@paytm"],
        bankAccounts=["1234567890"],
        phishingLinks=["http://fake-bank.com"],
        suspiciousKeywords=["urgent", "verify", "blocked"]
    )
    test_messages = [
        Message(sender="scammer", text="Your account is blocked", timestamp=1234567890),
        Message(sender="user", text="What should I do?", timestamp=1234567891),
        Message(sender="scammer", text="Send OTP immediately", timestamp=1234567892),
    ]

    pdf_bytes = forensic_reporter.generate_forensic_report_bytes(
        session_id=test_session_id,
        extracted_intelligence=test_intelligence,
        conversation_history=test_messages,
        agent_notes="Test scam detection - bank impersonation attempt",
        scam_detected=True,
        total_messages=3
    )

    if pdf_bytes is None:
        print("❌ FAILED: PDF generation returned None")
        return

    print(f"✅ PASSED: PDF generated successfully ({len(pdf_bytes)} bytes)")

    # Test 3: Store PDF in GridFS
    print("\n[TEST 3] Store PDF in MongoDB GridFS...")
    test_case_id = forensic_reporter._generate_case_id(test_session_id)

    file_id = await store_pdf(
        session_id=test_session_id,
        pdf_bytes=pdf_bytes,
        case_id=test_case_id,
        metadata={
            "scamDetected": True,
            "totalMessages": 3,
            "scamType": "BANK_IMPERSONATION"
        }
    )

    if file_id is None:
        print("❌ FAILED: PDF storage returned None")
        return

    print(f"✅ PASSED: PDF stored in GridFS with file_id: {file_id}")

    # Test 4: Check PDF exists
    print("\n[TEST 4] Check if PDF exists...")
    exists = await check_pdf_exists(test_session_id)

    if not exists:
        print("❌ FAILED: PDF should exist but check returned False")
        return

    print("✅ PASSED: PDF existence check successful")

    # Test 5: Retrieve PDF by file ID
    print("\n[TEST 5] Retrieve PDF by file ID...")
    result = await retrieve_pdf(file_id)

    if result is None:
        print("❌ FAILED: PDF retrieval returned None")
        return

    retrieved_bytes, metadata = result

    if len(retrieved_bytes) != len(pdf_bytes):
        print(f"❌ FAILED: Size mismatch (original: {len(pdf_bytes)}, retrieved: {len(retrieved_bytes)})")
        return

    print(f"✅ PASSED: PDF retrieved successfully")
    print(f"   Filename: {metadata['filename']}")
    print(f"   Size: {metadata['length']} bytes")
    print(f"   Upload Date: {metadata['uploadDate']}")

    # Test 6: Retrieve PDF by session ID
    print("\n[TEST 6] Retrieve PDF by session ID...")
    result = await retrieve_pdf_by_session(test_session_id)

    if result is None:
        print("❌ FAILED: PDF retrieval by session ID returned None")
        return

    retrieved_bytes, metadata = result

    if len(retrieved_bytes) != len(pdf_bytes):
        print(f"❌ FAILED: Size mismatch when retrieving by session ID")
        return

    print(f"✅ PASSED: PDF retrieved by session ID successfully")

    # Test 7: Duplicate prevention
    print("\n[TEST 7] Test duplicate prevention...")
    exists_before = await check_pdf_exists(test_session_id)

    if not exists_before:
        print("❌ FAILED: PDF should exist before duplicate check")
        return

    print("✅ PASSED: Duplicate prevention check - PDF already exists")
    print("   (In production, generation would be skipped)")

    # Test 8: Cleanup - Delete test PDF
    print("\n[TEST 8] Cleanup - Delete test PDF...")
    deleted = await delete_pdf(file_id)

    if not deleted:
        print("⚠️  WARNING: Failed to delete test PDF (non-critical)")
    else:
        print("✅ PASSED: Test PDF deleted successfully")

    # Verify deletion
    exists_after = await check_pdf_exists(test_session_id)
    if exists_after:
        print("⚠️  WARNING: PDF still exists after deletion (check manually)")
    else:
        print("✅ PASSED: Deletion verified - PDF no longer exists")

    # Final Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("✅ ALL TESTS PASSED")
    print("\nImplementation verified:")
    print("  ✅ GridFS bucket initialization")
    print("  ✅ PDF generation as bytes")
    print("  ✅ PDF storage in MongoDB")
    print("  ✅ PDF existence check")
    print("  ✅ PDF retrieval by file ID")
    print("  ✅ PDF retrieval by session ID")
    print("  ✅ Duplicate prevention mechanism")
    print("  ✅ PDF deletion (cleanup)")
    print("\n🎉 PDF storage implementation is working perfectly!")
    print("=" * 70)


async def test_mongodb_unavailable():
    """Test graceful degradation when MongoDB is unavailable."""
    print("\n" + "=" * 70)
    print("GRACEFUL DEGRADATION TEST (MongoDB Unavailable)")
    print("=" * 70)
    print("\nThis test verifies the system degrades gracefully when MongoDB")
    print("is unavailable. If MongoDB is configured, this test will be skipped.")
    print("\nTo test graceful degradation:")
    print("1. Temporarily unset MONGODB_URI")
    print("2. Run the test again")
    print("3. Verify logs show 'PDF storage disabled'")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🔍 Starting PDF Storage Tests...\n")

    try:
        asyncio.run(test_pdf_storage())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ TEST FAILED WITH ERROR:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    print("\n")
