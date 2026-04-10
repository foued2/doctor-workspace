class Solution:
    @staticmethod
    def interpret(command: str) -> str:
        # Replace occurrences of "()" with "o"
        command = command.replace("()", "o")
        # Replace occurrences of "(al)" with "al"
        command = command.replace("(al)", "al")
        # Return the interpreted command
        return command


print(Solution.interpret(command="G()()()()(al)"))
