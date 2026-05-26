def generate_membership_id(district_code: str, year: int, sequence_num: int) -> str:
    """
    Generate TVK-[DIST]-[YYYY]-[XXXXX]
    Example: TVK-CHN-2026-00142
    """
    return f"TVK-{district_code[:3].upper()}-{year}-{sequence_num:05d}"
