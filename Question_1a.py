import time

# Ask user for input
n = int(input("Enter a positive integer: "))

# Start timer
start_time = time.time()

# Initialize sum
sum_n = 0

# Calculate sum using for loop
for i in range(1, n + 1):
    sum_n += i

# End timer
end_time = time.time()

# Display the sum
print("The sum of first", n, "natural numbers is:", sum_n)

# Display time taken
print("Time taken to execute:", end_time - start_time, "seconds")
