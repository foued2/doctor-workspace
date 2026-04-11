"""
LeetCode Problem Suggestor
===========================
This script automatically:
1. Fetches LeetCode problem ratings from ZeroTrac
2. Finds the easiest problem not yet solved in your project
3. Auto-creates the solution file with full problem statement
4. Detects when you've solved a problem and suggests the next one

Usage:
    python leetcode_suggestor.py          # Auto-creates file for easiest unsolved problem
    python leetcode_suggestor.py --all    # Show top 10 easiest unsolved problems (without creating files)

How it works:
    1. Script scans your project for solved problems
    2. Finds the easiest unsolved problem from ZeroTrac ratings
    3. Automatically creates the solution file with problem statement
    4. Next time you run it, it detects the file exists and suggests the next easiest

A problem is considered "solved" when:
    - The file exists in the correct folder (e.g., 3801 to 3900/3870. Count Commas in Range.py)
    - OR you've marked it as solved in the .solved_tracking.json file
"""

import re
import sys
import json
import builtins
from pathlib import Path
from typing import List, Dict, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, IOError):
        pass

TOOLS_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = TOOLS_ROOT.parent
SOLUTIONS_ROOT = PROJECT_ROOT / "solutions"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from execution_controller import DEFAULT_BATCH_SIZE, ExecutionControlError, get_execution_controller

CONTROLLER = get_execution_controller(SOLUTIONS_ROOT)
SCAN_BATCH_SIZE = DEFAULT_BATCH_SIZE
DISPLAY_BATCH_SIZE = 10
RATING_CHUNK_SIZE = 25
FOLDER_PATTERN = re.compile(r"(\d+)\s+to\s+(\d+)")
FILE_PATTERN = re.compile(r"^(\d+)\.\s+.+\.py$")
from utils import chunk_items  # Shared utility

# Import skill state and ranking from Doctor for personalized suggestions
from leetcode_doctor import (
    load_skill_state,
    rank_problems,
    score_problem,
    SKILL_CATEGORIES,
    DOCTOR_SKILL_STATE_FILE,
    _detect_topic_with_threshold,
)


def _safe_print(*args, **kwargs):
    """Print without crashing on Windows console encoding issues."""
    try:
        return builtins.print(*args, **kwargs)
    except UnicodeEncodeError:
        stream = kwargs.get("file") or sys.stdout
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        text = sep.join(str(arg) for arg in args)
        safe_text = text.encode(stream.encoding if hasattr(stream, 'encoding') else 'utf-8', errors='replace').decode(stream.encoding if hasattr(stream, 'encoding') else 'utf-8')
        stream.write(safe_text + end)
        if kwargs.get("flush", False) and hasattr(stream, "flush"):
            stream.flush()


# Replace print with safe version
print = _safe_print


# ============================================================
# Fix #1 — Atomic file write (shared with Doctor)
# ============================================================
def atomic_write(file_path: Path, content: str, required_markers: List[str] = None) -> bool:
    """Queue the write in memory and commit it atomically."""
    try:
        CONTROLLER.queue_text_write(
            file_path,
            content,
            required_markers=required_markers or [],
        )
        CONTROLLER.commit(reason=f"suggestor:write:{file_path.name}")
        return True
    except Exception:
        CONTROLLER.io_manager.clear()
        return False


# Configuration
RATINGS_URL = "https://raw.githubusercontent.com/zerotrac/leetcode_problem_rating/main/ratings.txt"
LEETCODE_API_BASE = "https://leetcode-api-pied.vercel.app"
SOLVED_TRACKING_FILE = SOLUTIONS_ROOT.parent / ".qwen" / ".solved_tracking.json"


def _extract_problem_id_from_file(file_path: Path):
    if not file_path.is_file():
        return None
    file_match = FILE_PATTERN.match(file_path.name)
    if not file_match:
        return None
    return int(file_match.group(1))


