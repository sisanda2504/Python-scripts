def calculate_average(numbers):
    total = sum(numbers)
    average = total / len(numbers)
    return average


scores = [75, 80, 90, 65, 88]

result = calculate_average(scores)

print("Average:", result)