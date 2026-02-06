#!/usr/bin/env python3
"""
Script untuk memvalidasi template output dari sentiment analysis agent.
Memeriksa apakah file sentiment.md sesuai dengan template yang diharapkan.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Path ke file sentiment.md
SENTIMENT_FILE = Path("project-context/2.build/artifacts/sentiment.md")

# Heading yang diharapkan (dari expected_output di tasks.yaml)
REQUIRED_HEADINGS = [
    "Sentiment Summary",
    "Identified Risks",
    "Brand Safety Concerns",
    "Risk Mitigation Strategies",
    "Opportunities",
    "Recommendations",
    "Audit",
]

# Heading yang direkomendasikan (dari konten yang harus ada)
RECOMMENDED_HEADINGS = [
    "Platform-Specific Risk Matrix",
    "Misinformation & Claim Risk Assessment",
    "Cultural, Legal, or Ethical Risk Flags",
]

# Pattern untuk Pie Chart line
PIE_CHART_PATTERN = re.compile(
    r"Sentiment Composition\s*\([^)]*\)\s*:\s*(?:Positive|Positif)\s*(\d+(?:\.\d+)?)\s*%?\s*,?\s*(?:Neutral|Netral)\s*(\d+(?:\.\d+)?)\s*%?\s*,?\s*(?:Negative|Negatif)\s*(\d+(?:\.\d+)?)\s*%?",
    re.IGNORECASE
)


def check_pie_chart_line(content: str) -> Tuple[bool, str, Dict[str, float]]:
    """Memeriksa apakah Pie Chart line ada dan valid."""
    lines = content.split('\n')
    first_line = lines[0].strip() if lines else ""
    
    match = PIE_CHART_PATTERN.search(first_line)
    if not match:
        return False, "Pie Chart line tidak ditemukan di baris pertama", {}
    
    positive = float(match.group(1))
    neutral = float(match.group(2))
    negative = float(match.group(3))
    total = positive + neutral + negative
    
    if abs(total - 100.0) > 0.1:  # Allow small floating point errors
        return False, f"Total persentase tidak sama dengan 100% (Total: {total}%)", {
            "positive": positive,
            "neutral": neutral,
            "negative": negative
        }
    
    return True, "Pie Chart line valid", {
        "positive": positive,
        "neutral": neutral,
        "negative": negative
    }


def check_headings(content: str) -> Tuple[List[str], List[str]]:
    """Memeriksa apakah semua heading yang diperlukan ada."""
    found_headings = []
    missing_headings = []
    
    # Extract all headings (H1 and H2)
    heading_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
    headings_in_file = heading_pattern.findall(content)
    
    # Normalize headings (remove extra spaces, convert to title case)
    normalized_found = {h.strip().title() for h in headings_in_file}
    
    for required in REQUIRED_HEADINGS:
        normalized_required = required.strip().title()
        # Check if any found heading contains the required heading
        found = any(normalized_required in h or h in normalized_required 
                   for h in normalized_found)
        if found:
            found_headings.append(required)
        else:
            missing_headings.append(required)
    
    return found_headings, missing_headings


def check_recommended_headings(content: str) -> List[str]:
    """Memeriksa apakah heading yang direkomendasikan ada."""
    found_recommended = []
    
    heading_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)
    headings_in_file = heading_pattern.findall(content)
    normalized_found = {h.strip().title() for h in headings_in_file}
    
    for recommended in RECOMMENDED_HEADINGS:
        normalized_recommended = recommended.strip().title()
        found = any(normalized_recommended in h or h in normalized_recommended 
                   for h in normalized_found)
        if found:
            found_recommended.append(recommended)
    
    return found_recommended


def check_code_fences(content: str) -> Tuple[bool, int]:
    """Memeriksa apakah ada code fences (tidak diperbolehkan)."""
    code_fence_count = content.count('```')
    return code_fence_count == 0, code_fence_count


def check_content_elements(content: str) -> Dict[str, bool]:
    """Memeriksa apakah elemen konten penting ada."""
    checks = {
        "Overall Sentiment Score": "sentiment score" in content.lower() or "confidence level" in content.lower(),
        "Key Positive Sentiment Drivers": "positive" in content.lower() and ("driver" in content.lower() or "sentiment" in content.lower()),
        "Key Negative Sentiment Triggers": "negative" in content.lower() and ("trigger" in content.lower() or "sentiment" in content.lower()),
        "Audience Sensitivity Areas": "audience" in content.lower() and ("sensitivity" in content.lower() or "sensitive" in content.lower()),
        "Potential Controversy Scenarios": "controversy" in content.lower() or "controversial" in content.lower(),
        "Risk Mitigation": "mitigation" in content.lower() or "mitigate" in content.lower(),
        "Platform-Specific": "platform" in content.lower() and ("youtube" in content.lower() or "instagram" in content.lower() or "tiktok" in content.lower()),
        "Risk Severity": "severity" in content.lower() or ("low" in content.lower() and "medium" in content.lower() and "high" in content.lower()),
    }
    return checks


def main():
    """Fungsi utama untuk validasi."""
    if not SENTIMENT_FILE.exists():
        print(f"[ERROR] File tidak ditemukan: {SENTIMENT_FILE}")
        print(f"   Pastikan file sentiment.md ada di lokasi tersebut.")
        sys.exit(1)
    
    print(f"[FILE] Memeriksa file: {SENTIMENT_FILE}\n")
    
    content = SENTIMENT_FILE.read_text(encoding='utf-8')
    
    # 1. Check Pie Chart line
    print("=" * 60)
    print("1. PENGECEKAN PIE CHART LINE")
    print("=" * 60)
    pie_valid, pie_msg, pie_data = check_pie_chart_line(content)
    if pie_valid:
        print(f"[OK] {pie_msg}")
        print(f"   Positive: {pie_data['positive']}%")
        print(f"   Neutral: {pie_data['neutral']}%")
        print(f"   Negative: {pie_data['negative']}%")
    else:
        print(f"[ERROR] {pie_msg}")
        if pie_data:
            print(f"   Positive: {pie_data.get('positive', 'N/A')}%")
            print(f"   Neutral: {pie_data.get('neutral', 'N/A')}%")
            print(f"   Negative: {pie_data.get('negative', 'N/A')}%")
    
    # 2. Check Required Headings
    print("\n" + "=" * 60)
    print("2. PENGECEKAN HEADING YANG DIPERLUKAN")
    print("=" * 60)
    found_headings, missing_headings = check_headings(content)
    
    if found_headings:
        print(f"[OK] Heading yang ditemukan ({len(found_headings)}):")
        for h in found_headings:
            print(f"   - {h}")
    
    if missing_headings:
        print(f"\n[ERROR] Heading yang tidak ditemukan ({len(missing_headings)}):")
        for h in missing_headings:
            print(f"   - {h}")
    else:
        print("\n[OK] Semua heading yang diperlukan ditemukan!")
    
    # 3. Check Recommended Headings
    print("\n" + "=" * 60)
    print("3. PENGECEKAN HEADING YANG DIREKOMENDASIKAN")
    print("=" * 60)
    found_recommended = check_recommended_headings(content)
    missing_recommended = [h for h in RECOMMENDED_HEADINGS if h not in found_recommended]
    
    if found_recommended:
        print(f"[OK] Heading yang ditemukan ({len(found_recommended)}):")
        for h in found_recommended:
            print(f"   - {h}")
    
    if missing_recommended:
        print(f"\n[WARNING] Heading yang direkomendasikan tapi tidak ditemukan ({len(missing_recommended)}):")
        for h in missing_recommended:
            print(f"   - {h}")
        print("   (Ini tidak wajib, tapi direkomendasikan untuk kelengkapan analisis)")
    else:
        print("\n[OK] Semua heading yang direkomendasikan ditemukan!")
    
    # 4. Check Code Fences
    print("\n" + "=" * 60)
    print("4. PENGECEKAN CODE FENCES")
    print("=" * 60)
    no_fences, fence_count = check_code_fences(content)
    if no_fences:
        print("[OK] Tidak ada code fences (triple backticks) - sesuai template")
    else:
        print(f"[ERROR] Ditemukan {fence_count} code fences - tidak sesuai template")
        print("   Template mengharuskan plain Markdown tanpa code fences")
    
    # 5. Check Content Elements
    print("\n" + "=" * 60)
    print("5. PENGECEKAN ELEMEN KONTEN")
    print("=" * 60)
    content_checks = check_content_elements(content)
    for element, found in content_checks.items():
        status = "[OK]" if found else "[WARNING]"
        print(f"{status} {element}: {'Ditemukan' if found else 'Tidak ditemukan atau kurang jelas'}")
    
    # Summary
    print("\n" + "=" * 60)
    print("RINGKASAN VALIDASI")
    print("=" * 60)
    
    all_passed = (
        pie_valid and
        len(missing_headings) == 0 and
        no_fences
    )
    
    if all_passed:
        print("[OK] Template VALID - Semua elemen wajib ada dan sesuai format")
        if missing_recommended:
            print(f"[WARNING] Catatan: {len(missing_recommended)} heading yang direkomendasikan tidak ditemukan")
        sys.exit(0)
    else:
        print("[ERROR] Template TIDAK VALID - Ada elemen yang kurang atau tidak sesuai")
        print("\nPerbaikan yang diperlukan:")
        if not pie_valid:
            print("  - Perbaiki format Pie Chart line di baris pertama")
        if missing_headings:
            print(f"  - Tambahkan {len(missing_headings)} heading yang diperlukan")
        if not no_fences:
            print("  - Hapus code fences (triple backticks) dari output")
        sys.exit(1)


if __name__ == "__main__":
    main()
