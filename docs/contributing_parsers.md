# Contributing Parsers

A parser implements `can_handle`, `parse_request`, and `parse_response`. Keep parsing defensive and return useful partial data. Do not throw for malformed JSON.

Add tests for request parsing, response parsing, unknown fields, failed responses, and pricing/token behavior when relevant.