def _scan_problem_directory(directory: Path):
    if not directory.is_dir():
        return set()

    folder_match = FOLDER_PATTERN.match(directory.name)
    if not folder_match:
        return set()

    children = CONTROLLER.list_directory(directory)
    solved = set()

    for child in children:
        problem_id = _extract_problem_id_from_file(child)
        if problem_id is not None:
            solved.add(problem_id)

    nested_directories = [
        child for child in children if child.is_dir() and FOLDER_PATTERN.match(child.name)
    ]
    for nested_directory in nested_directories:
        nested_children = CONTROLLER.list_directory(nested_directory)
        for nested_child in nested_children:
            problem_id = _extract_problem_id_from_file(nested_child)
            if problem_id is not None:
                solved.add(problem_id)

    return solved


def get_existing_problems():
    """Scan the project and return a set of all solved problem numbers."""
    solved = set()

    project_items = CONTROLLER.list_directory(SOLUTIONS_ROOT)
    folder_results = CONTROLLER.process_batch(
        project_items,
        _scan_problem_directory,
        batch_size=SCAN_BATCH_SIZE,
        pipeline="validation",
        flush_writes=False,
        file_operation=True,
        batch_name="scan-project-folders",
    )
    for folder_solved in folder_results:
        solved.update(folder_solved)

    # Also check tracking file for manually marked solved problems
    tracking = load_tracking()
    if tracking and 'solved' in tracking:
        solved.update(tracking['solved'])

    return solved


