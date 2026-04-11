def solve_euler_836():
    # The bolded phrases from the problem description
    bolded_phrases = [
        "affine plane",
        "radically integral local field",
        "open oriented line section",
        "jacobian",
        "orthogonal kernel embedding"
    ]

    # Extract the first letter of each word in the phrases
    answer = ""
    for phrase in bolded_phrases:
        words = phrase.split()
        for word in words:
            answer += word[0]

    return answer

if __name__ == "__main__":
    result = solve_euler_836()
    print(f"Solution: {result}")
