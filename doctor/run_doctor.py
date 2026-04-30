from doctor.pipeline import run_pipeline


def run_doctor(statement: str, solution_code: str) -> dict:
    return run_pipeline(statement, solution_code)