def fetch_ratings():
    """Fetch problem ratings from ZeroTrac repository."""
    print("Fetching problem ratings from ZeroTrac...")
    
    try:
        def _download_ratings():
            req = Request(RATINGS_URL)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urlopen(req, timeout=30) as response:
                return response.read().decode('utf-8')

        content = CONTROLLER.run_operation(
            _download_ratings,
            label="network:fetch-ratings",
            file_operation=False,
        )

        def _parse_rating_line(line):
            parts = line.split()
            if len(parts) < 7:
                return None

            try:
                rating = float(parts[0])
                problem_id = int(parts[1])

                return {
                    'rating': rating,
                    'id': problem_id,
                    'raw_line': line
                }
            except (ValueError, IndexError):
                return None

        line_chunks = list(chunk_items(content.strip().split('\n')[1:], RATING_CHUNK_SIZE))

        def _parse_rating_chunk(line_chunk):
            problems = []
            for line in line_chunk:
                parsed_problem = _parse_rating_line(line)
                if parsed_problem is not None:
                    problems.append(parsed_problem)
            return problems

        parsed = CONTROLLER.process_batch(
            line_chunks,
            _parse_rating_chunk,
            batch_size=SCAN_BATCH_SIZE,
            pipeline="validation",
            flush_writes=False,
            file_operation=False,
            batch_name="parse-ratings",
        )
        problems = [problem for batch in parsed for problem in batch]

        print(f"Successfully fetched {len(problems)} problems\n")
        return problems

    except URLError as e:
        print(f"Error fetching ratings: {e}")
        print("Check your internet connection and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


def parse_problem_details(raw_line):
    """Parse a raw line from ratings.txt to extract problem details."""
    parts = raw_line.split()

    if len(parts) < 7:
        return None

    rating = float(parts[0])
    problem_id = int(parts[1])

    # Work backwards from the end
    problem_index = parts[-1]  # e.g., Q4
    contest_slug = parts[-2]   # e.g., weekly-contest-408
    title_slug = parts[-3]     # e.g., check-if-the-rectangle-corner-is-reachable

    # Find where English title ends and Chinese title begins
    english_title_parts = []
    chinese_title_parts = []
    in_chinese = False

    for part in parts[2:-3]:  # Skip rating, ID, and last 3 parts
        # Check if this part contains Chinese characters
        if any('\u4e00' <= char <= '\u9fff' for char in part):
            in_chinese = True

        if in_chinese:
            chinese_title_parts.append(part)
        else:
            english_title_parts.append(part)

    english_title = ' '.join(english_title_parts)
    chinese_title = ' '.join(chinese_title_parts)

    return {
        'rating': rating,
        'id': problem_id,
        'title': english_title,
        'title_zh': chinese_title,
        'title_slug': title_slug,
        'contest_slug': contest_slug,
        'problem_index': problem_index,
        'rating_source': 'ZeroTrac',
    }


def build_problem(raw_line, solved_set):
    """Build an explicit problem feature model from a raw ratings line.

    This makes the problem model explicit and testable, and sets up the
    foundation for multi-feature ranking later.

    Args:
        raw_line: A single line from ZeroTrac ratings.txt
        solved_set: Set of solved problem IDs for membership check

    Returns:
        Dict with explicit problem features, or None if parsing fails.
        Keys: id, rating, difficulty, solved, source
    """
    parsed = parse_problem_details(raw_line)
    if parsed is None:
        return None

    # Derive difficulty from rating (heuristic — can be extended later)
    rating = parsed['rating']
    if rating < 500:
        difficulty = 'easy'
    elif rating < 1000:
        difficulty = 'medium'
    else:
        difficulty = 'hard'

    return {
        'id': parsed['id'],
        'rating': parsed['rating'],
        'difficulty': difficulty,
        'solved': parsed['id'] in solved_set,
        'source': 'zerotrac'
    }


def _enrich_problem_with_topic(problem: dict) -> dict:
    """Add topic detection to a problem dict for skill-based ranking.
    
    Since we don't have the user's code for unsolved problems, we use
    problem title keywords as a proxy for topic detection.
    """
    title = problem.get('title', '').lower()
    title_slug = problem.get('title_slug', '').lower()
    combined = f"{title} {title_slug}"
    
    # Use doctor's topic detection on problem title/slug
    topic = _detect_topic_with_threshold(combined, threshold=0.3)
    
    problem['topic'] = topic
    return problem


def find_unsolved_problems(ratings, solved):
    """Find problems not yet solved in the project, sorted by rating (easiest first)."""
    def _collect_unsolved(problem):
        if problem['id'] not in solved:
            details = parse_problem_details(problem['raw_line'])
            if details:
                return details
        return None

    rating_chunks = list(chunk_items(ratings, RATING_CHUNK_SIZE))

    def _collect_unsolved_chunk(rating_chunk):
        unsolved_chunk = []
        for problem in rating_chunk:
            details = _collect_unsolved(problem)
            if details is not None:
                unsolved_chunk.append(details)
        return unsolved_chunk

    unsolved = CONTROLLER.process_batch(
        rating_chunks,
        _collect_unsolved_chunk,
        batch_size=SCAN_BATCH_SIZE,
        pipeline="validation",
        flush_writes=False,
        file_operation=False,
        batch_name="filter-unsolved",
    )
    unsolved = [problem for batch in unsolved for problem in batch]

    # Sort by rating (ascending = easiest first)
    unsolved.sort(key=lambda x: x['rating'])

    return unsolved


def rank_problems_with_skill_state(unsolved_problems, skill_state=None, top_n=10):
    """Rank unsolved problems using multi-feature skill-based ranking.
    
    Args:
        unsolved_problems: List of problem dicts from find_unsolved_problems
        skill_state: Current skill state (loaded from doctor_skill_state.json)
        top_n: Number of top problems to return
    
    Returns:
        List of (problem, score, score_breakdown) tuples
    """
    if skill_state is None:
        skill_state = load_skill_state()
    
    # Default weights for ranking
    weights = {
        'w1': 0.30,  # Normalized rating (difficulty)
        'w2': 0.35,  # Difficulty fit (sweet spot above current skill)
        'w3': 0.25,  # Topic gap (boost weak areas)
        'w4': 0.10,  # Recency bonus
    }
    
    # Enrich problems with topic detection
    enriched = [_enrich_problem_with_topic(p) for p in unsolved_problems[:100]]  # Limit to top 100 for performance
    
    # Mark all as unsolved for ranking
    for p in enriched:
        p['solved'] = False
    
    # Rank using multi-feature scoring
    ranked = rank_problems(enriched, skill_state, weights)
    
    # Calculate score breakdowns for top N
    result = []
    for problem in ranked[:top_n]:
        score = score_problem(problem, skill_state, weights)
        
        # Calculate breakdown
        rating_norm = min(problem['rating'], 3000) / 3000.0
        topic = problem.get('topic', 'unknown')
        skill_score = skill_state['skills'].get(topic, {}).get('score', 0.0)
        difficulty_fit = 1.0 - abs(rating_norm - (skill_score + 0.2))
        difficulty_fit = max(0.0, difficulty_fit)
        weak_areas = []
        overall = skill_state['overall_accuracy']
        for cat in SKILL_CATEGORIES:
            skill = skill_state['skills'][cat]
            if skill['count'] == 0 or skill['score'] < overall:
                weak_areas.append(cat)
        topic_gap = 1.0 if topic in weak_areas else 0.0
        recency = min(problem['id'], 4000) / 4000.0
        
        breakdown = {
            'w1_rating': round(weights['w1'] * rating_norm, 4),
            'w2_difficulty_fit': round(weights['w2'] * difficulty_fit, 4),
            'w3_topic_gap': round(weights['w3'] * topic_gap, 4),
            'w4_recency': round(weights['w4'] * recency, 4),
            'topic': topic,
            'skill_score': round(skill_score, 4),
            'difficulty_fit_raw': round(difficulty_fit, 4),
            'is_weak_area': topic in weak_areas,
        }
        
        result.append((problem, score, breakdown))
    
    return result


def fetch_leetcode_problem_list(solved: set) -> List[Dict]:
    """
    Fetch the full LeetCode problem list from the GraphQL API.
    Returns a list of dicts with 'id', 'title', 'title_slug', 'difficulty', 'rating'.
    This is the fallback for problems not in ZeroTrac (IDs < 749 or unsolved newer ones).
    """
    graphql_url = "https://leetcode.com/graphql"
    query = """
    query problemsetQuestionList($skip: Int!, $limit: Int!) {
      problemsetQuestionList: questionAll(
        pageInput: { skip: $skip, limit: $limit }
      ) {
        total
        questions {
          questionId
          questionFrontendId
          title
          titleSlug
          difficulty
          acRate
        }
      }
    }
    """

    all_problems = []
    skip = 0
    limit = 100

    print("Fetching problem list from LeetCode (for problems not in ZeroTrac)...")
    print("This may take a moment as we paginate through all problems...")

    while True:
        payload = json.dumps({
            "query": query,
            "variables": {"skip": skip, "limit": limit}
        }).encode('utf-8')

        try:
            def _download_chunk():
                req = Request(graphql_url, data=payload)
                req.add_header('User-Agent', 'Mozilla/5.0')
                req.add_header('Content-Type', 'application/json')
                with urlopen(req, timeout=30) as response:
                    return json.loads(response.read().decode('utf-8'))

            data = CONTROLLER.run_operation(
                _download_chunk,
                label=f"network:leetcode-list:skip-{skip}",
                file_operation=False,
            )

            question_list = data.get('data', {}).get('problemsetQuestionList', {})
            questions = question_list.get('questions', [])
            total = question_list.get('total', 0)

            if not questions:
                break

            for q in questions:
                try:
                    problem_id = int(q['questionFrontendId'])
                except (ValueError, TypeError, KeyError):
                    continue

                if problem_id in solved:
                    continue

                # Map difficulty to a numeric rating for sorting
                difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
                difficulty = q.get('difficulty', 'Unknown')
                rating = difficulty_map.get(difficulty, 2) * 1000 + (problem_id * 0.1)

                all_problems.append({
                    'id': problem_id,
                    'title': q.get('title', ''),
                    'title_slug': q.get('titleSlug', ''),
                    'difficulty': difficulty,
                    'rating': round(rating, 2),
                    'title_zh': '',
                    'contest_slug': '',
                    'problem_index': '',
                    'rating_source': 'LeetCode API',
                })

            skip += limit
            if skip >= total:
                break

            # Progress indicator
            if skip % 500 == 0:
                print(f"  ... fetched {skip}/{total} problems")

        except Exception as e:
            print(f"Error fetching Leetcode problem list at skip={skip}: {e}")
            break

    # Sort by rating (easiest first)
    all_problems.sort(key=lambda x: x['rating'])
    print(f"Found {len(all_problems)} unsolved problems from LeetCode API\n")
    return all_problems


def fetch_problem_statement(title_slug):
    """Fetch the full problem statement from LeetCode API."""
    api_url = f"{LEETCODE_API_BASE}/problem/{title_slug}"
    
    try:
        def _download_problem_statement():
            req = Request(api_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))

        data = CONTROLLER.run_operation(
            _download_problem_statement,
            label=f"network:problem-statement:{title_slug}",
            file_operation=False,
        )
        
        if 'content' in data:
            return {
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'difficulty': data.get('difficulty', 'Unknown'),
                'likes': data.get('likes', 0),
                'dislikes': data.get('dislikes', 0),
                'topics': data.get('topicTags', [])
            }
        else:
            return None
            
    except Exception as e:
        print(f"Could not fetch problem statement: {e}")
        return None


