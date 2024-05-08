import re

# Define a regex pattern for HH:MM format
pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'

time_str = "32:34"

# Check if the time string matches the pattern
print(re.match(pattern, time_str) is not None)