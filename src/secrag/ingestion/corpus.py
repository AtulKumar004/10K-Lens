"""The fixed set of companies we ingest: 10 per sector, all file 10-Ks for FY2023-FY2025.

Verified against SEC submissions (including the paged history). XOM is left out on purpose:
its ticker now maps to ExxonMobil Holdings Corp (CIK 2115436), which has no 10-K, while the
10-Ks sit under the old Exxon Mobil Corp (CIK 34088).
"""

CORPUS_TICKERS: list[str] = [
    # technology
    "AAPL", "MSFT", "NVDA", "GOOGL", "META", "AVGO", "ORCL", "CRM", "ADBE", "CSCO",
    # banking
    "JPM", "BAC", "WFC", "C", "GS", "MS", "USB", "PNC", "TFC", "COF",
    # healthcare
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "PFE", "TMO", "ABT", "AMGN", "BMY",
    # energy
    "DVN", "CVX", "COP", "EOG", "SLB", "OXY", "PSX", "MPC", "VLO", "KMI",
    # retail
    "AMZN", "WMT", "COST", "HD", "LOW", "TGT", "TJX", "BBY", "DG", "KR",
]  # fmt: skip
