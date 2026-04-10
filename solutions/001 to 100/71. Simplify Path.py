class Solution:
    @staticmethod
    def simplifyPath(path: str) -> str:
        # Split the path by '/' to handle individual components
        components = path.split('/')

        # Initialize a stack to simulate directory traversal
        stack = []

        # Process each component of the path
        for component in components:
            # Ignore empty and '.' components
            if component == '' or component == '.':
                continue
            # Handle '..' component
            elif component == '..':
                # If the stack is not empty, pop the top element
                if stack:
                    stack.pop()
            # Otherwise, push the component onto the stack
            else:
                stack.append(component)

        # Reconstruct the simplified path using the elements in the stack
        simplified_path = '/' + '/'.join(stack)

        return simplified_path


if __name__ == '__main__':
    print(Solution.simplifyPath(path="/home/user/../../usr/local/bin"))
