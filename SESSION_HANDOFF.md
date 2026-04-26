# Session Handoff — April 26 2026

## Branch: phase2-perturbation

## Direction 2 Status
- extractor.py: COMPLETE (commit e56ecdc)
- Schema validated for 2225G: PASS
- checker_generator.py: NOT STARTED

## Next Task (Task 2)
Build doctor/dynamic/checker_generator.py

Single function:
  generate_checker(schema: dict) -> str | None

Rules:
- Calls LLM to generate checker matching signature:
  def check(input_args: dict, output) -> tuple[bool, str]
- Standard Python only, no external libraries
- Validator only — never implements a solver
- Runs all 4 protocol tests from docs/direction2_checker_protocol.md
- Returns checker source code string if all 4 pass, None otherwise
- Logs specific failure_mode on failure

## Registry: 40 problems
## Key files
- doctor/dynamic/extractor.py — extraction engine
- docs/direction2_extraction_schema.md — schema spec  
- docs/direction2_checker_protocol.md — checker protocol
- doctor/dynamic/ — Direction 2 home directory