def clean_html_content(html_content):
    """Convert HTML problem statement to clean text format."""
    import html as html_module
    
    text = html_content
    
    # Replace common HTML elements with clean formatting
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n\n', text)
    text = re.sub(r'<p>', '', text)
    text = re.sub(r'</?(strong|b)>', '**', text)
    text = re.sub(r'</?(em|i)>', '*', text)
    text = re.sub(r'<li>', '\n• ', text)
    text = re.sub(r'</?ul>', '', text)
    text = re.sub(r'</?ol>', '', text)
    text = re.sub(r'<pre[^>]*>', '\n```\n', text)
    text = re.sub(r'</pre>', '\n```\n', text)
    text = re.sub(r'<code>', '`', text)
    text = re.sub(r'</code>', '`', text)
    
    # Remove all other HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = html_module.unescape(text)
    
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def get_folder_for_problem(problem_id):
    """Determine which folder a problem should go in."""
    # Calculate the range (e.g., 1-100, 101-200, etc.)
    range_start = ((problem_id - 1) // 100) * 100 + 1
    range_end = range_start + 99

    folder_name = f"{range_start:03d} to {range_end}"
    return SOLUTIONS_ROOT / folder_name


def create_solution_file(problem):
    """Create a solution file for the suggested problem with full problem statement."""
    problem_id = problem['id']
    title = problem['title']
    title_slug = problem['title_slug']

    print(f"\n{'=' * 60}")
    print(f"AUTO-CREATING SOLUTION FILE")
    print(f"{'=' * 60}")
    print(f"Problem: {problem_id}. {title}")
    print(f"Rating: {problem['rating']:.2f}")
    print(f"{'=' * 60}")

    # Fetch problem statement
    print(f"\nFetching problem statement...")
    problem_stmt = fetch_problem_statement(title_slug)

    folder = get_folder_for_problem(problem_id)

    # Create folder if it doesn't exist
    folder_exists = CONTROLLER.run_operation(
        lambda: folder.exists(),
        label=f"exists:{folder.name}",
        file_operation=True,
    )
    if not folder_exists:
        CONTROLLER.ensure_directory(folder)
        print(f"Created new folder: {folder.name}")

    # Create filename - match existing convention: "NUMBER. Title.py"
    filename = f"{problem_id}. {title}.py"
    filepath = folder / filename

    file_exists = CONTROLLER.run_operation(
        lambda: filepath.exists(),
        label=f"exists:{filepath.name}",
        file_operation=True,
    )
    if file_exists:
        print(f"File already exists: {filename}")
        print(f"  Location: {filepath}")
        print(f"\nThis problem appears to be already in your project.")
        print(f"Run the script again to get the next suggestion.")
        return True

    # Build the problem statement section
    if problem_stmt:
        clean_content = clean_html_content(problem_stmt['content'])

        # Format topics
        topics_str = ", ".join([tag['name'] for tag in problem_stmt['topics']]) if problem_stmt['topics'] else "None"

        statement_section = f"""
PROBLEM STATEMENT:
{'=' * 60}
{clean_content}

DIFFICULTY: {problem_stmt['difficulty']}
LIKES: {problem_stmt['likes']} | DISLIKES: {problem_stmt['dislikes']}
TOPICS: {topics_str}
"""
    else:
        statement_section = f"""
PROBLEM STATEMENT:
{'=' * 60}

Problem link: https://leetcode.com/problems/{title_slug}/

[Unable to auto-fetch problem statement.]
[Please visit the link above and add the problem description manually.]
[The suggestor will attempt to fetch it again on next run.]
"""

    # Create solution file with problem statement
    leetcode_url = f"https://leetcode.com/problems/{title_slug}/"

    # Handle both ZeroTrac problems and LeetCode API fallback problems
    contest_info = problem.get('contest_slug', '')
    problem_index = problem.get('problem_index', '')
    title_zh = problem.get('title_zh', '')
    rating_source = problem.get('rating_source', 'ZeroTrac')

    contest_line = f"Contest: {contest_info}" if contest_info else "Contest: N/A"
    index_line = f"Problem Index: {problem_index}" if problem_index else "Problem Index: N/A"
    zh_line = f"Chinese Title: {title_zh}" if title_zh else "Chinese Title: N/A"

    content = f'''"""
LeetCode {problem_id}. {title}
{'=' * 60}

Problem Number: {problem_id}
Difficulty Rating: {problem['rating']:.2f} ({rating_source})
{contest_line}
{index_line}

LeetCode URL: {leetcode_url}

Problem Slug: {title_slug}
{zh_line}
{statement_section}

{'=' * 60}
TODO WORKFLOW - Complete in Order (1 → 2 → 3 → 4):
{'=' * 60}
TODO #1 - PROBLEM STATEMENT      [Review auto-generated content above]
TODO #2 - APPROACH                [Describe your algorithm step-by-step]
TODO #3 - COMPLEXITY              [State Time/Space complexity with reasoning]
TODO #4 - SOLUTION + TESTS        [Implement solution + comprehensive test cases]
{'=' * 60}

Progress: Run this file directly to call the Doctor for this TODO workflow
          Alternative: `python leetcode_doctor.py {problem_id}`
          Must pass in order: #1 -> #2 -> #3 -> #4
          Each requires >=8/10 to pass (except #4 needs 100% test pass)

{'=' * 60}
TODO #2 - APPROACH:
TODO: Replace this line with your algorithm description.
      Explain step-by-step how you will solve this problem.
      Example: "I will use a hash map to store..." or "This is a sliding window problem where..."

{'=' * 60}
TODO #3 - COMPLEXITY:
Time Complexity: O(?)  — replace with actual complexity (e.g., O(n log n))
Space Complexity: O(?) — replace with actual complexity (e.g., O(n) for hash map)
"""

from typing import List, Optional
import heapq
from collections import defaultdict, deque


class Solution:
    @staticmethod
    def solve() -> None:
        """
        TODO #4a — Implement the solution for {title}

        Args:
            TODO: Add parameters based on the problem statement

        Returns:
            TODO: Add return type based on the problem statement
        """
        # TODO: Implement your solution here
        pass


# ============================================================
# TODO #4b — Test Cases (add from LeetCode examples + edge cases)
# ============================================================
def _run_embedded_tests() -> None:
    solution = Solution()

    # Example 1:
    # Input: TODO
    # Expected: TODO

    # Example 2:
    # Input: TODO
    # Expected: TODO

    # Edge case:
    # Input: TODO
    # Expected: TODO

    result = solution.solve()
    print(f"Result: {{result}}")


if __name__ == '__main__':
    from pathlib import Path
    import sys

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    from doctor_runtime import run_doctor_or_embedded_tests

    raise SystemExit(run_doctor_or_embedded_tests(__file__, _run_embedded_tests))
'''
    
    # Write atomically — temp file, validate, then rename
    required_markers = ['TODO WORKFLOW', 'TODO #1', 'TODO #2', 'TODO #3', 'TODO #4']
    success = atomic_write(filepath, content, required_markers=required_markers)

    if not success:
        print(f"\nFile write failed validation — file not created.")
        return False

    print(f"Created solution file: {filename}")
    print(f"  Location: {filepath}")
    print(f"\n{'=' * 60}")
    print(f"File created successfully!")
    print(f"{'=' * 60}")
    print(f"\nNext steps:")
    print(f"  1. Open the file in your editor")
    print(f"  2. Review the problem statement in the docstring")
    print(f"  3. Implement your solution in the solve() method")
    print(f"  4. Add test cases at the bottom")
    print(f"  5. When done, run this script again for the next suggestion")

    return True


def load_tracking():
    """Load tracking file for solved problems."""
    tracking = CONTROLLER.read_json(
        SOLVED_TRACKING_FILE,
        default=None,
        encoding='utf-8',
    )
    if not isinstance(tracking, dict):
        return {'solved': []}
    solved = tracking.get('solved')
    if not isinstance(solved, list):
        tracking['solved'] = []
    return tracking


def save_tracking(tracking):
    """Save tracking file for solved problems."""
    CONTROLLER.ensure_directory(SOLVED_TRACKING_FILE.parent)
    CONTROLLER.queue_json_write(
        SOLVED_TRACKING_FILE,
        tracking,
        indent=2,
        ensure_ascii=False,
    )
    CONTROLLER.commit(reason="suggestor:save-tracking")


def suggest_problem(mode='auto'):
    """Main function to suggest and auto-create unsolved LeetCode problems."""
    # Get existing solved problems
    print("Scanning project for solved problems...")
    solved = get_existing_problems()
    print(f"Found {len(solved)} solved problems\n")

    # Load skill state for personalized ranking
    skill_state = load_skill_state()
    if skill_state["total_problems"] > 0:
        print(f"📊 Skill State Loaded: {skill_state['total_problems']} problems completed")
        print(f"   Overall Accuracy: {skill_state['overall_accuracy']:.2%}")
        weak = []
        for cat in SKILL_CATEGORIES:
            skill = skill_state['skills'][cat]
            if skill['count'] == 0 or skill['score'] < skill_state['overall_accuracy']:
                weak.append(cat)
        if weak:
            print(f"   Weak Areas: {', '.join(weak)}")
        print()
    else:
        print("🆕 No skill history yet - using rating-based ranking\n")

    # Fetch ratings from ZeroTrac
    ratings = fetch_ratings()

    # Find unsolved problems from ZeroTrac
    print("Finding unsolved problems...")
    unsolved = find_unsolved_problems(ratings, solved)

    # If ZeroTrac has no more unsolved problems, fall back to LeetCode API
    if not unsolved:
        print("\nAll ZeroTrac-rated problems are solved (or unavailable).")
        print("Falling back to LeetCode GraphQL API for problem suggestions...\n")
        unsolved = fetch_leetcode_problem_list(solved)

    if not unsolved:
        print("\nCongratulations! You've solved all available problems!")
        return

    # Use skill-based ranking if we have skill state
    if skill_state["total_problems"] > 0:
        print("🎯 Ranking problems using multi-feature skill-based scoring...")
        ranked_problems = rank_problems_with_skill_state(unsolved, skill_state, top_n=10)
        
        # Display based on mode
        if mode == 'all':
            print("\n" + "=" * 100)
            print("TOP 10 RECOMMENDED PROBLEMS (Skill-Based Ranking)")
            print("=" * 100)
            print(f"{'Rank':<5} {'ID':<6} {'Score':<8} {'Rating':<10} {'Title':<35} {'Topic':<12} {'Weak':<5}")
            print("-" * 100)

            for i, (problem, score, breakdown) in enumerate(ranked_problems, 1):
                source = problem.get('rating_source', 'Unknown')
                title = problem.get('title', 'Unknown')[:33]
                topic = breakdown['topic']
                is_weak = "✓" if breakdown['is_weak_area'] else ""
                print(f"{i:<5} {problem['id']:<6} {score:<8.4f} {problem['rating']:<10.2f} {title:<35} {topic:<12} {is_weak:<5}")

            print("=" * 100)
            print(f"\nTotal unsolved problems: {len(unsolved)}")
            print(f"\nScoring breakdown for #1 recommendation:")
            top_problem, top_score, top_breakdown = ranked_problems[0]
            print(f"  Total Score: {top_score:.4f}")
            print(f"  w1 Rating (30%): {top_breakdown['w1_rating']:.4f}")
            print(f"  w2 Difficulty Fit (35%): {top_breakdown['w2_difficulty_fit']:.4f}")
            print(f"  w3 Topic Gap (25%): {top_breakdown['w3_topic_gap']:.4f} {'← Boosted: weak area' if top_breakdown['is_weak_area'] else ''}")
            print(f"  w4 Recency (10%): {top_breakdown['w4_recency']:.4f}")
            print(f"\nTo auto-create the top recommendation, run: leetcode_suggestor.py")

        else:  # auto mode - create the file automatically
            # Create the file for the top-ranked problem
            top_problem, top_score, top_breakdown = ranked_problems[0]
            
            print(f"\n🎯 TOP RECOMMENDATION (Score: {top_score:.4f})")
            print(f"   Problem: {top_problem['id']}. {top_problem['title']}")
            print(f"   Rating: {top_problem['rating']:.2f}")
            print(f"   Detected Topic: {top_breakdown['topic']}")
            print(f"   Your Skill ({top_breakdown['topic']}): {top_breakdown['skill_score']:.4f}")
            print(f"   Difficulty Fit: {top_breakdown['difficulty_fit_raw']:.4f}")
            print(f"   Weak Area Boost: {'Yes ✓' if top_breakdown['is_weak_area'] else 'No'}")
            print()
            
            create_solution_file(top_problem)
    else:
        # No skill state yet - use simple rating-based ranking
        print("📊 Using ZeroTrac rating-based ranking (complete a problem to enable skill-based ranking)")
        
        # Display based on mode
        if mode == 'all':
            print("\n" + "=" * 60)
            print("TOP 10 EASIEST UNSOLVED PROBLEMS (Rating-Based)")
            print("=" * 60)
            print(f"{'Rank':<5} {'ID':<6} {'Rating':<10} {'Title':<50} {'Source'}")
            print("-" * 60)

            for i, problem in enumerate(unsolved[:DISPLAY_BATCH_SIZE], 1):
                source = problem.get('rating_source', 'Unknown')
                title = problem.get('title', 'Unknown')[:48]
                print(f"{i:<5} {problem['id']:<6} {problem['rating']:<10.2f} {title:<50} {source}")

            print("=" * 60)
            print(f"\nTotal unsolved problems: {len(unsolved)}")
            print(f"\nTo auto-create the easiest problem, run: leetcode_suggestor.py")

        else:  # auto mode - create the file automatically
            # Create the file for the easiest unsolved problem
            create_solution_file(unsolved[0])


def main():
    """Entry point with argument parsing."""
    mode = 'auto'
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == '--all':
            mode = 'all'
        elif arg == '--help' or arg == '-h':
            print(__doc__)
            sys.exit(0)
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information")
            sys.exit(1)
    
    try:
        CONTROLLER.run_entrypoint(
            "leetcode_suggestor",
            lambda: suggest_problem(mode),
        )
    except ExecutionControlError as exc:
        print(f"\nControlled execution stopped: {exc}")
        sys.exit(1)


if __name__ == '__main__':
    main()
