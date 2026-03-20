#!/usr/bin/env python3
from __future__ import annotations

import json

from rag_common import add_records, build_records, cfg_from_args, common_parser, parse_metadata, read_text_input


def main() -> int:
    parser = common_parser("Ingest text or a file into Mac Mini LanceDB RAG")
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--source-type", default="document")
    parser.add_argument("--text")
    parser.add_argument("--file")
    parser.add_argument("--metadata-json")
    args = parser.parse_args()

    cfg = cfg_from_args(args)
    text = read_text_input(args.text, args.file)
    metadata = parse_metadata(args.metadata_json)
    records = build_records(
        source_id=args.source_id,
        source_type=args.source_type,
        text=text,
        cfg=cfg,
        metadata=metadata,
    )
    result = add_records(records, cfg)
    print(json.dumps({"ok": True, "action": "ingest", **result}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
