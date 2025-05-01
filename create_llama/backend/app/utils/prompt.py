OUTPUT_FORMAT = """
Return the results as a JSON array, with each object containing:
- "headline": the related article's headline
- "permalink": a clickable URL to the article
- "rationale": a brief explanation of why this article is related

The output should be a valid JSON array only — no explanations, markdown, or extra text.
Format:
[
  {{
    "headline": "Related Article Headline",
    "permalink": "https://www.edwardconard.com/macro-roundup/xxxxx",
    "rationale": "Brief reason why this article is relevant"
  }},
  ...
]
"""