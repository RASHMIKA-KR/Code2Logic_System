def print_half_diamond(n):
    # Print the upper half of the diamond
    for i in range(1, n + 1):
        print('*' * i)

    # Print the lower half of the diamond
    for i in range(n - 1, 0, -1):
        print('*' * i)

# Example usage
n = 5
print_half_diamond(n)